---
name: yaraikata-memo
description: Run long tasks with regular simple updates and an easy explanation. Use when work will not finish quickly, the user wants check-ins every 5 minutes, wants a plain summary with an expected time, and wants clear guidance if something goes wrong.
---

# Yaraikata Memo

## Overview
Run the work with a helper in the background. Every 5 minutes, give a short update with expected time. Explain how it works in simple words. If something goes wrong, give simple next steps.

## Steps
1. Acknowledge quickly before long work, especially in chat gateways like LINE. If tool work, search, scheduling, or tests may take more than a few seconds, send a short "受けた、確認して動く" style acknowledgement when possible before deeper execution.
2. Confirm the goal, what "done" means, and where results should appear.
3. Start a helper to do the work while you stay responsive.
4. Every 5 minutes, check the helper and report:
   - What is done
   - What is next
   - Expected time (rough)
5. Ask a second helper to explain how it works. Share the explanation in plain words.
6. If there is a problem:
   - Say what happened in one short sentence
   - Offer 1-2 simple choices to fix it
   - Ask which choice to try
7. If the user says "タスク中止", "中止", "stop", or jokes that the agent is overfocused/過集中 during an active task:
   - Treat it as a cancellation/control request before continuing the original work.
   - Stop or remove any pending scheduled/background work that matches the current task. For cron jobs, list jobs first, then remove the exact matching job ID; never guess IDs.
   - If the job/process is already gone, say that plainly and summarize the verified current state.
   - Keep the reply short; do not continue the cancelled task unless the user asks again.

## Output style
- Keep updates short and clear
- Avoid jargon
- Prefer simple words
- Use the same shape each time
- For LINE or other short-message gateways, avoid making the user wait silently while checking prerequisites; acknowledge first, then report the verified result after tools complete.

## Pitfalls
- A technically correct delayed response can feel like the user was "焦らされた". For time-sensitive or conversational requests, prioritize a tiny acknowledgement before lengthy verification or scheduling work.
