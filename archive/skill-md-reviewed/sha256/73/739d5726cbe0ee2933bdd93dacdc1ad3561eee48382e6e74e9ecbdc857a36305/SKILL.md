---
name: vrchat-daily-post-cron-recovery
description: "Recover VRChat daily photo+voice cron when js2py/pydantic breakage stops X posting."
version: 0.1.0
author: Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [cron, vrchat, x-posting, uv-venv, js2py, lm-twitterer]
    related_skills: [vrchat_daily_tweet, hermes-x-posting-workflows]
---

# VRChat Daily Post Cron Recovery

When the 07:00 VRChat photo + Hakua voice X posting cron appears to run (`execution_success: true`) but no tweet appears on X, the root cause is usually `lm-twitterer` media posting failing silently due to `js2py` / `pydantic