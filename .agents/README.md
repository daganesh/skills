# .agents: knowledge for agents working on this repo

This repo is a collection of Claude Code skills (markdown instructions, a few helper scripts). No build, no test suite. Read only the row you need.

## Topics
| File | Read when |
|---|---|
| [skill-map](knowledge/skill-map.md) | choosing a skill, or seeing how skills hand off to each other |
| [testing-skills](knowledge/testing-skills.md) | touching any of the 5 test-related skills (shared files, copies, file locations) |
| [conventions](knowledge/conventions.md) | adding or editing a skill, README or link |

## Components
No code components. The only scripts are [`usage-report/scripts/usage_report.py`](../usage-report/scripts/usage_report.py) and [`effort-estimator/`](../effort-estimator/README.md) (`estimate.py`, `analyze.py`).

## Skill folders
Each has a short `README.md` (purpose, when to use, links) and a `SKILL.md` (full instructions). Index: [../README.md](../README.md).

## Keeping knowledge up to date
When you add, rename, split or remove a skill, or change what it reads or writes, update in the same change: its `README.md`, the root [README](../README.md) table, [skill-map](knowledge/skill-map.md), and [testing-skills](knowledge/testing-skills.md) if it is test-related.
