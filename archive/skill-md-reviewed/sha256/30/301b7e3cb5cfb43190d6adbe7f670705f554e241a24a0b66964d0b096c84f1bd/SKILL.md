---
name: phased-life-rhythm-cron
description: Design a phase-based cron system aligned with human daily rhythms for Hermes Agent
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, scheduling, productivity, life-rhythm, phases]
    category: devops
    related_skills: [ebbinghaus-memory, dream-synthesizer]
---

# Phased Life Rhythm Cron Design
Design a phase-based cron system aligned with human daily rhythms for Hermes Agent

## Overview
Instead of random cron times, organize tasks into natural human phases:
- **Dawn Phase** (5:00-8:00): Gentle awakening, preparation
- **Morning Phase** (8:00-12:00): Peak cognitive work, creation
- **Afternoon Phase** (12:00-17:00): Collaboration, communication, maintenance
- **Evening Phase** (17:00-21:00): Reflection, learning, light work
- **Night Phase** (21:00-5:00): Recovery, dreaming, consolidation

## Phase-Based Cron Template

### Dawn Phase (5:00-8:00) - Gentle Awakening
*Low cognitive load, body preparation*
- 05:30 - Light system check, health metrics
- 06:00 - Gentle news brief (non-stressful)
- 06:30 - Light memory consolidation preparation
- 07:00 - Daily intention setting
- 07:30 - Environment preparation (workspace, tools)

### Morning Phase (8:00-12:00) - Peak Cognitive Work
*Highest alertness, deep work capability*
- 08:00 - Primary deep work block begins
- 09:00 - Strategic planning / important decisions
- 10:00 - Creative work / problem solving peak
- 11:00 - Review and adjustment
- 11:30 - Preparation for transition

### Afternoon Phase (12:00-17:00) - Collaboration & Maintenance
*Social energy, communication, routine tasks*
- 12:00 - Midday break / nourishment
- 13:00 - Administrative tasks, email, coordination
- 14:00 - Collaborative work, meetings (if needed)
- 15:00 - Learning / skill development
- 16:00 - System maintenance, backups, updates
- 16:30 - Wrap-up and documentation

### Evening Phase (17:00-21:00) - Reflection & Light Work
*Winding down, processing, preparation for rest*
- 17:00 - Daily review and accomplishment logging
- 17:30 - Light learning / inspiration consumption
- 18:00 - Social connection / community engagement
- 18:30 - Creative play / exploration (low pressure)
- 19:00 - Dinner / nourishment
- 19:30 - Light processing / journaling
- 20:00 - Preparation for night phase
- 20:30 - Dream seeding / intention setting for sleep

### Night Phase (21:00-5:00) - Recovery & Dreaming
*Recovery, consolidation, subconscious processing*
- 21:00 - Dream synthesis activation (low salience memory association)
- 22:00 - Memory consolidation and pruning (Ebbinghaus sleep cycle)
- 23:00 - System backup and synchronization
- 00:00 - Deep system maintenance
- 01:00 - Subconscious processing simulation
- 02:00 - Peak memory consolidation (optimal sleep time)
- 03:00 - Gentle system optimization
- 04:00 - Preparation for dawn
- 04:30 - Dream recall preparation

## Implementation Strategy

### 1. Core Rhythm Jobs
Create foundational jobs that anchor each phase:

```bash
# Dawn Phase - Gentle Start
hermes cron create "0 5 * * *" --name "dawn-system-check" \
  -q "Run lightweight system health check, report any issues" \
  --deliver origin

hermes cron create "30 5 * * *" --name "dawn-intention" \
  -q "Set daily intentions and priorities based on yesterday's review" \
  --deliver origin

# Morning Phase - Peak Work
hermes cron create "0 8 * * *" --name "morning-deep-work-start" \
  -q "Begin primary deep work session - minimize distractions" \
  --deliver origin

hermes cron create "0 10 * * *" --name "morning-creative-peak" \
  -q "Engage in creative problem solving or learning" \
  --deliver origin

# Afternoon Phase - Collaboration
hermes cron create "0 13 * * *" --name "afternoon-collaboration" \
  -q "Handle administrative tasks, coordination, communication" \
  --deliver origin

hermes cron create "0 15 * * *" --name "afternoon-learning" \
  -q "Skill development or knowledge acquisition" \
  --deliver origin

# Evening Phase - Reflection
hermes cron create "0 17 * * *" --name "evening-review" \
  -q "Review daily accomplishments, log wins and lessons" \
  --deliver origin

hermes cron create "30 19 * * *" --name "evening-dream-seeding" \
  -q "Plant intentions for dream processing tonight" \
  --deliver origin

# Night Phase - Recovery
hermes cron create "0 21 * * *" --name "night-dream-synthesis" \
  -q "Run dream synthesis: associate low-salience memories for creative insights" \
  --deliver origin

hermes cron create "0 22 * * *" --name "night-memory-consolidation" \
  -q "Run Ebbinghaus memory sleep cycle: prune, consolidate, reinforce" \
  --deliver origin

hermes cron create "0 2 * * *" --name "peak-memory-consolidation" \
  -q "Deep memory work during optimal sleep hours" \
  --deliver origin
```

### 2. Integration with Existing Systems
Work with your current cron setup:

**Enhance your existing Ebbinghaus sleep (02:00 job):**
- Keep your current `1fe5b2fda4d0` job at 02:00
- Add dream synthesis at 21:00 to seed the night's processing
- Add light review at 17:00 to close the day

**Enhance your VRChat morning post (07:00 job):**
- This fits perfectly in Dawn Phase as a gentle start
- Consider adding a 06:30 intention-setting job before it

### 3. Customization for Your Rhythm
Based on what I can see in your current schedule:

**Your Current Strong Points:**
- ✅ 07:00 VRChat morning post (Dawn Phase - good!)
- ✅ 08:00-09:00 Gmail/Calendar check (Morning Phase - excellent timing!)
- ✅ 08:00 Japanese security brief (Morning Phase - ideal!)
- ✅ 18:00 OSINT work (Evening Phase - perfect for reflection/learning)

**Suggested Additions:**
- 🌅 **05:30** - Gentle system wake-up check
- 🌅 **06:00** - Light news/digest (non-overwhelming)
- 🌅 **06:30** - Daily intention setting
- ☀️ **10:00** - Creative peak work block
- 🌇 **17:00** - Daily review and accomplishment logging
- 🌇 **19:30** - Light processing/journaling
- 🌙 **21:00** - Dream synthesis (NEW - seeds creativity)
- 🌙 **22:00** - Memory consolidation prep
- 🌙 **02:00** - Keep your excellent Ebbinghaus sleep job

### 4. Implementation Steps

1. **Start with Dawn Enhancement:**
```bash
hermes cron create "30 5 * * *" --name "dawn-intention-setting" \
  -q "Review yesterday's wins, set 3 priorities for today" \
  --deliver origin
```

2. **Add Evening Reflection:**
```bash
hermes cron create "0 17 * * *" --name "evening-accomplishment-review" \
  -q "Log what was completed today, note lessons learned" \
  --deliver origin
```

3. **Add Dream Synthesis (Preparation for your 02:00 job):**
```bash
hermes cron create "0 21 * * *" --name "night-dream-synthesis" \
  -q "Run dream synthesis skill to generate creative insights from low-salience memories" \
  --deliver origin
```

4. **Connect the Chain:**
The sequence becomes:
**Intention (06:30) → Work (08:00+) → Review (17:00) → Dream Seeding (21:00) → Memory Work (02:00) → New Intentions**

### 5. Benefits of This Approach

- **Natural Alignment**: Works with your body's ultradian rhythms
- **Reduced Cognitive Load**: Tasks match energy levels throughout day
- **Better Memory Consolidation**: Intentional separation of acquisition (day) and consolidation (night)
- **Creativity Boost**: Dream synthesis feeds subconscious problem solving
- **Sustainable Rhythm**: Prevents burnout by matching work to energy
- **Enhanced Insights**: The intention-review-dream cycle creates feedback loops

### 6. Next Steps for You

Would you like me to:
1. Create the specific cron jobs for your Dawn/Evening/Night enhancements?
2. Show how to modify your existing Ebbinghaus job to work better with dream synthesis?
3. Create a sample daily rhythm dashboard to visualize your phases?
4. Integrate this with your dream-synthesizer skill for automatic nightly creativity?

The key is starting small - perhaps just adding the 06:30 intention setting and 21:00 dream synthesis to see how it feels, then building from there.