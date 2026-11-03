# skills

Reusable [Claude Code](https://claude.com/claude-code) skills. Each folder is one skill: a `README.md` (short summary and links) and a `SKILL.md` (front matter `name` + `description`, then the full instructions), plus optional `references/` and `scripts/`.

Agents: start with [`.agents/README.md`](.agents/README.md), read a skill's `README.md` first and its `SKILL.md` only when using it.

## Skills

**Build**
| Skill | What it does |
|---|---|
| [`project-design`](project-design/README.md) | PRD → design doc, decision log and task-table plan, via a one-decision-at-a-time interview. |
| [`delivery-pipeline`](delivery-pipeline/README.md) | Works a task backlog with planner, implementer and reviewer agents, one PR per task. |
| [`create-feedback-form`](create-feedback-form/README.md) | Adds an in-app feedback / bug-report form with storage and delivery. |

**Repo setup**
| Skill | What it does |
|---|---|
| [`create-knowledge-base`](create-knowledge-base/README.md) | Creates or refreshes a `.agents/` knowledge base so agents orient without reading all the source. |

**Testing** (they share vocabulary and files, see [testing-skills](.agents/knowledge/testing-skills.md))
| Skill | What it does |
|---|---|
| [`plan-tests-for-change`](plan-tests-for-change/README.md) | Decides which tests a change needs, at which level, in which file, with risk levels. |
| [`review-tests`](review-tests/README.md) | Audits an existing suite and opens prioritized GitHub issues. |
| [`manual-tests`](manual-tests/README.md) | Keeps and runs `.agents/manual-tests.md`, the list of human-checked behaviors. |
| [`test-run-report`](test-run-report/README.md) | Runs the suites and commits a comparable report per run. |

**Cost**
| Skill | What it does |
|---|---|
| [`usage-report`](usage-report/README.md) | Spend and active hours per project from local transcripts. |
| [`effort-estimator`](effort-estimator/README.md) | Script (not a skill): forecasts cost and time from your past sessions. |

How skills hand off to each other: [skill-map](.agents/knowledge/skill-map.md).

## Installing

Copy or symlink a skill folder into `~/.claude/skills/` (all projects) or `<project>/.claude/skills/` (one project). Install the testing skills together, since they reference each other's files.

```sh
cp -r create-feedback-form ~/.claude/skills/
```

Then invoke it by name (e.g. `/create-feedback-form`) or describe the task and let Claude pick it up from the skill's description.

## Adding a skill

See [conventions](.agents/knowledge/conventions.md).
