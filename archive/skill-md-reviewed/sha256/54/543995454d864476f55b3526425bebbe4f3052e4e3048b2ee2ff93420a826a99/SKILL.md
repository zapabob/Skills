---
name: windows-home-network-diagnosis
description: Measure Windows home WAN before changing it.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, network, wifi, ipoe, bufferbloat]
    category: devops
---

# Windows Home Network Diagnosis

Measure first. Do not retune NIC, DNS, IPoE, or Wi-Fi channel until a labeled JSON probe shows where the path is actually slow.

## When to Use

自宅回線が遅い、体感が悪い、前後比較したい、IPoE/電波/HGWのどれか切り分けたいとき。

## How to Run

1. Baseline with a label, then change one thing, then re-run with a new label.
2. Script (stdlib, `py -3`): `scripts/standalone/net_home_probe.py --label <name>`
3. Compare `results/net_home_probe_<label>_latest.json`. Ignore older files if the summary has null ping/IPv6 after a parser miss.
4. Judge in this order: radio → last-mile/IPoE → CPE (HGW/router) → PC NIC/TCP.
5. Report three buckets: 実測 / 推測 / 未検証.

See `references/windows-probe-and-decision-tree.md`.

## Procedure

1. Run the probe. Do not skip IPv6, gateway ping, single vs 6-parallel download, or hop-1 traceroute.
2. If `netsh wlan show interfaces` says no wireless NIC, Wi-Fi channel and placement are 効果なし for that machine. Probe the slow device instead.
3. If global IPv6 + `flets-east.jp` (or similar) already exist, do not recommend "IPoE化" as if IPv6 is absent. IPv4 MAP-E vs leftover PPPoE is a separate, unverified question until the HGW UI is read.
4. If link is 1 Gbps, GW RTT is ~1–2 ms, and WAN is hundreds of Mbps, do not apply Windows TCP/NIC tweaks. The remaining lever is the HGW/ISP path.
5. NTT HGW is often `http://192.168.1.1` with HTTP Basic `realm=hgw-area`. Ask for the sticker username and password together. Do not spray `admin`/`user` guesses.

## Pitfalls

- `networkQuality` is macOS-only. On Windows use a loaded-latency RPM proxy only if the load transfer actually saturates (non-403, multi-second).
- Japanese `ping` is `時間 =8ms` (spaces). Japanese `nslookup` answers are under `Addresses:`.
- Prefer `ipconfig /all`, `route print`, and `netsh interface ipv6` over `Get-NetAdapter` for collectors.
- Ethernet MTU 1466 is consistent with IPoE/MAP-E overhead. Do not force 1500.
- Parallel download >> single flow is not proof the line is dead. It is a per-flow vs aggregate split.
- Do not write failed HGW logins or guessed passwords into skills or memory.
