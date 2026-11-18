# Conventions

## Layout
```
.claude-plugin/marketplace.json   marketplace "daganesh-skills": lists the plugins
plugins/<family>/                 develop, test, usage
  .claude-plugin/plugin.json      name, version, description
  skills/<skill>/                 one folder per skill (below)
effort-estimator/                 standalone script, in no plugin
```
Skills are auto-discovered from `skills/`; installed, they are invoked as `/<family>:<skill>`.

## Versions
Each `plugin.json` has its own semver `version` (started at 0.1.0). Bump it in the same change as any edit to that plugin's skills, or installed users will not get the update. Keep `version` out of `marketplace.json` entries (`plugin.json` wins and the validator warns on a mismatch). Check with `claude plugin validate .` and `claude plugin validate plugins/<family>`.

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
1. Pick a family and create `plugins/<family>/skills/<skill>/` with `SKILL.md` and `README.md`. Bump that plugin's version.
2. Add a row to the root [README](../../README.md) and to [skill-map](skill-map.md).
3. Link it from the READMEs of skills it hands off to or reads from, and link back.

## Links
A skill's `SKILL.md` may only reference files in its own plugin (an installed plugin is copied on its own), so `../<other-skill>/` is fine within a family and never across families. READMEs may link across families (`../../../<family>/skills/<skill>/README.md`).

Relative links only, README to README for skill-to-skill, to a specific `references/` file when that file is the point. Keep READMEs short: detail belongs in `SKILL.md`.
