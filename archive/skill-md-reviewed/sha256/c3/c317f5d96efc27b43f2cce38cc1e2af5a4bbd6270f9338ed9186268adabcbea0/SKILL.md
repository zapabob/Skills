---
name: workflow-skill
description: Use when distilling workflow steps into reusable skill.!!.
category: productivity
---

1. **Branch creation**
   `git fetch origin && git checkout main && git pull origin main && git checkout -b feat/<short-description>`

2. **Commit**
   `git add <files>`
   `git commit -m "type(scope): short description

- bullet points"`

3. **Push**
   `git push -u origin HEAD`

4. **Create PR**
   `cat > /tmp/pr-body.md <<'EOF'`
   `## Summary`
   `- ...`
   `## Test plan`
   `- [ ] ...`
   `EOF`
   `gh pr create --title "<title>" --body-file /tmp/pr-body.md`

5. **Monitor CI**
   `gh pr checks --watch` or poll with curl.

## Pitfalls

- Use `--body-file` for PR bodies with quotes or backticks.
- Abort cherry-pick on conflicts; copy only intended paths.
- Follow branch naming conventions (`type/description`).

## Verification

- Test in a dry‑run repo.
- Ensure description matches trigger phrase exactly.
- Verify all commands work in target environment.