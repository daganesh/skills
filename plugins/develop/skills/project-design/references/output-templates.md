# Output templates

Scale to the project: a family game gets one file with short sections; a regulated service gets all three documents. Never pad. Use tables where the user's past docs did (decision tables, task tables, technology tables).

## 1. Design document (`docs/<project>-design.md`)

```
# <Project> - Design
Status: Draft | Approved   Date: YYYY-MM-DD   PRD: <path/link>   Decisions: <decisions file>

## 1. Summary
2-4 sentences: what it is, who for, shape of the solution.

## 2. Goals, non-goals, constraints
Goals / Non-goals / Hard constraints (budget, devices, languages, compliance, dependency approval).

## 3. PRD review findings
| # | Finding (contradiction / gap / flaw) | Resolution | Decision |

## 4. Architecture overview
Diagram (ASCII or mermaid): components, dependency direction, trust boundaries.
Layering rules + how enforced (e.g. tools/check_layers.py in CI).
Frontend/backend separation: what lives where; shared package.

## 5. Components and interfaces
| Component | Responsibility | Depends on (ports only) |
Ports table: | Port | Methods (summary) | Implementations | Fake | Contract test |

## 6. APIs
Internal: service facade (commands/results). External: REST/OpenAPI (resource table, versioning, errors, auth, pagination, idempotency). Third-party APIs consumed (auth, limits, cost, mock).

## 7. Data
Source of truth per datum; storage; schema + migrations; ids; retention; backup/export.

## 8. State and lifecycle
State machine diagrams/tables for each stateful entity; derived vs stored fields.

## 9. Security and privacy
AuthN/Z, server authority, secrets, key custody, data egress, abuse/moderation, scan gates.

## 10. Errors, concurrency, observability
Error taxonomy + shape; retry/timeout; consistency model and accepted races; logging, audit, support.

## 11. AI/LLM (if applicable)
Provider port, stub/mock, validation, reliability, safety, cost caps, human-in-the-loop.

## 12. Domain specifics
(Games: engine, rendering, rules core, assets, content, multiplayer, economy. Others: pipelines, workflows, schedulers.)

## 13. Technology
| Area | Choice | Why | Decision | Licence/maintenance check |
Dependencies kept minimal; list rejected libraries with reason.

## 14. Testing strategy
Levels per component, fakes, mock modes, acceptance bars, gates.

## 15. Delivery
Repo layout, CI jobs (blocks merge?), environments, deploy trigger, review gate, docs/KB rules.

## 16. Risks, spikes, deferred, open questions
Spikes: | Spike | Question | Done when | Blocks |
Deferred: | Item | Why not v1 | Re-entry point |
Open: | Q-n | Question | Recommendation | Resolved by (milestone) |
```

## 2. Decision log (`docs/<project>-decisions.md`)

One numbered, dated row per decision. Never silently rewrite; supersede explicitly.

```
### D-07  <Decision title>                              Status: Decided | Provisional | Open
Date: YYYY-MM-DD   Source: user | PRD | default (confirmed)   Supersedes/Refines: D-03
Question: <as asked>
Choice: <what we do>
Why: <driver: constraint / preference / evidence>
Rejected: <option> - <reason>; <option> - <reason>
Cost accepted / known limit: <what this costs us, when to revisit>
Consequences for the plan: <tasks, interfaces, tests affected>
```

Top of file: index table `| ID | Title | Status |`, then "Open questions" and "Closed during design review" lists.

## 3. Implementation plan (`docs/<project>-implementation-plan.md`)

```
# <Project> - Implementation plan
## Governing decisions
| Decision | Consequence for tasks |

## Technology (with source decision)  [short; points to design 13]

## Phase 0 - Foundation (serial, then FROZEN)
Scaffold + CI skeleton, domain models, ports + fakes, API contract (OpenAPI / types), mock mode, layer check, test harness, knowledge base skeleton.
Exit gate: <what must be green; test counts>.

## Phase 1..n
For each phase: goal, tracks (parallelisable), exit gate.

### Task table
| ID | Scope (one line) | Depends on | DoD (requirements / use cases / tests) | Test levels | Notes |
M1.1 ... ; spike tasks flagged "start first"; each milestone ends with an Acceptance task proving end-to-end reachability through the real interface.

## Waves
Wave 1: ...  Wave 2: ...  (topological order; parallel candidates)
Parallel tracks across phases; named sync points (fan-in tasks).

## Delivery process
Branching (from clean main, one PR per task ID, slices n/N), PR contents (task ID, decisions satisfied, tests added), CI job table:
| Job | Runs on | Blocks merge? |
Review gate, environments, deploy trigger, docs and `.agents/` updates in the same change set, CI-cost controls.

## Stop conditions for implementing agents
1. Unguessable blocking choice  2. New material ambiguity (log as open question)  3. A test failure implying the design is wrong  4. Conflict with a locked decision  5. Dependency failing licence/security/maintenance check.

## Verification per milestone
Concrete, observable acceptance bars (commands, screens, numbers).

## Coverage map
| PRD requirement | Design section | Task IDs |   (no row may be empty)
```

Task rules: one reviewable PR each; self-contained and testable; DoD names the tests; test levels declared; no forward dependencies; large features sliced `n/N`; every component has a wiring/integration task; no `NotImplementedError` branches left behind.

## 4. Question card (what to send with AskUserQuestion)

```
header: <=12 chars e.g. "Backend"
question: "<Decision as a question, unmistakable, one decision only>?"
options:
  1. "<Recommended option> (Recommended)" - consequence + cost, 1 line; why recommended (constraint/preference)
  2. "<Alternative>" - consequence + cost
  3. "<Alternative>" - consequence + cost
(optional preview: tiny diagram / layout)
```
Record immediately as D-n. "No preference" => recommended.
