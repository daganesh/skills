# Versioning the plugins

Each plugin carries its own semver `version` in `plugins/<family>/.claude-plugin/plugin.json` (`develop`, `test`, `usage`; all started at 0.1.0). Installed users only receive a change when that version changes, so an edit without a bump never reaches them.

## When to bump
Bump in the same commit or PR as the change, only for the plugin(s) whose files changed:

| Change in the plugin | Bump | Example |
|---|---|---|
| Typo, wording, link fix, README-only edit | patch | 0.1.0 → 0.1.1 |
| New skill, new instructions or behavior, new `references/` or `scripts/` file, a compatible change to what a skill reads or writes | minor | 0.1.1 → 0.2.0 |
| Skill removed or renamed (its `/<family>:<skill>` name changes), or files it writes in a target repo change incompatibly | major (minor while below 1.0.0) | 0.2.0 → 0.3.0 |

- Several changes in one PR: one bump, the highest level needed.
- A skill moved between plugins: bump both, the one losing it as a removal.
- Not a plugin change, so no bump: root `README.md`, `.agents/`, `effort-estimator/`, `marketplace.json` descriptions.
- A new plugin starts at 0.1.0 and gets an entry in `.claude-plugin/marketplace.json`.

## Rules
- `version` lives only in `plugin.json`. Keep it out of the `marketplace.json` entries: `plugin.json` wins at install time and the validator warns on a mismatch.
- Never reuse or lower a version.

## Checking
```sh
git diff --name-only origin/main -- plugins/ | cut -d/ -f2 | sort -u   # plugins that need a bump
claude plugin validate .
claude plugin validate plugins/<family>
```

Users pick up new versions with `/plugin marketplace update daganesh-skills`.
