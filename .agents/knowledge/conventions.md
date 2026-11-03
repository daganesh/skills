# Conventions

## A skill folder
```
<skill>/
  SKILL.md      front matter (name, description) + instructions; description says when to trigger
  README.md     ≤ 20 lines: purpose, use-when, related skills (relative links), entry point
  references/   optional, loaded on demand by SKILL.md
  scripts/      optional helpers
```
`effort-estimator/` is the exception: scripts and a README, no `SKILL.md`.

## Adding a skill
1. Create `SKILL.md` and `README.md`.
2. Add a row to the root [README](../../README.md) and to [skill-map](skill-map.md).
3. Link it from the READMEs of skills it hands off to or reads from, and link back.

## Links
Relative links only, README to README for skill-to-skill, to a specific `references/` file when that file is the point. Keep READMEs short: detail belongs in `SKILL.md`.
