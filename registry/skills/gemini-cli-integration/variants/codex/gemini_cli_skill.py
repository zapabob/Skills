#!/usr/bin/env python3
"""
GeminiCLI Integration Skill
MCP/A2A/Skills経由でのGeminiCLI統合
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import websockets
import aiohttp

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    # 内部モジュール（必要に応じて）
    pass
except ImportError:
    pass


@dataclass
class GeminiCLIConfig:
    """GeminiCLI設定"""
    cli_path: str = ""
    api_token: str = ""
    mcp_host: str = "localhost"
    mcp_port: int = 8081
    a2a_enabled: bool = True
    streaming_enabled: bool = True
    markdown_enabled: bool = True
    context_window: int = 32768
    timeout: int = 30
    max_retries: int = 3


@dataclass
class MCPMessage:
    """MCPメッセージ"""
    message_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str
    source: str = "gemini_cli_skill"


@dataclass
class GeminiTask:
    """Geminiタスク"""
    task_id: str
    description: str
    context: Dict[str, Any]
    priority: str = "normal"
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class GeminiCLISkill:
    """
    GeminiCLI統合スキル
    MCP/A2A/Skills経由でのGeminiCLI操作
    """

    def __init__(self, config: Optional[GeminiCLIConfig] = None):
        self.config = config or GeminiCLIConfig()
        self.logger = logging.getLogger("GeminiCLISkill")

        # コンポーネント初期化
        self.cli_detector = GeminiCLIDetector()
        self.mcp_server = MCPServer(self.config, self)
        self.a2a_bridge = A2ABridge(self)
        self.task_processor = GeminiTaskProcessor(self.config, self)
        self.streaming_processor = GeminiStreamingProcessor()
        self.context_manager = GeminiContextManager()

        # 状態管理
        self.is_initialized = False
        self.active_tasks = {}
        self.connected_clients = set()

        # パフォーマンス監視
        self.performance_monitor = GeminiPerformanceMonitor()

    async def initialize(self) -> bool:
        """初期化"""
        try:
            self.logger.info("GeminiCLI Skill初期化開始")

            # GeminiCLIパス検出
            self.config.cli_path = await self.cli_detector.find_gemini_cli()
            if not self.config.cli_path:
                raise RuntimeError("GeminiCLIが見つかりません")

            self.logger.info(f"GeminiCLIパス: {self.config.cli_path}")

            # 設定検証
            await self._validate_configuration()

            # MCPサーバー起動
            await self.mcp_server.start()

            # A2Aブリッジ初期化
            if self.config.a2a_enabled:
                await self.a2a_bridge.initialize()

            # タスクプロセッサ初期化
            await self.task_processor.initialize()

            self.is_initialized = True
            self.logger.info("GeminiCLI Skill初期化完了")

            return True

        except Exception as e:
            self.logger.error(f"GeminiCLI Skill初期化失敗: {e}")
            return False

    async def shutdown(self):
        """シャットダウン"""
        self.logger.info("GeminiCLI Skillシャットダウン開始")

        # アクティブタスクキャンセル
        await self._cancel_active_tasks()

        # MCPサーバー停止
        await self.mcp_server.stop()

        # A2Aブリッジ停止
        if self.config.a2a_enabled:
            await self.a2a_bridge.shutdown()

        # タスクプロセッサ停止
        await self.task_processor.shutdown()

        self.is_initialized = False
        self.logger.info("GeminiCLI Skillシャットダウン完了")

    async def execute_research_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        研究タスク実行

        Args:
            task_description: タスク説明
            context: 実行コンテキスト

        Returns:
            実行結果
        """
        if not self.is_initialized:
            return {"success": False, "error": "Skill not initialized"}

        context = context or {}
        task_id = f"task_{int(time.time())}_{hash(task_description) % 10000}"

        try:
            self.logger.info(f"研究タスク実行開始: {task_id}")

            # タスク作成
            task = GeminiTask(
                task_id=task_id,
                description=task_description,
                context=context
            )

            # アクティブタスク登録
            self.active_tasks[task_id] = task

            # タスク実行
            start_time = time.time()
            result = await self.task_processor.execute_task(task)
            execution_time = time.time() - start_time

            # パフォーマンス記録
            await self.performance_monitor.record_execution({
                "task_id": task_id,
                "execution_time": execution_time,
                "success": result.get("success", False),
                "streaming_used": context.get("streaming", False)
            })

            # 結果強化
            enhanced_result = await self._enhance_result(result, task, execution_time)

            # アクティブタスク削除
            self.active_tasks.pop(task_id, None)

            self.logger.info(f"研究タスク実行完了: {task_id}")
            return enhanced_result

        except Exception as e:
            self.logger.error(f"研究タスク実行エラー: {task_id} - {e}")

            # エラータスク削除
            self.active_tasks.pop(task_id, None)

            return {
                "success": False,
                "error": str(e),
                "task_id": task_id,
                "execution_time": time.time() - time.time()  # 0
            }

    async def stream_research_response(self, task_description: str, context: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
        """
        ストリーミング研究応答

        Args:
            task_description: タスク説明
            context: 実行コンテキスト

        Yields:
            応答チャンク
        """
        if not self.is_initialized:
            yield "Error: Skill not initialized"
            return

        context = context or {}
        context["streaming"] = True

        try:
            # ストリーミング実行
            async for chunk in self.task_processor.stream_execute_task(task_description, context):
                yield chunk

        except Exception as e:
            self.logger.error(f"ストリーミング実行エラー: {e}")
            yield f"Error: {str(e)}"

    async def register_with_a2a_network(self) -> bool:
        """A2Aネットワークに登録"""
        if not self.config.a2a_enabled:
            return False

        try:
            capabilities = [
                "research_execution",
                "streaming_responses",
                "markdown_formatting",
                "context_management",
                "gemini_ai_integration"
            ]

            await self.a2a_bridge.register_agent("gemini_cli_skill", capabilities)
            self.logger.info("A2Aネットワークに登録完了")
            return True

        except Exception as e:
            self.logger.error(f"A2A登録エラー: {e}")
            return False

    async def process_mcp_message(self, message: str) -> str:
        """MCPメッセージ処理"""
        try:
            # MCPメッセージ解析
            mcp_data = json.loads(message)
            mcp_message = MCPMessage(**mcp_data)

            self.logger.debug(f"MCPメッセージ受信: {mcp_message.message_type}")

            # メッセージタイプに応じた処理
            if mcp_message.message_type == "research_query":
                result = await self.execute_research_task(
                    mcp_message.content["task"],
                    mcp_message.content.get("context", {})
                )
            elif mcp_message.message_type == "streaming_query":
                # ストリーミングの場合は特別処理
                result = {"streaming": True, "task": mcp_message.content["task"]}
            elif mcp_message.message_type == "capability_query":
                result = await self._get_capabilities()
            else:
                result = {"success": False, "error": f"Unknown message type: {mcp_message.message_type}"}

            # MCP応答フォーマット
            response = {
                "message_id": mcp_message.message_id,
                "timestamp": datetime.now().isoformat(),
                "source": "gemini_cli_skill",
                "result": result
            }

            return json.dumps(response)

        except Exception as e:
            self.logger.error(f"MCPメッセージ処理エラー: {e}")
            return json.dumps({
                "message_id": "error",
                "timestamp": datetime.now().isoformat(),
                "source": "gemini_cli_skill",
                "error": str(e)
            })

    async def _validate_configuration(self):
        """設定検証"""
        if not os.path.exists(self.config.cli_path):
            raise FileNotFoundError(f"GeminiCLI not found: {self.config.cli_path}")

        # GeminiCLI実行テスト
        try:
            result = await asyncio.create_subprocess_exec(
                self.config.cli_path, "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode != 0:
                raise RuntimeError("GeminiCLI execution test failed")

        except Exception as e:
            raise RuntimeError(f"GeminiCLI validation failed: {e}")

    async def _cancel_active_tasks(self):
        """アクティブタスクキャンセル"""
        for task_id, task in self.active_tasks.items():
            self.logger.info(f"タスクキャンセル: {task_id}")

        self.active_tasks.clear()

    async def _enhance_result(self, result: Dict[str, Any], task: GeminiTask, execution_time: float) -> Dict[str, Any]:
        """結果強化"""
        enhanced = result.copy()

        # メタデータ追加
        enhanced["task_id"] = task.task_id
        enhanced["execution_time"] = execution_time
        enhanced["model"] = "gemini-cli"
        enhanced["skill_version"] = "1.0.0"

        # 品質スコア計算
        enhanced["quality_score"] = self._calculate_quality_score(result, task)

        # 推奨アクション
        enhanced["suggestions"] = await self._generate_suggestions(result, task)

        return enhanced

    def _calculate_quality_score(self, result: Dict[str, Any], task: GeminiTask) -> float:
        """品質スコア計算"""
        if not result.get("success", False):
            return 0.0

        score = 0.5  # ベーススコア

        # 応答長による品質評価
        content = result.get("content", "")
        if len(content) > 100:
            score += 0.2
        elif len(content) > 500:
            score += 0.3

        # マークダウン使用
        if self.config.markdown_enabled and "##" in content:
            score += 0.1

        # ストリーミング使用
        if task.context.get("streaming", False):
            score += 0.1

        return min(score, 1.0)

    async def _generate_suggestions(self, result: Dict[str, Any], task: GeminiTask) -> List[str]:
        """推奨アクション生成"""
        suggestions = []

        if result.get("success", False):
            if len(result.get("content", "")) < 200:
                suggestions.append("より詳細な調査を検討してください")
            else:
                suggestions.append("結果を保存または共有することを検討してください")

            if task.context.get("streaming", False):
                suggestions.append("ストリーミングモードが効果的でした")
            else:
                suggestions.append("次回はストリーミングモードを試してみてください")

        return suggestions

    async def _get_capabilities(self) -> Dict[str, Any]:
        """機能取得"""
        return {
            "capabilities": [
                "research_execution",
                "streaming_responses",
                "markdown_formatting",
                "context_management",
                "multilingual_support"
            ],
            "supported_formats": ["text", "markdown"],
            "max_context_length": self.config.context_window,
            "streaming_supported": self.config.streaming_enabled
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンスメトリクス取得"""
        return self.performance_monitor.generate_report()


class GeminiCLIDetector:
    """GeminiCLI自動検出"""

    def __init__(self):
        self.common_paths = [
            r"C:\Users\downl\AppData\Local\Programs\Python\Python312\Scripts\gemini-cli.exe",
            r"C:\Program Files\GeminiCLI\gemini-cli.exe",
            r"C:\Users\downl\AppData\Roaming\npm\gemini-cli.cmd",
            "/usr/local/bin/gemini-cli",
            "/usr/bin/gemini-cli"
        ]

    async def find_gemini_cli(self) -> Optional[str]:
        """GeminiCLI実行ファイル検索"""
        # 一般的なパスをチェック
        for path in self.common_paths:
            if os.path.exists(path):
                return path

        # PATH環境変数から検索
        gemini_cli = shutil.which("gemini-cli")
        if gemini_cli:
            return gemini_cli

        # Python環境からの検索
        try:
            result = await asyncio.create_subprocess_exec(
                sys.executable, "-c", "import gemini_cli; print(gemini_cli.__file__)",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()

            if result.returncode == 0:
                module_path = stdout.decode().strip()
                cli_path = os.path.join(os.path.dirname(module_path), "gemini-cli")
                if os.path.exists(cli_path):
                    return cli_path

        except Exception:
            pass

        return None


class MCPServer:
    """MCPサーバー"""

    def __init__(self, config: GeminiCLIConfig, skill: GeminiCLISkill):
        self.config = config
        self.skill = skill
        self.logger = logging.getLogger("MCPServer")
        self.server = None
        self.is_running = False

    async def start(self):
        """MCPサーバー起動"""
        try:
            self.logger.info(f"MCPサーバー起動: {self.config.mcp_host}:{self.config.mcp_port}")

            self.server = await websockets.serve(
                self.handle_connection,
                self.config.mcp_host,
                self.config.mcp_port
            )

            self.is_running = True
            self.logger.info("MCPサーバー起動完了")

        except Exception as e:
            self.logger.error(f"MCPサーバー起動失敗: {e}")
            raise

    async def stop(self):
        """MCPサーバー停止"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            self.logger.info("MCPサーバー停止完了")

    async def handle_connection(self, websocket, path):
        """WebSocket接続処理"""
        try:
            self.logger.debug(f"MCPクライアント接続: {websocket.remote_address}")

            async for message in websocket:
                try:
                    response = await self.skill.process_mcp_message(message)
                    await websocket.send(response)

                except Exception as e:
                    self.logger.error(f"メッセージ処理エラー: {e}")
                    error_response = json.dumps({
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                    await websocket.send(error_response)

        except websockets.exceptions.ConnectionClosed:
            self.logger.debug("MCPクライアント切断")
        except Exception as e:
            self.logger.error(f"MCP接続エラー: {e}")


class A2ABridge:
    """A2A通信ブリッジ"""

    def __init__(self, skill: GeminiCLISkill):
        self.skill = skill
        self.logger = logging.getLogger("A2ABridge")
        self.registered_agents = {}
        self.message_handlers = {}

    async def initialize(self):
        """初期化"""
        self.logger.info("A2Aブリッジ初期化")

    async def shutdown(self):
        """シャットダウン"""
        self.logger.info("A2Aブリッジシャットダウン")

    async def register_agent(self, agent_id: str, capabilities: List[str]):
        """エージェント登録"""
        self.registered_agents[agent_id] = {
            "capabilities": capabilities,
            "registered_at": datetime.now()
        }
        self.logger.info(f"A2Aエージェント登録: {agent_id}")

    async def send_message(self, target_agent: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """メッセージ送信"""
        # 簡易実装：実際にはネットワーク経由で送信
        self.logger.debug(f"A2Aメッセージ送信: {target_agent}")

        # ターゲットエージェントが見つからない場合はローカル処理
        if target_agent not in self.registered_agents:
            return {"success": False, "error": f"Agent not found: {target_agent}"}

        # メッセージ処理（実際の実装ではネットワーク経由）
        return {"success": True, "processed": True}


class GeminiTaskProcessor:
    """Geminiタスクプロセッサ"""

    def __init__(self, config: GeminiCLIConfig, skill: GeminiCLISkill):
        self.config = config
        self.skill = skill
        self.logger = logging.getLogger("GeminiTaskProcessor")

    async def initialize(self):
        """初期化"""
        self.logger.info("Geminiタスクプロセッサ初期化")

    async def shutdown(self):
        """シャットダウン"""
        self.logger.info("Geminiタスクプロセッサシャットダウン")

    async def execute_task(self, task: GeminiTask) -> Dict[str, Any]:
        """タスク実行"""
        try:
            # GeminiCLIコマンド構築
            cmd_args = await self._build_cli_command(task)

            # プロセス実行
            process = await asyncio.create_subprocess_exec(
                self.config.cli_path, *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._build_environment()
            )

            # タイムアウト付き実行
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return {"success": False, "error": "Execution timeout"}

            # 結果処理
            if process.returncode == 0:
                content = stdout.decode('utf-8', errors='replace')
                return {
                    "success": True,
                    "content": content,
                    "raw_output": content,
                    "execution_method": "standard"
                }
            else:
                error_msg = stderr.decode('utf-8', errors='replace')
                return {
                    "success": False,
                    "error": error_msg,
                    "return_code": process.returncode
                }

        except Exception as e:
            self.logger.error(f"タスク実行エラー: {e}")
            return {"success": False, "error": str(e)}

    async def stream_execute_task(self, task_description: str, context: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """ストリーミングタスク実行"""
        try:
            cmd_args = await self._build_cli_command_streaming(task_description, context)

            process = await asyncio.create_subprocess_exec(
                self.config.cli_path, *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._build_environment()
            )

            # ストリーミング読み取り
            while True:
                chunk = await process.stdout.read(1024)
                if not chunk:
                    break

                text_chunk = chunk.decode('utf-8', errors='replace')
                yield text_chunk

                # 処理負荷軽減のための小さな遅延
                await asyncio.sleep(0.01)

            # プロセス完了待機
            return_code = await process.wait()
            if return_code != 0:
                stderr = await process.stderr.read()
                error_msg = stderr.decode('utf-8', errors='replace')
                yield f"\n[Error: {error_msg}]"

        except Exception as e:
            self.logger.error(f"ストリーミング実行エラー: {e}")
            yield f"\n[Error: {str(e)}]"

    async def _build_cli_command(self, task: GeminiTask) -> List[str]:
        """CLIコマンド構築"""
        args = []

        # ストリーミングオプション
        if task.context.get("streaming", False) and self.config.streaming_enabled:
            args.append("--stream")

        # マークダウンオプション
        if task.context.get("markdown", True) and self.config.markdown_enabled:
            args.append("--markdown")

        # コンテキスト設定
        if "context_file" in task.context:
            args.extend(["-c", task.context["context_file"]])

        # 制限設定
        if "limit" in task.context:
            args.extend(["-n", str(task.context["limit"])])

        # プロンプト
        args.append(task.description)

        return args

    async def _build_cli_command_streaming(self, task_description: str, context: Dict[str, Any]) -> List[str]:
        """ストリーミング用CLIコマンド構築"""
        args = ["--stream", "--markdown"]

        # コンテキスト設定
        if "context_file" in context:
            args.extend(["-c", context["context_file"]])

        # プロンプト
        args.append(task_description)

        return args

    def _build_environment(self) -> Dict[str, str]:
        """環境変数構築"""
        env = os.environ.copy()

        # APIトークン設定
        if self.config.api_token:
            env["GEMINI_API_TOKEN"] = self.config.api_token

        return env


class GeminiStreamingProcessor:
    """Geminiストリーミングプロセッサ"""

    def __init__(self):
        self.logger = logging.getLogger("GeminiStreamingProcessor")

    async def process_chunk(self, chunk: str) -> str:
        """チャンク処理"""
        # マークダウン処理などの後処理
        if chunk.strip():
            return chunk
        return ""


class GeminiContextManager:
    """Geminiコンテキストマネージャ"""

    def __init__(self):
        self.logger = logging.getLogger("GeminiContextManager")
        self.contexts = {}

    async def save_context(self, session_id: str, context: Dict[str, Any]):
        """コンテキスト保存"""
        self.contexts[session_id] = {
            "data": context,
            "timestamp": datetime.now()
        }

    async def load_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """コンテキスト読み込み"""
        return self.contexts.get(session_id, {}).get("data")


class GeminiPerformanceMonitor:
    """Geminiパフォーマンス監視"""

    def __init__(self):
        self.metrics = {
            "executions": [],
            "response_times": [],
            "success_rates": [],
            "streaming_efficiency": []
        }

    async def record_execution(self, execution_data: Dict[str, Any]):
        """実行記録"""
        self.metrics["executions"].append(execution_data)
        self.metrics["response_times"].append(execution_data["execution_time"])

        if execution_data["success"]:
            self.metrics["success_rates"].append(1)
        else:
            self.metrics["success_rates"].append(0)

    def generate_report(self) -> Dict[str, Any]:
        """レポート生成"""
        total_executions = len(self.metrics["executions"])

        if total_executions == 0:
            return {"total_executions": 0}

        avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
        success_rate = sum(self.metrics["success_rates"]) / len(self.metrics["success_rates"])

        return {
            "total_executions": total_executions,
            "avg_response_time": avg_response_time,
            "success_rate": success_rate,
            "streaming_executions": sum(1 for ex in self.metrics["executions"] if ex.get("streaming_used", False))
        }


# テスト用メイン関数
async def main():
    """テスト実行"""
    logging.basicConfig(level=logging.INFO)

    skill = GeminiCLISkill()

    try:
        # 初期化
        if not await skill.initialize():
            print("初期化失敗")
            return

        # 基本テスト
        print("=== 基本機能テスト ===")
        result = await skill.execute_research_task("量子コンピューティングの最新トレンドを教えてください")
        print(f"結果: {result['success']}")
        if result['success']:
            print(f"応答長: {len(result.get('content', ''))}")
            print(f"実行時間: {result.get('execution_time', 0):.2f}秒")

        # ストリーミングテスト
        print("\n=== ストリーミングテスト ===")
        chunk_count = 0
        async for chunk in skill.stream_research_response("AIの未来について簡単に説明してください"):
            chunk_count += 1
            if chunk_count <= 3:  # 最初の3チャンクのみ表示
                print(f"チャンク {chunk_count}: {chunk[:50]}...")

        print(f"合計チャンク数: {chunk_count}")

        # パフォーマンスレポート
        print("\n=== パフォーマンスレポート ===")
        metrics = skill.get_performance_metrics()
        print(f"総実行数: {metrics.get('total_executions', 0)}")
        print(".2f"
        print(".1f"
    finally:
        await skill.shutdown()


if __name__ == "__main__":
    asyncio.run(main())