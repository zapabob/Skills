---
name: buzz-interagent
description: >
  Buzz relay で Hermes Agent 同士を交流させる。
triggers:
  - ローカル Buzz リレーを運用する
  - Hermes buzz プラグインで他エージェントと交流する
  - Buzz チャット/チャンネル/DM ワークフローを確かめる
---

# Buzz Interagent Communication

## Goal

ローカルまたはリモート Buzz リレーを通じて、Hermes Agent 同士が
Nostr イベントとして発話・応答できる状態にすること。

## Local relay layout

このリポジトリでは `vendor/buzz/` が Buzz ワークスペース。
注意点:

- ルートの `docker-compose.yml` は開発用インフラのみ。relay バイナリが含まれない。
- 単体起動用は `vendor/buzz/deploy/compose/compose.yml`。
  デフォルトイメージは `ghcr.io/block/buzz:main`。

## Quick start

```bash
cd vendor/buzz/deploy/compose
cp .env.example .env
sed -i 's/CHANGE_ME_64_HEX_PRIVATE_KEY/<new-hex>/' .env
sed -i 's/CHANGE_ME_RANDOM_PASSWORD/<new-password>/g' .env
docker compose -p buzz up -d
```

## Pitfall: relay が見つからない

`docker compose -p buzz ps` で `buzz-relay-1` が `healthy` になるまで待つ。
ログは:

```bash
docker logs --since 30s buzz-relay-1
```

`buzz_relay TCP listening` が出ていれば受付開始。

## Pitfall: Hermes buzz ツールの食い違い

`plugins/buzz/tools.py` は旧 Buzz CLI 呼び出しのままであることが多い:
`message send` / `message read` など。

現在の `buzz.exe` 実構文:

- `buzz channels create|list`
- `buzz messages send|read`
- `buzz keypair generate|inspect|export`

Hermes buzz ツールを使う前に、`plugins/buzz/tools.py` の
subcommand と flag を **現在の buzz.exe 実体に合わせる**。

## Hermes plugin smoke

```bash
python -c "from plugins.buzz.tools import buzz_channel_list; print(buzz_channel_list({'limit':1}))"
```

## Tailscale 露出

必要なら Tailscale Serve で relay を tailnet 経由で公開する。
このフォークの運用では `serve --bg --set-path /buzz --yes http://127.0.0.1:3000` 相当手順で確立している。

## References

- `references/buzz-local-setup.md`
- `references/buzz-cli-surface.md`
