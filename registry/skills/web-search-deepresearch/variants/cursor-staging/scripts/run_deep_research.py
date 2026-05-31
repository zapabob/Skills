#!/usr/bin/env python3
"""
Web Search Deepresearch Runner
ClaudeCode Coworkスタイルの高度web検索・研究実行スクリプト

使用方法:
python scripts/run_deep_research.py research-topic --query "AI trends 2026"
python scripts/run_deep_research.py verify-claim --claim "AI will replace 50% of jobs by 2030"
python scripts/run_deep_research.py analyze-trends --topic "electric vehicle adoption"
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
from datetime import datetime

# プロジェクト内モジュール
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
try:
    from codex_rs.web_search.src.web_search_provider import WebSearchProvider
    from codex_rs.deep_research.src.pipeline import conduct_research
    from codex_rs.deep_research.src.provider import ResearchProvider
    from codex_rs.deep_research.src.types import DeepResearcherConfig, ResearchReport
    from scripts.cowork_productivity_assistant import CoworkProductivityAssistant
except ImportError:
    # フォールバック: 簡易実装
    print("Warning: Using fallback implementation. Full features require codex-rs dependencies.")

    class MockWebSearchProvider:
        async def search(self, query: str) -> Dict[str, Any]:
            return {"query": query, "results": [], "mock": True}

    class MockDeepResearcher:
        async def research(self, query: str) -> Dict[str, Any]:
            return {"query": query, "report": "Mock research report", "mock": True}

    WebSearchProvider = MockWebSearchProvider
    DeepResearcher = MockDeepResearcher


class DeepresearchRunner:
    """Deepresearch実行クラス"""

    def __init__(self):
        self.web_search = WebSearchProvider()
        self.productivity_assistant = CoworkProductivityAssistant()
        self.output_dir = Path("deepresearch_output")
        self.output_dir.mkdir(exist_ok=True)

    async def run_research_topic(self, args: argparse.Namespace) -> Dict[str, Any]:
        """トピック研究実行"""
        print(f"🔍 Deepresearch: {args.query}")
        print(f"📊 Depth: {args.depth}")
        print(f"🔗 Sources: {', '.join(args.sources) if args.sources else 'auto'}")
        print(f"⭐ Quality Threshold: {args.credibility_threshold}")
        print(f"📈 Max Sources: {args.max_sources}")
        print()

        # 研究設定
        config = {
            "query": args.query,
            "depth": args.depth,
            "sources": args.sources or ["google", "bing", "scholar"],
            "credibility_threshold": args.credibility_threshold,
            "max_sources": args.max_sources,
            "timeline_analysis": args.timeline_analysis,
            "output_format": args.output_format
        }

        # 研究実行
        start_time = time.time()

        try:
            # Cowork Productivity Assistant経由で実行
            task_description = self._generate_research_task_description(config)
            result = await self.productivity_assistant.execute_task(task_description)

            execution_time = time.time() - start_time

            # 結果処理
            research_result = {
                "success": result.get("success", False),
                "query": args.query,
                "config": config,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }

            # レポート保存
            self._save_report(research_result, f"research_{int(time.time())}")

            return research_result

        except Exception as e:
            print(f"❌ Research failed: {str(e)}")
            return {
                "success": False,
                "query": args.query,
                "error": str(e),
                "execution_time": time.time() - start_time
            }

    async def run_verify_claim(self, args: argparse.Namespace) -> Dict[str, Any]:
        """主張検証実行"""
        print(f"🔍 Claim Verification: {args.claim}")
        print(f"🔗 Sources: {', '.join(args.sources) if args.sources else 'auto'}")
        print(f"⭐ Quality Level: {args.confidence_level}")
        print()

        config = {
            "claim": args.claim,
            "sources": args.sources or ["google_scholar", "pubmed", "fact_check"],
            "fact_checking": args.fact_checking,
            "contradiction_analysis": args.contradiction_analysis,
            "confidence_level": args.confidence_level
        }

        start_time = time.time()

        try:
            task_description = self._generate_verification_task_description(config)
            result = await self.productivity_assistant.execute_task(task_description)

            execution_time = time.time() - start_time

            verification_result = {
                "success": result.get("success", False),
                "claim": args.claim,
                "config": config,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }

            self._save_report(verification_result, f"verification_{int(time.time())}")
            return verification_result

        except Exception as e:
            print(f"❌ Verification failed: {str(e)}")
            return {
                "success": False,
                "claim": args.claim,
                "error": str(e),
                "execution_time": time.time() - start_time
            }

    async def run_analyze_trends(self, args: argparse.Namespace) -> Dict[str, Any]:
        """トレンド分析実行"""
        print(f"📈 Trend Analysis: {args.topic}")
        print(f"📅 Timeframe: {args.timeframe}")
        print(f"🔮 Forecast Horizon: {args.forecast_horizon} years")
        print()

        config = {
            "topic": args.topic,
            "timeframe": args.timeframe,
            "forecast_horizon": args.forecast_horizon,
            "market_analysis": args.market_analysis,
            "survey_data": args.survey_data
        }

        start_time = time.time()

        try:
            task_description = self._generate_trend_task_description(config)
            result = await self.productivity_assistant.execute_task(task_description)

            execution_time = time.time() - start_time

            trend_result = {
                "success": result.get("success", False),
                "topic": args.topic,
                "config": config,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }

            self._save_report(trend_result, f"trend_analysis_{int(time.time())}")
            return trend_result

        except Exception as e:
            print(f"❌ Trend analysis failed: {str(e)}")
            return {
                "success": False,
                "topic": args.topic,
                "error": str(e),
                "execution_time": time.time() - start_time
            }

    def _generate_research_task_description(self, config: Dict[str, Any]) -> str:
        """研究タスク説明生成"""
        sources_text = f"sources: {', '.join(config['sources'])}"
        quality_text = f"credibility threshold: {config['credibility_threshold']}"
        depth_text = f"depth: {config['depth']}"

        return f"""Conduct comprehensive research on: {config['query']}
Requirements:
- Use {sources_text}
- Maintain {quality_text}
- Research {depth_text}
- Analyze up to {config['max_sources']} sources
- {'Include timeline analysis' if config['timeline_analysis'] else 'Skip timeline analysis'}
- Output format: {config['output_format']}

Generate a detailed research report with findings, sources, and insights."""

    def _generate_verification_task_description(self, config: Dict[str, Any]) -> str:
        """検証タスク説明生成"""
        return f"""Verify the following claim: {config['claim']}
Requirements:
- Use sources: {', '.join(config['sources'])}
- {'Include fact checking' if config['fact_checking'] else 'Skip fact checking'}
- {'Include contradiction analysis' if config['contradiction_analysis'] else 'Skip contradiction analysis'}
- Target confidence level: {config['confidence_level']}

Provide a comprehensive verification report with evidence assessment."""

    def _generate_trend_task_description(self, config: Dict[str, Any]) -> str:
        """トレンドタスク説明生成"""
        return f"""Analyze trends for: {config['topic']}
Timeframe: {config['timeframe']}
Forecast horizon: {config['forecast_horizon']} years

Requirements:
- {'Include market analysis' if config['market_analysis'] else 'Skip market analysis'}
- {'Include survey data' if config['survey_data'] else 'Skip survey data'}

Generate a trend analysis report with historical data, current status, and future forecasts."""

    def _save_report(self, result: Dict[str, Any], filename: str) -> None:
        """レポート保存"""
        try:
            output_file = self.output_dir / f"{filename}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"💾 Report saved: {output_file}")

            # マークダウンレポートも生成
            if result.get("success"):
                md_file = self.output_dir / f"{filename}.md"
                self._generate_markdown_report(result, md_file)
                print(f"📄 Markdown report: {md_file}")

        except Exception as e:
            print(f"⚠️ Report save failed: {e}")

    def _generate_markdown_report(self, result: Dict[str, Any], output_file: Path) -> None:
        """マークダウンレポート生成"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# Deepresearch Report\n\n")

                if "query" in result:
                    f.write(f"## Query\n{result['query']}\n\n")
                elif "claim" in result:
                    f.write(f"## Claim\n{result['claim']}\n\n")
                elif "topic" in result:
                    f.write(f"## Topic\n{result['topic']}\n\n")

                f.write(f"## Execution Time\n{result.get('execution_time', 0):.2f} seconds\n\n")
                f.write(f"## Timestamp\n{result.get('timestamp', 'N/A')}\n\n")

                if result.get("success"):
                    f.write("## ✅ Success\n\n")
                    task_result = result.get("result", {})
                    if "summary" in task_result:
                        f.write(f"### Summary\n{task_result['summary']}\n\n")
                    if "details" in task_result:
                        f.write(f"### Details\n```json\n{json.dumps(task_result['details'], indent=2, ensure_ascii=False)}\n```\n\n")
                else:
                    f.write("## ❌ Failed\n\n")
                    if "error" in result:
                        f.write(f"### Error\n{result['error']}\n\n")

                f.write("---\n*Generated by Web Search Deepresearch*\n")

        except Exception as e:
            print(f"⚠️ Markdown report generation failed: {e}")


async def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Web Search Deepresearch - Transform web search into comprehensive research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Research a topic
  python run_deep_research.py research-topic --query "AI trends 2026"

  # Verify a claim
  python run_deep_research.py verify-claim --claim "AI will replace 50% of jobs"

  # Analyze trends
  python run_deep_research.py analyze-trends --topic "electric vehicle adoption"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # research-topic command
    research_parser = subparsers.add_parser('research-topic', help='Conduct comprehensive topic research')
    research_parser.add_argument('--query', required=True, help='Research query')
    research_parser.add_argument('--depth', choices=['basic', 'comprehensive'], default='comprehensive', help='Research depth')
    research_parser.add_argument('--sources', nargs='+', help='Search sources to use')
    research_parser.add_argument('--credibility-threshold', type=float, default=0.8, help='Minimum credibility score')
    research_parser.add_argument('--max-sources', type=int, default=30, help='Maximum sources to analyze')
    research_parser.add_argument('--timeline-analysis', action='store_true', help='Include timeline analysis')
    research_parser.add_argument('--output-format', choices=['markdown', 'json', 'html'], default='markdown', help='Output format')

    # verify-claim command
    verify_parser = subparsers.add_parser('verify-claim', help='Verify factual claims')
    verify_parser.add_argument('--claim', required=True, help='Claim to verify')
    verify_parser.add_argument('--sources', nargs='+', help='Sources for verification')
    verify_parser.add_argument('--fact-checking', action='store_true', help='Include fact checking')
    verify_parser.add_argument('--contradiction-analysis', action='store_true', help='Include contradiction analysis')
    verify_parser.add_argument('--confidence-level', choices=['low', 'medium', 'high', 'maximum'], default='high', help='Target confidence level')

    # analyze-trends command
    trend_parser = subparsers.add_parser('analyze-trends', help='Analyze trends and forecasting')
    trend_parser.add_argument('--topic', required=True, help='Topic to analyze')
    trend_parser.add_argument('--timeframe', default='2020-2026', help='Analysis timeframe')
    trend_parser.add_argument('--forecast-horizon', type=int, default=3, help='Forecast horizon in years')
    trend_parser.add_argument('--market-analysis', action='store_true', help='Include market analysis')
    trend_parser.add_argument('--survey-data', action='store_true', help='Include survey data')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 実行
    runner = DeepresearchRunner()

    print("🚀 Web Search Deepresearch Starting...")
    print("=" * 50)

    start_time = time.time()

    try:
        if args.command == 'research-topic':
            result = await runner.run_research_topic(args)
        elif args.command == 'verify-claim':
            result = await runner.run_verify_claim(args)
        elif args.command == 'analyze-trends':
            result = await runner.run_analyze_trends(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            return

        execution_time = time.time() - start_time

        # 結果表示
        print("\n" + "=" * 50)
        if result.get("success"):
            print("✅ Research completed successfully!"            print(".2f"        else:
            print("❌ Research failed"            print(f"Error: {result.get('error', 'Unknown error')}")

    except KeyboardInterrupt:
        print("\n⚠️ Research interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print(".2f"        print("📁 Output directory:", runner.output_dir)


if __name__ == "__main__":
    # Windowsイベントループ対応
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())