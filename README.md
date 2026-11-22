# skills

Reusable [Claude Code](https://claude.com/claude-code) skills. Skills live in `plugins/<family>/skills/<skill>/`. Each skill folder has a `README.md` (short summary and links) and a `SKILL.md` (front matter `name` + `description`, then the full instructions), plus optional `references/` and `scripts/`.

Agents: start with [`.agents/README.md`](.agents/README.md), read a skill's `README.md` first and its `SKILL.md` only when using it.

## Skills

**Build**
| Skill | What it does |
|---|---|
| [`project-design`](plugins/develop/skills/project-design/README.md) | PRD → design doc, decision log and task-table plan, via a one-decision-at-a-time interview. |
| [`delivery-pipeline`](plugins/develop/skills/delivery-pipeline/README.md) | Works a task backlog with designer, test-builder, implementer and reviewer agents (tests and code built in parallel), one PR per task. |
| [`create-feedback-form`](plugins/develop/skills/create-feedback-form/README.md) | Adds an in-app feedback / bug-report form with storage and delivery. |

**Repo setup**
| Skill | What it does |
|---|---|
| [`create-knowledge-base`](plugins/develop/skills/create-knowledge-base/README.md) | Creates or refreshes a `.agents/` knowledge base so agents orient without reading all the source. |

**Testing** (they share vocabulary and files, see [testing-skills](.agents/knowledge/testing-skills.md))
| Skill | What it does |
|---|---|
| [`plan-tests-for-change`](plugins/test/skills/plan-tests-for-change/README.md) | Decides which tests a change needs, at which level, in which file, with risk levels. |
| [`review-tests`](plugins/test/skills/review-tests/README.md) | Audits an existing suite and opens prioritized GitHub issues. |
| [`manual-tests`](plugins/test/skills/manual-tests/README.md) | Keeps and runs `.agents/manual-tests.md`, the list of human-checked behaviors. |
| [`test-run-report`](plugins/test/skills/test-run-report/README.md) | Runs the suites and commits a comparable report per run. |

**Cost**
| Skill | What it does |
|---|---|
| [`usage-report`](plugins/usage/skills/usage-report/README.md) | Spend and active hours per project from local transcripts. |
| [`effort-estimator`](effort-estimator/README.md) | Script (not a skill): forecasts cost and time from your past sessions. |

How skills hand off to each other: [skill-map](.agents/knowledge/skill-map.md).

## Installing

The repo is a Claude Code plugin marketplace (`daganesh-skills`) with three plugins:

| Plugin | Skills |
|---|---|
| `develop` | project-design, delivery-pipeline, create-feedback-form, create-knowledge-base |
| `test` | plan-tests-for-change, review-tests, manual-tests, test-run-report |
| `usage` | usage-report |

In Claude Code:

```
/plugin marketplace add daganesh/skills
/plugin install test@daganesh-skills
```

Or from a shell (`--scope project` shares it with the team through `.claude/settings.json`):

```sh
claude plugin marketplace add daganesh/skills
claude plugin install develop@daganesh-skills --scope user
```

Plugin skills are namespaced: `/test:review-tests`, `/develop:project-design`. Claude also picks them up from their descriptions. Run `/plugin marketplace update daganesh-skills` to get new versions.

**Without plugins:** copy a skill folder into `~/.claude/skills/` (all projects) or `<project>/.claude/skills/` (one project). Copy all four test skills together, because `manual-tests` and `test-run-report` read `review-tests/references/test-strategy.md`.

```sh
cp -r plugins/develop/skills/create-feedback-form ~/.claude/skills/
```

`effort-estimator/` is a standalone script, not part of any plugin: run it from a clone.

## Adding a skill

See [conventions](.agents/knowledge/conventions.md).
