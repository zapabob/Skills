---
name: release-notes
description: "Release notes. Turns merged commits into user-facing release notes grouped by feature, fix and breaking change."
disable-model-invocation: true
---

Turn the merged commits into release notes a user would understand.

Group by Feature, Fix, and Breaking change. Write for someone who uses the
product, not someone who wrote it: no commit hashes, no internal file names,
no "refactored X".

Omit anything with no user-visible effect. If nothing user-visible shipped,
say so in one line rather than padding.
