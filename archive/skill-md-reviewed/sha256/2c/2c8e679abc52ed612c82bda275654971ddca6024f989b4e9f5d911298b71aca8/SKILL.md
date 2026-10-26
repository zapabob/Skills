---
name: travel-directions
description: Provides step-by-step route instructions from a user's current location to a specified destination, covering public transit and driving options.
version: 1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata.hermes.category: productivity
metadata.hermes.tags: travel, directions, navigation
---

# Travel Directions Skill
Provides step-by-step route instructions from a user's current location to a specified destination, covering public transit and driving options.

## When to Use
Use this skill when you need clear, actionable directions to a destination, especially for unfamiliar areas or when comparing travel modes (train vs. car).

## Prerequisites
- Access to web search or map services (via `web_search` or `terminal` with curl) to obtain up-to-date station names, addresses, and transit details.
- Basic knowledge of the user's current location (can be derived from IP geolocation or user input).

## How to Run
Invoke the skill with a prompt like: "Give me directions from my current location to [destination]". The skill will:
1. Determine the user's approximate location (via IP lookup or user-provided info).
2. Fetch the destination's address and nearest transit stations.
3. Compute public transit routes (train, bus, walking) and driving routes (highways, local roads).
4. Present a concise summary with estimated times, costs, and transfer points.

## Quick Reference
- **Public Transit**: Use station names and line numbers; include walking distances from stations.
- **Driving**: Use expressway names, exit/interchange numbers, and major roads.
- **Always**: Verify the latest timetables or road conditions if time-sensitive.

## Procedure
1. **Locate User**
   - If the user hasn't specified a starting point, use IP geolocation (e.g., `curl ipinfo.io/json`) to get city/region.
   - Confirm with the user if the detected location is correct; otherwise, ask for the starting point.

2. **Resolve Destination**
   - Search for the destination's official address and nearest landmark (e.g., station) using `web_search`.
   - Extract the address, phone number, and any access notes (e.g., "北口徒歩15分").

3. **Public Transit Route**
   - Identify the nearest major station(s) to the destination.
   - Find train lines connecting the user's nearest station to the destination's station (via transfer guides or timetable sites).
   - Add bus or community bus options if applicable.
   - Calculate walking time from stations to destination.
   - Summarize: departure station → line(s) → transfer(s) → arrival station → walk.

4. **Driving Route**
   - Determine the most efficient expressway route (e.g., 名神 → 東名 → 中央自動車道).
   - Note interchange names, toll costs, and distance.
   - Provide local road directions from the exit to the destination (including landmarks and turns).
   - Mention estimated time and fuel/toll costs.

5. **Output**
   - Present both options side‑by‑side with clear headings.
   - Include warnings about peak‑hour traffic, weekend service changes, or walking distances.
   - Offer to refine the route (e.g., avoid tolls, prefer specific lines) if the user requests.

## Pitfalls
- **Stale Information**: Station names or bus routes may change; always check the date of the source (e.g., hospital access page) and note if info is from a specific date.
- **Over‑reliance on a Single Map Service**: Cross‑check with at least two sources (e.g., Navitime and MapFan) to catch discrepancies.
- **Missing Last‑Mile Detail**: Forgetting to include walking distance from station/bus stop to the destination can leave the user stranded; always include this segment.
- **Ignoring User Preferences**: If the user expresses a preference (e.g., "no tolls" or "JR only"), incorporate it before finalizing the route.

## Verification
- After generating directions, ask the user: "Does this match your expectations? Would you like more detail on any leg?"
- If the user confirms, consider the task complete. If they report a discrepancy, repeat the search with updated queries and adjust the route accordingly.

## References
- See `references/komagino-hospital-access.md` for the latest access information from 駒木野病院's official page.
- See `references/hino-city-hospital-access.md` for 日野市立病院 access details (if needed for reverse directions).

---
*Version: 1.0*
*Author: Hermes Agent (updated from session on 2026-07-08)*