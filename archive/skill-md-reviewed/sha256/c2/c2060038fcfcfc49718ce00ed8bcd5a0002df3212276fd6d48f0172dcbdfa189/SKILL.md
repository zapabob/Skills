---
name: line-platform-integration
category: devops
description: Use when setting up LINE platform integration in Hermes.
tags: [Tailscale-Funnel, LINE, devops]
author: Hermes
---

# line-platform-integration

Use when setting up LINE platform integration in Hermes.

## Steps

1. Verify `line-platform` plugin status:
   ```bash
   hermes plugins list | grep line-platform
   ```

2. Ensure gateway environment has `aiohttp==3.14.3`:
   ```bash
   pip install aiohttp==3.14.3 --break-system-packages
   ```

3. Configure Hermes for LINE platform:
   ```bash
   hermes config set platforms.line-json "{\"platform\":\"line\",\"webhook_url\":\"https://<your-public-url>/line/webhook\"}"
   ```

4. Start Hermes gateway and verify listening port:
   ```bash
   hermes gateway start
   netstat -ano | grep 8646
   ```

5. Set up Tailscale Funnel for public tunnel:
   ```bash
   # Use Tailscale to expose local port 8646
   tshctl fwd --addr 127.0.0.1:8646 --target https://<your-public-url>/line/webhook
   ```

6. Verify webhook health and signature:
   ```bash
   curl -sS -i http://127.0.0.1:8646/line/webhook/health
   curl -sS -i -X POST http://127.0.0.1:8646/line/webhook -H "Content-Type: application/json" -H "x-line-signature: test" --data '{"events":[],"destination":"test"}'
   ```

7. Test LINE API authentication:
   ```bash
   curl -sS -H "Authorization: Bearer <channel-access-token>" https://api.line.me/v2/bot/info
   ```

8. Test auto-reply functionality:
   ```bash
   hermes -t line-personal line-personal send <chat-id> "テストメッセージ #はくあ #hermesagent"
   ```

## Notes

- Ensure `line-platform` and `line-ai-bot` plugins are both enabled.
- The gateway requires `aiohttp`; install it in the uv-managed Python environment.
- Use Tailscale Funnel instead of ngrok for reliable public access.
- Verify webhook signature verification is enabled in the adapter.