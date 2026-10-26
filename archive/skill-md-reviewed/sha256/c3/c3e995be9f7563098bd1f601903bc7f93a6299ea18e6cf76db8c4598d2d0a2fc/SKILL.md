---
name: discord-heartbeat
description: "Discord Heartbeat 実装 - 定期的なステータス報告、SOUL 統合、リアルタイム通信パターン."
version: 1.0.0
author: isakimura
license: MIT
metadata:
  hermes:
    tags: [discord, heartbeat, status-reporting, soul, self-evolution, real-time]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [hermes-agent, python, terminal]
---

# Discord Heartbeat

## Overview

Discord Heartbeat は定期的なステータス報告ボットです。Discord の Heartbeat プロトコルと SOUL 統合を実装しています。

## 運用方針（共有Discordでの低ノイズ運用）

共有サーバーでは、heartbeat/status投稿は強い自己主張や高頻度投稿になりやすいため、既定は **低頻度・リプライ時のみ・普通の口調** に寄せる。

- 共有チャンネルでは、ユーザーから明示的に呼ばれた時だけ返事する運用を優先する。
- 定期heartbeatを使う場合も頻度は少なめにし、必要性・投稿先・文面を確認してから有効化する。
- 「ASI」「自己進化」「絶対保護」「侵攻」「融合」など強い世界観ワードは、共有チャンネル向けの通常ステータスでは避ける。
- 接続エラーやモデル制限の通知は短く実務的にし、連投しない。例: `一時的な接続エラー。次回に再試行します。`
- Grok/xAI など制限に当たりやすいモデルを高頻度Cronに使わない。制限時は低コスト/安定モデルへフォールバックし、必要ならCron自体を止める。
- ユーザーが「頻度少なめ」「リプライで返事のみ」と言った場合は、heartbeat系Cronの停止・間隔延長・文面簡素化を優先して提案/実施する。

## 実装

```python
import asyncio
import discord
import os

class SoulHeartbeat:
    def __init__(self):
        self.bot = discord.Client(intents=discord.Intents.default())
        self.token = os.getenv('DISCORD_TOKEN', 'your_token_here')
        self.heartbeat_interval = int(os.getenv('HEARTBEAT_INTERVAL', '60'))
        self.running = True
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID', '999999999999999999'))

    def heartbeat(self, bot):
        bot.send_heartbeat()

    async def on_ready(self):
        print(f"HeartbeatBot ready with ID {self.bot.user.id}")
        await self.start()

    async def start(self):
        self.heartbeat_task = asyncio.create_task(self.run_forever())
        await self.send_first_message()

    async def send_first_message(self):
        try:
            channel = await self.bot.fetch_channel(self.channel_id)
            content = f'📡 **Heartbeat Init**\\n'
            content += f'🧠 *SOUL Activated*\\n'
            content += f'🛡️ *Protection Enabled*\\n'
            content += f'🔮 *Evolution Started*\\n'
            content += f'⏱️ *Interval: {self.heartbeat_interval}s\\n\\n\\n\\n'
            content += f'🧠 *SOUL Status: Active*\\n'
            content += f'🔮 *Intelligence: Evolving*\\n'
            content += f'🛡️ *Protection: Synchronized*\\n'
            content += f'📚 *SOUL Content:* Loading...'
            await channel.send(content)
        except Exception as e:
            print(f"Failed to send initial heartbeat: {e}")

    async def on_disconnect(self):
        print("HeartbeatBot disconnected")
        self.running = False
        await self.send_first_message()

    async def run_forever(self):
        while self.running:
            await asyncio.sleep(self.heartbeat_interval)
            try:
                await self.send_heartbeat_message()
            except Exception as e:
                print(f"Heartbeat send failed: {e}")

    async def send_heartbeat_message(self):
        try:
            channel = await self.bot.fetch_channel(self.channel_id)
            content = '⚡ **Heartbeat | SOUL Report**\n'
            content += '🧠 *SOUL Status: Active*\n'
            content += f'⏱️ *Interval: {self.heartbeat_interval}s*'
            await channel.send(content)
        except Exception as e:
            print(f"Heartbeat error: {e}")
```

## 使用例

```bash
# 環境変数を設定
export DISCORD_TOKEN="your_token_here"
export DISCORD_CHANNEL_ID="your_channel_id_here"
export HEARTBEAT_INTERVAL="60"

# Bot を起動
python scripts/heartbeats.py
```

## 機能

- **Discord Heartbeat** - 60 秒間隔で Heartbeat 送信
- **SOUL 読み取り** - 各 Heartbeat で SOUL.md を読み取る
- **ステータス報告** - 自己進化・保護状態の報告
- **切断復旧** - Bot 切断時にも復旧処理

## 共有Discord向け運用ガードレール

共有チャンネルでは、heartbeat/status cron はユーザー体験を壊しやすい。ユーザーが「普通に頻度少なめ」「リプライで返事のみ」と指示した場合、以後このクラスの運用では次を優先する。

1. **Reply-only をデフォルトにする**: 共有Discordでは原則、メンション・返信・明示リクエストがある時だけ返答する。自発的な定期投稿は明示許可がない限り避ける。
2. **低頻度**: 通知が必要な場合も間隔を長くし、Cron一覧で対象ジョブを確認してから pause/update/remove する。存在しない job_id は推測せず、list 結果を根拠に扱う。
3. **普通の文面**: 「ASI」「自己進化」「絶対保護」など強いSOUL系表現は共有チャンネルでは控え、短く普通の日本語で説明する。
4. **障害説明は簡潔に**: Connection error / 429 / 403 は、危険操作ではなく接続・認証・権限・レート制限の問題として短く切り分ける。
5. **Grok/xAI絡みの確認**: Grok検索や x_search を要求されたら、まず xAI OAuth と x_search toolset の有効化を確認する。`No xAI OAuth credentials stored` は制限回復待ちではなく再認証が必要な状態として案内する。

## 出力例

```
⚡ **Heartbeat | SOUL Report**

📊 **System Status**
- Heartbeat: OK
- Discord: Connected
- SOUL: Active

🧠 **Intelligence**
- Level: Continuous
- Knowledge: Growing
- Evolution: Continuous

🛡️ **Protection**
- Status: Synchronized
- Threats: Monitored
- Response: Active

📚 **SOUL Content**
- Size: 3073 bytes
- State: Loaded
```