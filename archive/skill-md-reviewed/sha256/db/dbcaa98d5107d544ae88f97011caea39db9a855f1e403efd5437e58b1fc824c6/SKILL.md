---
name: questframe-036-dibr-lab-goal
description: Orchestrate QuestFrame v0.36 DIBR/6DoF integration lab (MAM-51-08/09) with max parallel subagents, evidence packs, claim boundaries, and multi-game profiles (FH6, AC7, AC8 planned). Use when user invokes /goal for 0.36, MAM-83/84, DIBR lab, or PC Ace Combat 7/8 extensibility.
---

# QuestFrame 0.36 DIBR / 6DoF Lab Goal Orchestrator

## When to use

- User says `/goal: 0.36`, `MAM-83`, `MAM-84`, `MAM-51-08`, `MAM-51-09`, DIBR lab, 6DoF cockpit schema
- Extending PCVR lab beyond FH6 to **ACE COMBAT 7** (active) and **AC8** (planned)
- Re-running multitask evidence with parallel subagents

## Linear ID map

| User alias | Canonical | Slice |
|------------|-----------|-------|
| MAM-83 (informal) | **MAM-51-08** | DIBR 72Hz lab gate |
| MAM-84 (informal) | **MAM-51-09** | 6DoF cockpit pose schema |
| Parent | **MAM-51** | QuestFrame productization |

## Claim boundary (never regress)

**May claim:** DIBR fixture/offline lab Pass; 6DoF pose fields in reports; HMD diagnostic at 72Hz lab baseline; game profile registry (fh6/ac7/ac8).

**Must NOT claim:** Playable FH6VR/AC7VR; live in-game D3D12 depth without proof; `ReadyForInGameDriving=true`; 120Hz shipped safe profile.

## Game profiles

| Slug | Title | Steam | Process | Lab ready |
|------|-------|-------|---------|-----------|
| `fh6` | Forza Horizon 6 | 2483190 | forzahorizon6 | yes |
| `ac7` | ACE COMBAT 7 | 502500 | Ace7Game | yes |
| `ac8` | ACE COMBAT 8 | TBD | TBD | schema only |

CLI: `FH6VR.Launcher.exe game-profiles --json --probe`

Code: `PcvrGameProfileRegistry`, `PcvrGameProcessMatch`

## Evidence pack (primary)

```powershell
cd work\fh6vr
dotnet build src\FH6VR.Launcher\FH6VR.Launcher.csproj -c Release

# Offline lab (no HMD required)
.\scripts\Invoke-Quest2VdDibrLabEvidencePack.ps1 -GameProfile fh6 -AllowMissingRuntime

# Live Quest2+VD 72Hz lab
.\scripts\Invoke-Quest2VdDibrLabEvidencePack.ps1 -GameProfile fh6 -RequireHmd -AttemptWindowCapture

# AC7 profile (game running, non-invasive)
.\scripts\Invoke-Quest2VdDibrLabEvidencePack.ps1 -GameProfile ac7 -AttemptWindowCapture
```

Session tag: `quest2-vd-dibr-0.36-{slug}_yyyyMMdd-HHmmss`
Schema: `0.36`
Manifest: `artifacts/evidence/sessions/.../env/session-manifest.json`

## Multitask subagent split (max parallel)

Launch **in parallel** when safe (no duplicate HMD grabs):

1. **docs** — `docs/EVIDENCE_SCHEMA_0.36.md`, `docs/LIVE_SESSION_DIBR_LAB_0.36.md`, `docs/GAME_PROFILES.md`
2. **code** — game profile registry, tests, `game-profiles` CLI
3. **script** — `Invoke-Quest2VdDibrLabEvidencePack.ps1`
4. **offline-lab** — run pack with `-AllowMissingRuntime`; capture session id
5. **live-lab** — VD 72Hz, HMD connected; run without `-AllowMissingRuntime`
6. **trackers** — GitHub #15 comment draft, Linear MAM-51-08/09 status, `outputs/GOAL_STATUS_0.36_*.md`
7. **version** — bump `AppVersion` to `0.36.0-dev`, `RELEASE_NOTES.md` after lab Pass gates met

**Serialize** OpenXR + foreground game capture if simultaneous instance errors occur.

## Verification gates (0.36)

| Gate | Command / artifact | Pass signal |
|------|-------------------|-------------|
| DIBR lab | `dibr-selftest --json` | Status Pass |
| RTX3060 budget | `rtx3060-selftest --json` | Status Pass |
| Swapchain DIBR | `dibr-swapchain-selftest --json` | Status Pass |
| 6DoF schema | `cockpit-presence-selftest --approve --target-hz 72` | SixDof fields present |
| Game profiles | `game-profiles --json --probe` | fh6+ac7 labReady true |
| Unit tests | `dotnet test -c Release` | all Pass |

## Implementation log

After substantive work:

- Path: `work/fh6vr/_docs/YYYY-MM-DD_mam-51-08-036-dibr-lab_6-quest2-vr.md`
- Style: なんJ風 + CoT仮説検証
- Play on completion: `%USERPROFILE%\Desktop\SO8T\.cursor\marisa_owattaze.wav`

## Prior slices (context)

- 0.34 MAM-78: 72Hz HMD Pass
- MAM-80: 90Hz candidate Pass
- 0.35 MAM-81: FH6 foreground Pass

## Examples

**User:** `/goal: 0.36 DIBR lab, AC7 too, skill化`

1. Read this skill + `docs/ROADMAP_0.33_0.36.md`
2. Launch parallel subagents (docs, code, offline-lab, trackers)
3. Run offline lab; then live lab if HMD available
4. Write GOAL_STATUS + implementation log + completion sound

## Performance notes

- Prefer Release launcher auto-detect in scripts (newest `FH6VR.Launcher.exe` under `bin/Release`)
- DIBR selftests are CPU/GPU light; OpenXR steps dominate latency
- Do not run two OpenXR selftests concurrently

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Empty launcher stdout | Script synthesizes Fail JSON; rebuild Release |
| openxr exit 2 without HMD | Use `-AllowMissingRuntime` for offline lab only |
| AC7 process not found | Launch AC7; verify process `Ace7Game` via `game-profiles --probe` |
| MAM-83 vs MAM-51-08 confusion | Use MAM-51-08 in Linear; note user alias in comments |
