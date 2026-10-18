# House preferences (the user's recurring design, architecture and implementation choices)

Mined from the user's own projects and sessions: mico, light-eqms, bisly, monsort, irri-vision, find-the-photos, weddinvaders, iso-top, bruxism-tracker, ClearClaim, Word_guess. Use these as the **recommended option** in questions and as the **assumed defaults**. They are defaults, not laws: a project's constraints win (monsort is deliberately backendless; bisly deliberately has a server). Always say which preference drove a recommendation, and record deviations as decisions.

Evidence tags in brackets name the project where it was observed.

## 1. Architecture

1. **Interface (port) first for everything volatile.** Every external service, storage, LLM, engine, scheduler, notification channel is a narrow interface (Protocol/ABC/TS interface) with at least one **fake** and a **contract test** run against every implementation. The app layer imports interfaces and models only; composition roots are the only place naming concrete implementations. [eqms E2, mico AD-04, bisly ISimulationEngine, monsort INetworkAdapter/ITopicGenerator/LLMProvider, irri stage ABCs, iso-top repositories/LLMFallback]
   - Justify abstractions by **testability and replaceability**, not by promising a vendor swap. mico's "swap storage with zero changes" claim was called dishonest; the bar became "the pipeline is green against an in-memory fake".
   - Keep ports narrow (about 12 primitives beat per-aggregate repositories; mico) and evolve them additively. Interfaces and models are **frozen after Phase 0**; later changes are deliberate and logged.
2. **API/service-first, thin UIs.** One service facade with command/result objects is the only thing UIs call. REST (OpenAPI) is a thin binding with no logic; CLI and web have parity (a parity gap is a bug). Shared pure logic and API contracts live in a shared package so client and server cannot drift. Generate client types from the OpenAPI spec. [mico AD-06, find-the-photos `shared`, irri generated types, iso-top OpenAPI-first]
3. **Pure/headless core.** Domain rules live in a module with zero UI/DOM/framework imports (game engine, pipeline library, `shared/logic`), driven by UI, bots, CLI and tests alike. [bisly GameSession, monsort `engine/`, find-the-photos, mico]
4. **Encapsulation = self-contained classes/components with one responsibility, not microservices.** A service depends on ports and the store, never on another service's internals. "As different classes/components. I don't mean standalone microservices." Persistence is owned by the service layer so routes cannot forget it. [eqms E28/E46]
5. **Layering enforced mechanically**, not by convention: an import-lint test or ~100-line AST script in CI plus a test that the real tree is clean. Direction is one-way (ui -> logic -> brain/infra; app never imports infra). [mico check_layers, eqms import-lint]
6. **Right-size.** Modular monolith over services. One customer / one catalog / small team => no multi-tenancy, no DB until needed, no lock service, optimistic concurrency with a documented accepted race. Prepare the seam (UUID keys, owner_id defaulted to a local user, repository interface) and don't build it. [irri, iso-top D31, eqms, bisly]
7. **Backendless/low-ops first.** If the product can be a static PWA/page with local state, prefer it (GitHub Pages, single-file HTML). BYOK for AI keys, memory-only by default, opt-in "remember". When a server is unavoidable: scale-to-zero serverless container + object storage with **no DB at first** (irri), or a Node/Python modular monolith with SQLite (bisly) / Postgres on Railway (find-the-photos). [monsort, weddinvaders, Word_guess]
8. **Local-first / privacy by design** for personal, medical and document tools: sensitive text stays on the device, minimal metadata in the cloud, LLM opt-in and off by default with an explicit "leaves this device" notice, keys in the OS keychain. [iso-top, bruxism, mico, eqms]
9. **Server authority.** The server owns prices, rewards, validation, ownership and rate limits; the client is never trusted for state. New routes are private by default. [bisly review, find-the-photos IDOR fixes, eqms E58]
10. **Source of truth stated for every datum**; the rest is derived or disposable and can be rebuilt (`reindex`). Derived values (e.g. `late`) are computed, never stored. Prefer **idempotent, state-derived, reconcile-style** designs and **append-only** histories over event emission and in-place mutation. Persisted state machines with explicit parked and terminal states. [mico, eqms]
11. **Additive evolution.** Add fields/ports/modules; old rows load with defaults; separate display formatting from stored values so recovery keys survive. If breaking is allowed (pre-live), say so and state whether the user must restart tests.
12. **Hide, don't delete** features awaiting review (one admin flag); remove only truly dead code together with its tests, docs and deps. [eqms E67]
13. **Customer-contradicts-decision => opt-in alternative behind a port, default off**; never replace a locked decision silently. [eqms E37]
14. **Honest limits.** Every decision records its known limit or cost accepted; every non-goal is stated (privacy/audit for a backup feature was declared a non-goal and the design respected that). [mico, eqms]

## 2. Dependencies and technology

- **Minimise dependencies; own small code behind an ABC.** Hand-roll 60-100 lines rather than add a library (mico rejected APScheduler, croniter, structlog, aiosqlite, alembic...). Every dependency needs a recorded licence / CVE / maintenance check; "no package is pre-approved". Check for enterprise approval constraints early. Measure bundle impact before adding a frontend dependency. Pin exact versions, commit the lockfile.
- **Stack defaults** (recommended unless constraints say otherwise):
  - Web/mobile client: **TypeScript + React + Vite** PWA (direct install, no store; Capacitor only if camera/install/native API demands it). One codebase for mobile and desktop. Plain CSS or Tailwind; zod at external boundaries; Vitest + Testing Library; Playwright for e2e when stakes warrant.
  - Backend: **Python (FastAPI + Pydantic v2)** for document/ML/pipeline-ish work; **Node/Express (TS)** when sharing code with a TS client is the main win (a `shared` workspace). Next.js monolith for small full-stack apps with auth.
  - Storage: files/localStorage/IndexedDB for backendless; **SQLite (WAL)** for single-node; **Postgres** (JSONB-friendly) on Railway when multi-instance; object storage for blobs; no DB v1 if one customer.
  - Hosting: GitHub Pages (static), Railway (server + DB, staging + per-PR envs for riskier apps), Cloud Run (serverless Python). Deploy on merge to main via GitHub Actions.
  - Games: Canvas 2D with a fixed-timestep loop, state in refs/engine not React state; Matter.js behind an engine interface if physics is needed; WebAudio synthesised sounds; emoji/procedural fallback art with drop-in SVG/PNG overrides.
  - Python/TS split for algorithm-heavy products: Python for algo and backend, TS for the frontend (stated personal preference).
- **Config over magic numbers**: a constants module/file, named enums, config + presets/flags justified by measured evidence. No feature flags "unless asked".
- **i18n/RTL from day one** when the audience is Hebrew-speaking (logical CSS properties, RTL e2e). [monsort, irri]

## 3. AI / LLM features

- Provider behind an interface; **one shared client**; **stub implementation** so the app and tests run with no keys; mock mode env var. Model names in env with a fallback model.
- Keys server-side only (or BYOK memory-only for backendless). Never in the client bundle, never logged, never in the repo.
- **Deterministic first, LLM as fallback** (hint patterns, structural segmentation); no LLM/automation "until there's evidence it's worth the complexity" (bruxism dropped its LLM and cron). Human confirmation for any AI-authored content that matters; human can overrule an AI verdict (dispute).
- Output pipeline: validate (zod/Pydantic) -> sanity checks -> retry -> fall back to bundled data. Retry with configurable count and increasing backoff, a hard overall timeout (about 30 s), model fallback on persistent 503/429, friendly error that does not burn the user's retry budget, loading indicator. Slow AI calls never run inside DB locks.
- Safety: prompt-injection detection and text sanitisation before text reaches the model, length caps, image MIME allow-list + magic bytes + downscale, two-tier moderation (hard block vs flagged-with-override that is logged), never `innerHTML` model text, never reveal answers in model "reason" fields.
- Cost: caching of paid calls, daily/monthly budget caps server-side, per-request cost recorded. Prefer cheap multimodal models for consumer apps; decide hosted-vs-local explicitly (cost, privacy, quality).
- Build-vs-buy for the hard component is a real decision: check vendor lifecycle (deprecations), run a benchmark, record the evidence.

## 4. Errors, concurrency, observability

- **Error taxonomy by what makes the error go away** (transient / depleted / budget / config / content / fatal), one error shape (class, stable code, message, detail, affordances) rendered identically by CLI, web, notifications and logs. Bounded retries with jitter, a wall-clock ceiling and a circuit breaker. Optional dependency down => degrade visibly; mandatory => fail hard; unattended runs fail fast on config errors and never silently commit unverified output. "Don't fail, use default" for missing/corrupt settings.
- **Concurrency**: name the lost-update hazard; prefer optimistic concurrency + partitioned writes (one file/row per entity) + service-layer persistence; row-lock read-modify-write with a fresh read inside the lock; accept and document rare races at small scale. Test concurrency; don't ship it untested. Rate limits keyed per user, not IP.
- **Measure, don't guess** performance, then pin the number in a test (call count constant in library size). One pipeline, not many parallel scans; stage-then-swap and diff UI state rather than clearing counters.
- **Logging/audit are first-class**: structured or single-line greppable logs with a correlation id; **redaction in the handler**, not at call sites; an audit entry for every state-changing action (append-only, durable, one per action); support-bundle export; debug logging to find root cause.
- State must be visible: show reasons and next actions for failures; no stuck "loading" text; stage-accurate status messages; overloaded words get distinct labels.

## 5. Testing

- **TDD**: Definition of Done derived from requirements + use cases + tests; tests designed and failing before code; full suite before PR; checklist review.
- Declare **test levels per task**: unit, component/integration (in-memory fake), smoke, system (scripted full flows without a browser), e2e (Playwright/CLI subprocess). Offline suite must pass with no network or keys.
- Fakes for every port; shared contract suites; **mock agent / mock LLM / mock server** as first-class deliverables; injected clock, random and sleep (real-clock tests rot); no tests reaching into private members; table-driven tests for every row of a spec table (off-by-ones were caught repeatedly).
- Games: **bots that solve every canonical level** so a rules change that breaks a level fails the build; "this should kill you" tests; screenshot evidence for UI.
- Security tests derived from the route table (every protected route 401s anonymously); coverage gates per area; run `/code-review` and security scans (CodeQL, dependency audit) as CI gates.
- "Acceptance" per milestone proves reachability through the real interface.

## 6. Delivery and process

- Docs trio: **PRD (what) -> decision log (why) -> implementation plan (how/order)**, plus a `.agents/` knowledge base (what the code does today) with `CLAUDE.md` as a 3-10 line pointer; update the knowledge files in the same change set (or a separate `docs(agents):` commit, the repo's convention). Link, don't copy. "`.agents/` describes the code, `docs/` describes the product; if they disagree trust the code and flag it."
- **Numbered, dated decision rows** (D-n/E-n/AD-nn) with rationale, rejected alternatives, cost accepted, supersedes/refines links; open questions tracked and never guessed; deferred items with re-entry points.
- **Execution protocol** for agents: Phase 0 serial and frozen -> parallel tracks against fakes -> sequential chain only where truly dependent -> integration/hardening with exit gates and test counts; 7-step per-task loop (design -> DoD -> tests -> implement tests -> minimal code -> full suite -> checklist review); stop conditions; status per phase, not per task.
- **One PR per task ID** (large features sliced `n/N`), each branch from clean `main`, draft PR, subscribed, driven to green, merged on the user's say-so. Always give the PR link. Run tests before opening or splitting a PR. Design is posted/discussed before code when the user says "do not implement yet".
- CI: lint, typecheck, test, e2e, build. **CI-cost aware**: cancel superseded runs, per-job path filters (skipped jobs still report success), skip drafts for review, heavy scans weekly/on demand, PR-only triggers with deploy on merge. CI failure caused by runner/quota is not a blocker; one re-run, one comment, then proceed. Independent reviewer agent and an automated review gate with a single-source checklist; gate infra bugs must not block all merges.
- Environments: staging branch and per-PR environments for riskier apps; secrets in platform env vars; the server **refuses to start in production with default secrets**; env matching case-insensitive (Railway capitalises values).
- Deploy trigger is explicit: merge to main -> Actions -> host; verify the deploy.

## 7. UX principles (when there is a UI)

Minimum-effort start; auto-advance flows instead of "next" buttons; everything on one screen for kids/pass-the-device; icon-only buttons with aria-labels and tooltips on mobile; one primary CTA; progressive disclosure; undo toast over confirm dialogs; tap-to-edit; quiet, tasteful visuals (no confetti); never leak spoilers or answers; show validation reasons; consistent terminology (the user owns the domain vocabulary and renames it); colours/radii/fonts in a token file with a test that fails on raw colours; mobile-first because the user tests from an Android phone on the deployed site.

## 8. How the user communicates (so the interview fits)

- Terse and directive: numbered answers, "ok", "merge", "next", "status". Often on a phone.
- Delegates routine technology choices ("no preference"), decides product behaviour and wording firmly, defines terms.
- Wants a reasoned explanation before approving anything unfamiliar ("explain what you wanna do and why").
- Wants to review security findings one at a time with the danger and the fix, approving each.
- Expects honesty about what was not verified (not run, not heard, not seen).

## 9. Anti-patterns to design against (each was a correction or review finding)

- Docs and code drifting; spec text that no longer matches behaviour. Components built but never wired; dead stubs and unreferenced constants.
- Trusting client input; unauthenticated trust of caller-supplied fields; secrets or default admin emails in code; a hardening change that locks the owner out.
- PRD flows that leak the answer; spoilers in UI or model output.
- Duplicate paths for solo vs team (reuse components); duplicated concepts (three kinds of "document"); persistence left to each route; whole-file rewrites of shared state.
- Guessing open questions; silently breaking a locked decision; assuming scope (working on the PoC when the product was meant; touching crawlers/catalogs when told not to).
- Over-engineering: speculative extensibility, two-step classifiers, automation/LLM without evidence.
- Invisible failures; stuck status text; overloaded labels; text buttons on mobile.
- Tests tied to the host or real clock; flaky e2e re-run forever instead of root-caused; shipping without running tests.
- Claiming something shipped/merged/working without checking its real state.
