# Decision catalog

The decisions a PRD usually leaves open. For each: the question, the realistic options, the house default (from `house-preferences.md`; "none" = no history, ask), and the dilemma seen in past projects. Select by project type using `project-profiles.md`; skip anything the PRD or repo already answers. Order of categories is the usual order of asking.

Tags: **[B]** blocking - ask. **[D]** defaultable - put in the assumed-defaults batch unless the PRD makes it risky. **[C]** conditional - only when its trigger holds.

---

## A. Product shape and scope

- **A1 [B] Project type and success criteria** - game / consumer web app / personal tool / B2B service / internal tool / local-first desktop or CLI / data-ML pipeline / content site. What does "done" look like for v1?
- **A2 [B] MVP slice** - which PRD scope is v1? What is explicitly deferred? Default: the thinnest end-to-end slice, everything else listed under Deferred with a re-entry point. Dilemma: "product not PoC" - confirm whether this is a prototype or a product (changes testing, auth, hosting).
- **A3 [B] Users and tenancy** - single user, a family/group, one customer, many customers? Default: single-tenant now, seams for later (UUID keys, owner_id, repository interface).
- **A4 [D] Non-goals** - state them (privacy, audit trail, offline, realtime, accessibility, native app...). The user respects declared non-goals and doesn't want over-engineering for them.
- **A5 [D] Fixed rules vs tunable settings** - which product rules are "never violate" (go in `.agents/README` hard rules) vs configurable.
- **A6 [C] Cost envelope** - per-user / per-month ceiling, API budget; drives free-tier hosting, caching, local vs hosted AI. Trigger: any paid API, hosted backend, or price-sensitive customer.
- **A7 [C] Regulatory/compliance** - medical (ISO 13485 / Part 11), PHI, kids' data, GDPR. Trigger: PRD mentions. Default: state positioning guards (what the product must NOT become), human-in-the-loop for AI content, tamper-evident audit, minimal data off-device.
- **A8 [D] Audience and language** - ages, technical skill, languages, RTL. Default: i18n + logical CSS from day one if Hebrew.

## B. Platform and client

- **B1 [B] Client form factor** - static web page / PWA / PWA + Capacitor wrapper / native (Kotlin/Swift) / cross-platform (Flutter, React Native) / game engine (Unity, Godot, Phaser) / Electron desktop / CLI. Default: **one TypeScript React PWA**, direct install, no store; Capacitor only if native API or store presence is required. Dilemma (irri): native = second codebase and toolchain; React Native adds its own toolchain and desktop shims. No past evidence of a native Android build or an engine like Unity/Godot - ask, don't assume.
- **B2 [B] Target devices and distribution** - Android phone, iOS, Windows/macOS/Linux, kiosk; store vs direct install vs GitHub Pages. Default: Android phone primary + desktop browser; direct install.
- **B3 [D] Offline behaviour** - none / cache shell / full offline with sync. Default: PWA shell cached, no offline mode if the customer has connectivity (simplest); backendless apps are inherently offline-capable after load.
- **B4 [D] Input and controls** (games/mobile) - touch, keyboard, gamepad; mobile controls early vs deferred (bisly left touch controls open for a long time - decide early if mobile is a target).
- **B5 [D] Accessibility and i18n** - a11y bar (axe sweep), reduced motion, colour-blind safe palettes, languages/RTL.
- **B6 [D] Look and feel direction** - art style, palette, tone (quiet/tasteful vs playful), tokens-based theming and branding. Default: design tokens in one file, a test that fails on raw colours.

## C. Architecture shape

- **C1 [B] Backend or backendless** - static/local-only; BYOK to third-party APIs from the browser; serverless container; modular monolith; separate services. Default: backendless if possible; else modular monolith or one serverless container. Dilemma (monsort, irri): no backend means no server-held key => BYOK/memory-only keys or a proxy deferred behind an interface.
- **C2 [B] Local-first vs hosted vs customer-owned cloud** - who holds the data (eqms moved from SaaS to "the customer's own Google Workspace; Drive ACLs are the authority"). Default: local-first when privacy or cost is central.
- **C3 [B] Frontend/backend separation and contract** - monorepo with `shared` package of pure logic + API contracts; OpenAPI as the contract with generated TS types; mock server for parallel work. Default: yes, contract frozen in Phase 0.
- **C4 [B] Layers and dependency direction** - e.g. ui -> logic -> infra; app never imports infra; enforcement mechanism (import-lint / AST script). Default: mechanical enforcement in CI.
- **C5 [B] Interfaces (ports)** - list every volatile/external capability and give it a port + fake: storage, LLM, auth, e-sign, notifications, scheduler, simulation engine, network adapter, clock. Default: all of them.
- **C6 [D] Service facade and API surface** - one facade with command/result objects used by CLI and web; REST thin binding; **internal API** (module interfaces) vs **external API** (public REST/webhooks) vs **third-party APIs consumed**; versioning (`/api/v1`), error shape, pagination, idempotency keys. Default: facade + thin REST + parity rule.
- **C7 [C] CLI surface** - Trigger: tool for engineers/managers. Default: CLI-first, core fully tested through CLI before web bindings; `-h` with examples.
- **C8 [D] Plugin/extension points** - none until asked. Default: no speculative extensibility.
- **C9 [C] Background work and scheduling** - none / in-process job runner / cron hitting a secret-guarded endpoint (GitHub Actions) / queue. Default: smallest thing; structured schedule spec over cron-string parsing; skip-if-in-flight; catch-up on startup. Trigger: reminders, refresh, sync.
- **C10 [C] Realtime** - polling (3-5 s) vs websockets vs none. Default: polling with row-locked read-modify-write. Trigger: multiplayer/chat.

## D. Languages, stack and dependencies

- **D1 [D] Languages** - Default: TypeScript everywhere; Python for algorithm/document/ML backends; the user states a Python-algo + TS-frontend preference for such products.
- **D2 [D] Frameworks and tooling** - React+Vite, FastAPI, Express, Next.js, Tailwind/plain CSS, Zustand, zod, Vitest/pytest/Playwright, ruff+mypy, uv/npm workspaces. Default: see house-preferences.
- **D3 [B if constrained] Dependency policy** - allowed/forbidden, approval process (enterprise), pinning, licence/CVE/maintenance check, hand-roll vs library. Ask early whether any approval constraint exists.
- **D4 [C] Build vs buy for the hard component** - e.g. visual product search, scheduling, e-signature, physics, auth. Research vendor lifecycle (deprecations), benchmark, record evidence; keep behind a port. Trigger: any component that is the product's core difficulty.
- **D5 [D] Repo layout** - monorepo with workspaces (`shared`, `server`, `web`), or `platform/` + `products/` + `apps/` layers for a multi-product tool; where docs, `.agents/`, OpenAPI live.

## E. Data and persistence

- **E1 [B] Source of truth per datum** and what is derived/disposable (rebuildable). Include files-vs-DB split if human-editable files matter.
- **E2 [B] Storage technology** - localStorage / IndexedDB / files / SQLite / Postgres / object storage / Drive / Firestore. Default by scale: local state -> SQLite -> Postgres; no DB v1 if one customer (folder per job in a bucket + index file).
- **E3 [D] Schema/migrations** - numbered forward-only migrations with pre-migration snapshot; JSONB "data" columns to avoid migrations (find-the-photos); test migrations against non-empty data.
- **E4 [D] Identifiers and keys** - UUID/UUIDv7, human-readable numbers (stored vs display format kept separate).
- **E5 [C] Retention and artifacts** - store everything per job (inputs, outputs, corrections) vs minimal; where; who can read; deletion. Trigger: photos, documents, personal data.
- **E6 [D] Backup/export/import** - one-way mirror to GitHub / file export / none. State what is allowed to be lost.
- **E7 [C] Concurrency model** - see G1.

## F. Identity, security and privacy

- **F1 [B] Authentication** - none / local profile / email+password / Google SSO / shared code / allowlist; two run modes (local without login vs multiplayer server mode, as in bisly). Default: none for local-only; Google SSO or email+password with session cookie for hosted.
- **F2 [C] Authorization** - role tiers, per-resource grants, who may read/write; storage ACL as authority; separation of duties (decide enforce or deliberately not). Trigger: more than one user role.
- **F3 [B] Secrets and key custody** - server env vars; BYOK memory-only; OS keychain; never client bundle; production refuses default secrets. Case-insensitive env matching.
- **F4 [D] Security posture** - CSP, referrer policy, rate limits per user, IDOR checks on every object route, localhost-only bind + token for local tools, security tests from route table, scanning gates (CodeQL, dependency audit, ZAP).
- **F5 [C] Privacy and data egress** - what leaves the device (LLM, analytics, maps, video embeds); opt-in notices; PHI minimisation; third-party contact disclosed.
- **F6 [C] Moderation / abuse** - user-generated content, AI-generated content, two-tier moderation; admin panel; reports.
- **F7 [C] Server authority** - which values the client may never set (prices, rewards, ownership, publish state). Trigger: economy, scores, multi-user.

## G. State, errors and consistency

- **G1 [C] Consistency and concurrency** - lost-update hazards; optimistic vs lock vs queue; partitioned writes; accepted races written down. Trigger: multi-user or multi-process writes.
- **G2 [C] Lifecycles / state machines** - draft -> review -> sign -> release; run states; hunt state; list states, parked/terminal, derived views. Draw it.
- **G3 [D] Error model and retries** - taxonomy by what makes the error go away; one error shape; retry caps, timeouts, circuit breaker, degrade-vs-fail for optional dependencies; fail fast when unattended.
- **G4 [D] Configuration resolution** - global -> per-operation -> per-item -> per-run; effective config recorded.
- **G5 [D] Idempotency and recovery** - reconcile sweeps, startup recovery, "folder is source of truth on reconnect", no silent auto-adopt.

## H. AI / LLM (trigger: any model use)

- **H1 [B] Is an LLM needed at all?** deterministic-first; what is the evidence it is worth it?
- **H2 [B] Provider and hosting** - Gemini / Claude / OpenAI / local Ollama; cost, privacy, quality. Default: hosted for quality with a selectable local option; Gemini for cheap multimodal in consumer apps.
- **H3 [D] Abstraction and stub** - provider interface, single client, stub for no-key dev, mock mode, model env + fallback model.
- **H4 [D] Reliability** - retries with increasing backoff, hard timeout (~30 s), model fallback, friendly error, loading indicator.
- **H5 [D] Output validation** - schema validation, sanity checks, retry once, fall back to bundled content; confidence scoring; provenance on every AI claim.
- **H6 [C] Safety** - prompt-injection, sanitisation, moderation, kid mode, human override.
- **H7 [C] Cost controls** - cache, budgets, caps; per-request cost recorded.
- **H8 [C] Human-in-the-loop** - what an AI may write on its own vs behind an Approve/Cancel card.
- **H9 [C] Using Claude Code/agents as a runtime** - subprocess vs API, trust boundary (a file sidecar, not parsing transcripts), no credentials held, scoped tools. Trigger: the product orchestrates agents.

## I. External integrations

- **I1 [B] Which third-party systems** - for each: purpose, auth, cost, rate limits, lifecycle/deprecation risk, mock. Default: adapter behind a port, a spike first for unknown behaviour, mock mode.
- **I2 [D] Webhooks/inbound events and outbound notifications** - email / push / in-app; opt-in; actionable vs informational.
- **I3 [C] Feedback/bug loop** - in-app report -> GitHub issue -> delegated implementation (see `create-feedback-form`).

## J. Game-specific (trigger: project type = game)

- **J1 [B] Game genre, core loop, session length, win/lose** - and the "one new idea per level" progression.
- **J2 [B] Engine and rendering** - Canvas 2D / DOM / WebGL / Phaser / Unity / Godot; fixed timestep; logical vs backing resolution; state in refs not React state. Default: Canvas 2D + headless core; Matter.js behind an interface if physics.
- **J3 [B] Headless rules core** - all rules in an engine with no UI imports so bots and tests drive it. Default: yes.
- **J4 [D] Content authoring and validation** - levels/decks as data (JSON auto-registered), in-game editor, import/export, bot-solved canonical levels, publish gates (cleared N times).
- **J5 [B] Multiplayer model** - none / pass-and-play on one device / async via accounts / realtime. Where is authoritative state? Public vs private rooms and codes. Default: avoid realtime; async + polling.
- **J6 [C] Economy and balance** - currencies, prices, rewards; server-authoritative; tunables in constants; balance iterated from playtests and recorded with the "why".
- **J7 [D] Assets pipeline** - art source (user-supplied / generated / procedural), sprite naming convention, state variants, fallback chain (custom -> bundled -> emoji), pose briefs for image generation, audio (synthesised vs files), size budget.
- **J8 [D] Customisation/white-label layer** - config object -> named packages, one active, store interface swappable for an API.
- **J9 [D] Persistence and progression** - localStorage / account; save after every move; resume.
- **J10 [D] Mobile game specifics** - touch controls, orientation, performance budget, haptics, install, store vs PWA.
- **J11 [D] Fairness/secrecy rules** - hidden information on a shared screen (equal dwell time), spoiler protection, anti-cheat server-side.

## K. Observability

- **K1 [D] Logging** - format, correlation id, levels, redaction in handler, retention.
- **K2 [C] Audit trail** - append-only, durable (fsync), per-action, per-node files, document-scoped queries. Trigger: compliance, multi-user changes.
- **K3 [D] Error reporting and support** - in-app report, support bundle, status page.
- **K4 [D] Metrics/usage and cost tracking** - minimal; per-request API cost.

## L. Testing

- **L1 [D] Test levels per component** (unit / component / smoke / system / e2e) and what each area uses.
- **L2 [D] Fakes, mocks, contract suites; mock mode without keys.**
- **L3 [D] Coverage and quality gates**; security tests; concurrency/stability tests; a11y sweep.
- **L4 [C] Domain-specific verification** - bot-solved levels, golden files, fixture corpora, benchmark harness for ML.

## M. Delivery and operations

- **M1 [D] Branching and PR rules** - one PR per task, draft PRs, branch from clean main, numbered slices.
- **M2 [D] CI jobs** and which block merge; CI-cost controls; review gate.
- **M3 [B] Hosting and deploy trigger** - Pages / Railway / Cloud Run / shared host / Docker image artifact; merge-to-main -> Actions -> deploy; staging and per-PR environments for riskier apps.
- **M4 [D] Environments and secrets management.**
- **M5 [D] Release/versioning and in-app version display; PWA auto-update.**
- **M6 [D] Automation** - `@claude` delegated implementation via a label/comment-triggered Action.

## N. Docs and process

- **N1 [D] Doc set** - PRD, design, decision log, plan, `.agents/` knowledge base, in-app help; link don't copy; update in the same change set.
- **N2 [D] Agent execution protocol** - phases, parallel tracks, stop conditions, status cadence, merge delegation.
- **N3 [D] Open questions and deferred items register.**
