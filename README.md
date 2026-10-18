# skills

Reusable [Claude Code](https://claude.com/claude-code) skills. Each folder is one skill with a `SKILL.md` (front matter `name` + `description`, then the instructions) and optional helper files.

## Skills

| Skill | What it does |
|---|---|
| [`create-feedback-form`](create-feedback-form/SKILL.md) | Adds an in-app feedback / bug-report form to a project. Asks where feedback goes (app DB, email, GitHub issue or other), types, severities, screenshot and system-info opt-outs, recipient/assignee/mention and button location, with defaults. Then builds the form, the issue model and storage, and delivery adapters. |
| [`create-knowledge-base`](create-knowledge-base/SKILL.md) | Sets up or refreshes a `.agents/` knowledge base so AI agents can orient in a repo without reading all the source. |
| [`delivery-pipeline`](delivery-pipeline/SKILL.md) | Works through a task backlog with a planner, implementer and reviewer agent, one PR per task. |
| [`project-design`](project-design/SKILL.md) | Takes a PRD and produces a detailed design plus implementation plan. Reviews the PRD, identifies the project type, lists the architecture decisions needed (platform, backend vs backendless, services, APIs, languages, data, auth, AI, testing, CI/CD), asks them one by one with a recommended option, then writes the design doc, decision log and task-table plan. Pre-loaded with recurring choices mined from past projects. |
| [`usage-report`](usage-report/SKILL.md) | Estimates Claude Code spend and active hours per project from local session transcripts. |

## Installing

Copy or symlink a skill folder into `~/.claude/skills/` (all projects) or `<project>/.claude/skills/` (one project):

```sh
cp -r create-feedback-form ~/.claude/skills/
```

Then invoke it by name (e.g. `/create-feedback-form`) or describe the task and let Claude pick it up from the skill's description.

## Adding a skill

Create `<skill-name>/SKILL.md` with `name` and `description` front matter, add any helper files next to it, and add a row to the table above.
