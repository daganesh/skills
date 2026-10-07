---
name: create-knowledge-base
description: Set up or update a .agents/ knowledge base in a repository so AI coding agents can understand the codebase without reading all source files upfront — covering both semantic concepts (architecture, testing, api, etc.) and the significant, high-influence code components (core classes/modules that anchor most of the codebase). Use when onboarding a repo (or a folder of repos) to an agent-friendly workflow, or when refreshing/verifying one that already exists. Language- and tool-agnostic.
---

You are setting up (or updating) a `.agents/` knowledge base so that AI coding agents — and humans — can orient in a codebase quickly, by reading a small curated index first instead of crawling every source file. The knowledge base has two complementary layers: **semantic/topic files** (architecture, testing, api, auth, …) and **component files** (the specific classes/modules that form the codebase's backbone). Neither layer alone is enough: topic files give the map, component files give agents a precise, verified foothold in the actual code, and the links between the two are what let an agent find "just enough" context fast instead of either guessing or reading everything. Work through the setup questions, then follow the steps in order.

## Step 0 — Setup questions (ask before doing anything)

Confirm the following with the user before making changes. Use sensible defaults where the answer is obvious from the environment, but surface them.

1. **Fresh setup or update?** — Check whether `.agents/knowledge/` already exists. If it does, default to **update mode** (see "Updating an existing knowledge base" below): verify and patch what's there, add what's missing, don't blindly regenerate. If it doesn't exist, this is a fresh **create mode** run of the full Steps 1–8. Surface which mode you're in before proceeding.
2. **Target scope** — A single repository (the current working directory), or a folder containing multiple repositories? If multiple, which ones (all sub-folders that contain a VCS root, or an explicit list)? For a multi-repo run, repeat Steps 1–8 per repo.
3. **Coding agents to support** — Which agents will read this knowledge base? For each selected agent, create the matching root pointer file (see table below) that links to `.agents/README.md`. Default: detect existing agent files in the repo and match them; if none, ask.
4. **Version control & PR flow** — Is this a Git repo? What is the default/integration branch to target (`main`, `master`, `dev`, …)? Should changes go on a feature branch + pull request, or be committed directly? Is there a hosted remote (GitHub/GitLab/Bitbucket/other) and a CLI/MCP available to open a PR?
5. **Depth** — Minimal (architecture + dev-environment + testing only, no dedicated component files) or full (topic files plus dedicated component files for the codebase's foundational classes/modules — recommended, and the default for any repo past trivial size)?
6. **Existing docs** — Should existing `CLAUDE.md` / `AGENTS.md` / `.github/copilot-instructions.md` / `.cursor/rules` be replaced with pointers, or left untouched and merely referenced?
7. **External documentation resources (optional)** — Are there authoritative docs outside the source tree that should inform the knowledge base? For example: a design system, architecture RFCs/ADRs, an API spec (OpenAPI/GraphQL), a style guide, product/PRD docs, or a runbook. Accept any of: a local path/folder, a URL, or a connected source (Notion, Confluence, Google Drive, etc. — use the matching MCP tool if available). Note which are the source of truth for their topic.

### Agent → root pointer file

| Agent | Root file to create/point | 
|-------|---------------------------|
| Claude Code / Claude | `CLAUDE.md` |
| OpenAI Codex / generic | `AGENTS.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Cursor | `.cursor/rules/` (or `.cursorrules`) |
| Gemini CLI | `GEMINI.md` |
| Windsurf | `.windsurfrules` |

Each root file stays short (≤ 10 lines) and just points to `.agents/README.md`. This keeps a single source of truth and avoids duplicated, drifting instructions per tool.

## Updating an existing knowledge base

If `.agents/knowledge/` already exists, this is a verify-and-patch pass, not a rewrite. Treat every existing file as a claim to check, not ground truth to preserve blindly:

1. **Read everything first.** Read `.agents/README.md` and every file under `knowledge/` and `skills/` before touching anything, so you know what's already claimed and how it's cross-linked.
2. **Verify facts against current source.** For every file path, line number, class/method name, and code snippet a knowledge file cites, re-check it against the actual repo (`grep`/`Read`, not memory). Line numbers drift constantly as files change — treat a stale line number as a bug to fix, not a rounding error.
3. **Patch, don't regenerate.** Fix only what's stale, wrong, or missing. Preserve the existing structure, section order, and voice of files that are still accurate — a full rewrite destroys hand-tuned phrasing and cross-links for no benefit.
4. **Diff the component inventory.** Run the foundational-component identification (Step 1c below) and compare it against what already has a dedicated component file. Components newly grown into significance (more fan-in, more code) get a new file; components that shrank or were removed get their file trimmed or deleted; everything else just gets its facts re-verified.
5. **Reconcile cross-links both ways.** When you add or rename a component file, update every topic file that should link to it, and make sure the component file links back to the topic files and sibling components it relates to (see "Cross-linking" in Step 4b). A component file with zero inbound links from topic files is a sign the graph is incomplete, not that the component is unimportant.
6. **Update the README index** for anything added, renamed, or removed — stale index entries are worse than no index.

## Structure to create

```
.agents/
├── README.md                ← index file (agents read this first)
├── knowledge/
│   ├── architecture.md      ← repo structure, key entry points, core modules
│   ├── dev-environment.md   ← build, run, test commands and gotchas
│   ├── testing.md           ← test framework, where tests live, how to run
│   ├── <topic>.md           ← repo-specific concept (api, auth, db, deploy, etc.)
│   └── <component>.md       ← repo-specific foundational class/module (see Step 1c)
└── skills/
    ├── bug-fix.md           ← step-by-step bug fix workflow
    ├── new-feature.md       ← feature development workflow
    └── write-test.md        ← test writing workflow
```

Component files live alongside topic files in `knowledge/` — same folder, same naming convention (kebab-case, one concept per file) — they are distinguished in `README.md`'s index by which table they're listed in (see Step 3), not by a separate folder.

## Step 1 — Explore the repo

Read any existing agent/instruction files (`CLAUDE.md`, `AGENTS.md`, `README.md`, `.github/copilot-instructions.md`, `CONTRIBUTING.md`) and the top-level directory layout. Detect the stack from manifest files (`package.json`, `pyproject.toml`/`requirements.txt`, `go.mod`, `Cargo.toml`, `pom.xml`/`build.gradle`, `Gemfile`, `composer.json`, etc.) so the knowledge files reflect the real tooling rather than assumptions.

## Step 1b — Ingest external documentation (only if provided in Step 0)

For each external resource the user named:

1. **Read it** via the appropriate tool — local file (`Read`), URL (web fetch), or a connected source (e.g. `mcp__notion__*`, Confluence, Drive MCP).
2. **Distill, don't dump.** Extract the facts, conventions, and constraints an agent needs (naming rules, design tokens, API contracts, architectural decisions and their rationale). Do not copy whole pages into the repo — summarize and **link back to the source** so the doc stays the source of truth.
3. **Record provenance.** In the relevant knowledge file, note where each externally-sourced fact came from and when it was read (e.g. `Source: Design System (Notion), read 2026-07-02`). This lets a reader tell verified-from-code facts from doc-derived ones and re-check when the external doc changes.
4. **Route to the right file.** A design system → a `design-system.md` (or the `<topic>.md` it fits); an API spec → `api.md`; ADRs/RFCs → `architecture.md`. Where an external doc and the code disagree, prefer the code and flag the discrepancy for the user.

## Step 1c — Identify foundational components

Semantic topic files (architecture, api, testing…) tell an agent *what kind* of thing it's looking for. Component files tell it *exactly where* — a specific class or module, verified against the source, with real line numbers. The goal is a small set of high-leverage component files, not one file per class: pick the handful of classes/modules whose influence covers most of the code span, so that reading their file plus the topic file gets an agent to "enough context" fast without reading everything.

A component is worth its own file if it's a genuine architectural anchor — evaluate candidates against these signals, in rough order of strength:

1. **Named in the data/control flow.** If the architecture overview already draws a flow like `A → B → C`, every node in that diagram is a strong candidate — including ones that only got a one-line mention and no dedicated file (that gap is exactly what this step exists to close).
2. **High fan-in.** Grep how many other files import or instantiate it (`grep -rl "import <Name>\|from .* import <Name>"`, or the language equivalent). A class referenced from a dozen call sites across multiple modules is load-bearing; a class used in one file is not — however important that one file is. Score every named entry point this way, even ones a topic file already discusses — fan-in is a property of the code, not of the docs, and the highest-fan-in class in the repo is disqualified by nothing.
3. **Orchestrator / wrapper / entry-point role.** Classes that construct or delegate to several other core classes (an `Explainer`-, `Delegator`-, `Manager`-, `Wrapper`-, `Client`-, or `Runner`-style class) tend to be the seams an agent needs to understand before changing anything nearby. The main SDK/library entry point a user directly instantiates is almost always in this category, however "obvious" or already-named it seems.
4. **Size and surface area.** A file that's large (hundreds+ lines) or exposes many public methods usually can't be summarized adequately in a shared topic file's margins — it needs its own space, or its summary elsewhere will silently go stale or shallow.
5. **Cross-repo or cross-package reach.** A class imported from another package/repo in the same system (a shared client, protocol wrapper, or SDK surface) gets its own file — even a short one — whenever it has any material in-repo usage, because it's a contract other code depends on and agents look it up by name, not by which topic file happens to mention it. Treat this as a requirement, not a nice-to-have: a two-paragraph file that clearly says "this is external, here's how this repo uses it, here's where the source of truth for its internals lives" beats a buried paragraph inside a topic file every time.

Build the candidate list by combining what's already named in existing architecture/entry-point docs with a fan-in sweep of the codebase. Two scoping mistakes will each quietly produce an incomplete list, so guard against both explicitly:

- **Don't stop at fan-in alone for candidates outside the named entry points.** It's tempting to run a cheap fan-in grep across the repo, and then dismiss anything below the fan-in of the headline classes with a comparative one-liner ("doesn't rival X, no dedicated file needed") without ever checking its size or role. That comparison is a category error: a class can lose on fan-in and still win outright on signal 3 (orchestrator role) or signal 4 (size/surface area) — a large, complex, low-fan-in algorithm class (e.g. something instantiated from exactly one call site but running to hundreds of lines with dozens of methods) clears the bar on size alone. Score every candidate that clears *any one* signal against *all five* signals before dismissing it — a single unfavorable number (fan-in) is not a verdict.
- **Sweep every top-level source package/module in the repo, not just the one the architecture doc already focuses on.** A repo with multiple packages (e.g. a core library plus a utils/testing package, or multiple services in a monorepo) needs the fan-in sweep run separately per package. It's easy for a sweep to implicitly scope itself to whichever package the existing architecture.md already centers on and never touch the others — enumerate the top-level packages first (from the directory layout / Step 1's stack detection) and confirm each one was actually swept before treating the candidate list as complete.

Score every candidate against the signals above **before** looking at how it's currently documented — scoring first, then checking existing coverage, keeps a strong candidate from being waved through just because it already has some words written about it somewhere. If a sweep was delegated to a subagent (recommended for a large repo, to protect main-context budget), verify it actually enumerated classes across every package and scored non-headline candidates on more than fan-in — a subagent under-scoping the same way is the same failure, one level removed.

**Anti-pattern to watch for**: "it's already mentioned in `api.md`/`communication.md`/etc." is not the same claim as "it already has a dedicated component file." An inline mention inside a topic file is frequently *how* a foundational component ends up under-documented — being folded into someone else's file is the symptom this step exists to fix, not evidence the component is already handled. Before deciding a high-scoring candidate doesn't need its own file, check literally: does `knowledge/<component>.md` exist for this exact class? If not, "it's mentioned elsewhere" is not a reason to skip it.

Then prune the low scorers: drop candidates that only ever hit signal 4 weakly and nothing else — a small helper class fully described by one bullet in `api.md`, with low fan-in, not named in the flow diagram, not an orchestrator, no cross-repo reach — that one legitimately doesn't need to fork into its own file (resist one-file-per-class). Pruning is for candidates that score low across the board, not for candidates that score high but happen to already live inside a topic file.

Keep the survivors — typically single digits to a couple dozen even for a large repo — as the component list for Step 4b. When updating an existing knowledge base, diff this list against components that already have a file (see "Updating an existing knowledge base" above) instead of starting over.

**Final gate**: if the user (or any brief/spec for this task) named specific classes or concepts they expect to see, check each one resolves to its own `knowledge/<name>.md` before calling the pass done — a name that only resolves to a mention inside another file is a gap, not a different valid interpretation. Don't silently reinterpret "give X its own file" as "make sure X is mentioned somewhere."

## Step 2 — Create directory structure

```bash
mkdir -p .agents/knowledge .agents/skills
```

## Step 3 — Write `.agents/README.md`

Include:
1. One-line repo description
2. Table of all **concept/topic** knowledge files with descriptions (architecture, dev-environment, testing, api, auth, …)
3. A separate table of all **component** knowledge files (see Step 1c / 4b), each with the class/module it covers and a one-line purpose — this is what makes the component layer discoverable rather than buried
4. Table of all skill files with when-to-use
5. A "Keeping knowledge up to date" section — instruct agents to update the relevant knowledge file (topic *or* component) in the same change set whenever they alter architecture, public APIs, the dev workflow, or a documented component's interface/behavior. Explicitly call out: if a change touches a class that has a component file, that file must be checked for drift, not just the topic file.

## Step 4a — Write concept/topic knowledge files

Keep each file **20–60 lines**, focused, referencing real file paths from the repo.

| File | Must cover |
|------|-----------|
| `architecture.md` | Directory structure, key entry points, core modules, external dependencies — and a link to each component file for anything named in the flow/entry-points list |
| `dev-environment.md` | Prerequisites, env vars, how to install/run/build, common gotchas |
| `testing.md` | Framework + version, where tests live, how to run (single test + full suite), required setup |
| `<topic>.md` | Repo-specific as needed (api, auth, db, state, build-system, deploy, ci, etc.) |

Topic files stay high-level: they describe *categories* and link out to component files for depth, rather than re-describing a component's methods inline (that description belongs in exactly one place — the component file — so it can't drift out of sync in two places).

## Step 4b — Write component knowledge files

For each survivor from Step 1c, create (or update) `knowledge/<component-kebab-case>.md`. Unlike topic files, these are anchored to one class/module and must be verified against the source, not summarized from memory:

- **Location**: exact file path and the line the class/def starts at (re-grep this — don't trust a number carried over from a previous pass).
- **Purpose**: one or two sentences — what this component *is* and the role it plays in the flow named in `architecture.md`.
- **Construction**: constructor/init signature or key factory, and who constructs it (which other component or entry point).
- **Key surface**: the methods/properties another engineer or agent would actually need to call or override, each with a line number and a short purpose — not every method, just the public surface that matters. For very large classes (hundreds of methods), group by responsibility rather than listing exhaustively.
- **Relationships / cross-links** (this is what makes the knowledge graph rich, not just wide): explicitly link to
  - the topic file(s) it's an instance of (e.g. a wrapper class links back to its `architecture.md` flow entry)
  - sibling component files it constructs, is constructed by, or hands data to/from
  - the topic file(s) that exercise it (e.g. `testing.md` if there's a dedicated fixture/mock for it)
  A component file with no outbound links is almost certainly missing context an agent will need next; a component with no inbound links from any topic file means the topic files aren't surfacing it — fix whichever side is missing.
- Length is guidance, not a hard cap: a small wrapper might be 15 lines; a genuinely central class with a wide public surface can run longer — but stay curated (group and link) rather than dumping every method signature.

## Step 5 — Write skill files

Each skill file: numbered steps, exact commands for *this* repo's tooling, minimal prose.
Start with `bug-fix.md`, `new-feature.md`, `write-test.md`; add more (e.g. `release.md`, `migration.md`) if the repo's workflow warrants it.

## Step 6 — Write root pointer files

For each agent chosen in Step 0, create/replace its root file with a short pointer. Example for `CLAUDE.md` / `AGENTS.md`:

```markdown
# <Repo Name>
<One-line description.>

## Codebase knowledge
See `.agents/README.md` for architecture, APIs, patterns, and dev environment.

## Task workflows
See `.agents/README.md` for step-by-step skill guides.
```

For `.github/copilot-instructions.md`, `.cursor/rules`, etc., write the equivalent short pointer in that file's expected format. If any pointer target is listed in `.gitignore`, either un-ignore it or note that the agent must read `.agents/README.md` directly.

## Step 7 — Commit and (optionally) open a PR

Only if the repo uses version control and the user opted for it. Use the repo's actual default branch and remote:

```bash
git checkout -b feat/agent-knowledge-base
git add .agents/ CLAUDE.md AGENTS.md .github/copilot-instructions.md .gitignore
git commit -m "feat: add .agents/ knowledge base for AI coding agents"
git push -u origin feat/agent-knowledge-base
# Open a PR with whatever CLI/MCP is available, targeting the integration branch:
# gh pr create --title "feat: add .agents/ knowledge base" --base <default-branch>
```

If there is no remote or PR flow, stop after the commit.

## Done when

- [ ] Setup questions answered; scope, target agents, and fresh-vs-update mode confirmed
- [ ] Each chosen agent has a root pointer file (≤ 10 lines) pointing to `.agents/README.md`
- [ ] `.agents/README.md` has a complete index (topic table **and** component table) + "Keeping knowledge up to date" section
- [ ] Foundational, high-influence components identified (Step 1c) and each has an accurate, source-verified component file (Step 4b) — including any named in the flow diagram or explicitly expected by the user, even if they were already mentioned inline in a topic file beforehand
- [ ] Component files and topic files cross-link both ways — no component file is an orphan with zero inbound links, no topic file silently duplicates a component's internals
- [ ] Knowledge files are concise and reference real paths and line numbers that were just re-verified against the source
- [ ] If updating an existing base: stale facts (paths, line numbers, renamed/removed methods) were corrected, not left in place; unchanged-and-accurate files were left alone rather than rewritten
- [ ] Any external docs distilled (not copied), linked back, and provenance recorded
- [ ] Skill files have numbered steps with exact, repo-correct commands
- [ ] (If applicable) changes committed / PR opened against the right branch
