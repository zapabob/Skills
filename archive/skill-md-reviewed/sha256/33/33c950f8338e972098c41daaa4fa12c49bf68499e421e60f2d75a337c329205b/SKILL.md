---
name: line-bridge-evex-upgrade
description: Upgrade LINE bridge to @evex/linejs 3.5.x keeping zapabob features.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [line, bridge, evex, upgrade, zapabob]
---
# LINE Bridge Evex Upgrade Skill

This skill upgrades ~/.hermes/plugins/line-personal-bridge to @evex/linejs 3.5.x, preserves zapabob custom features (auto-reply, webhook, sendMessage, NOT_AUTHORIZED_DEVICE refresh), and verifies bridge readiness.
It does NOT modify hermes-agent core.

## When to Use
- Bridge is stopped with API incompatibility errors.
- @evex/linejs needs a 3.4→3.5 upgrade.
- Zapabob custom features must be kept.

## Prerequisites
- Node 18+ and npm.
- Plugin exists at ~/.hermes/plugins/line-personal-bridge.
- LINEJS_PERSONAL_EMAIL / LINEJS_PERSONAL_PASSWORD in ~/.hermes/.env.
- Allow remote npm fetch for jsr registry.

## How to Run
Invoke through Hermes tools: `terminal`, `read_file`, `write_file`, `patch`, `execute_code`.

## Quick Reference
- Path: ~/.hermes/plugins/line-personal-bridge/bridge.mjs
- Dependency: @evex/linejs npm:@jsr/evex__linejs@^3.5.0
- Status URL: http://127.0.0.1:9101/status
- Chats URL: http://127.0.0.1:9101/chats

## Procedure
1. Read package.json and bridge.mjs via `read_file`.
2. Set dependency to npm:@jsr/evex__linejs@^3.5.0 with `write_file` or `patch`.
3. Run `terminal` `cd ~/.hermes/plugins/line-personal-bridge && npm install --legacy-peer-deps`.
4. Verify version: `cat node_modules/@evex/linejs/package.json`.
5. Start bridge: `terminal` background `node bridge.mjs`.
6. Wait 3s then `terminal` `curl http://127.0.0.1:9101/status`.
7. Expect loginState ready and profile present.

## Pitfalls
- npm EALLOWREMOTE for jsr: set registry in .npmrc.
- EPERM during cleanup on Windows: run npm install again after lock release.
- NOT_AUTHORIZED_DEVICE on first /chats call is normal post-upgrade; status remains ready.

## Verification
`curl -s http://127.0.0.1:9101/status | python -c "import sys,json; d=json.load(sys.stdin); print(d['loginState'])"` prints `ready`.
