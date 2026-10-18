# Project profiles

Pick the closest profile(s) after the PRD read-back (a project can be two, e.g. "web LLM game"). Each lists: the categories to cover (letters refer to `decision-catalog.md`), the stack the user has actually used, and the questions specific to the type. Past examples are named so the recommendation can cite precedent.

## Game (casual / party / physics / level-based)

Past: bisly (physics trick-room, server + SQLite), monsort (pass-and-play, backendless PWA), weddinvaders (canvas shooter, backendless), find-the-photos (photo treasure hunt, Postgres), Word_guess (single-file party game).

- Categories: A (esp. A2, A8), B (B1, B4, B5, B6), C1, J (all), F7 if any shared economy, G2 for game/turn state machine, H if AI content, L4, M3.
- Typical stack: TypeScript, React + Vite, Canvas 2D with fixed-timestep loop, headless engine module, Vitest; Zustand if a store is needed; GitHub Pages when backendless, Express + SQLite/Postgres on Railway when shared state is needed.
- Specific questions to surface:
  1. Core loop, session length, single vs multi-player, same-device vs remote.
  2. Is the rules engine headless and testable by bots? (default yes)
  3. Where does hidden information live (private store slice, `toPublicView` redaction)? Does any flow leak the answer?
  4. Multiplayer: pass-and-play / async accounts / realtime? Authoritative state? Cheating tolerance?
  5. Content: authored data vs generated (LLM) vs user-made; validation and publish gates.
  6. Assets: who produces art/sound; fallback when missing; naming convention; image-gen briefs.
  7. Mobile: touch controls, orientation, performance budget, PWA vs wrapped app vs engine export - **if "Android mobile game": ask native vs PWA+Capacitor vs engine (Unity/Godot); no precedent in history.**
  8. Balance: which numbers are tunables in one constants file; how is balance iterated (issues from playtests).
  9. Fun and feel guardrails: quiet celebrations, no spoilers, minimum-effort start, auto-advancing flows, kid-safe.
  10. Customisation/white-label (weddinvaders packages) needed?

## Web LLM app / AI-powered product

Past: find-the-photos (Gemini image judge, moderation, avatars), irri-vision (VLM perception pipeline), ClearClaim (Gemini OCR), monsort (BYOK deck generation), iso-top (opt-in LLM fallback).

- Categories: A6, C1, C5, D4, F3, F5, F6, H (all), K1, L2, M3.
- Typical stack: Python FastAPI (pipeline) or Node Express (shared TS), React PWA client, Gemini via one shared client, stub + mock mode, cached paid calls, bucket/SQLite/Postgres.
- Specific questions:
  1. LLM necessary, or deterministic-first with LLM fallback? Evidence?
  2. Provider, hosted vs local; cost per request and a budget cap; who holds the key (server / BYOK).
  3. Output schema and validation; fallback content; human override.
  4. Reliability: retries/backoff/timeout/model fallback.
  5. Safety: injection, moderation tiers, kid-safe, spoiler leakage via model "reason".
  6. Eval: benchmark set and regression; small-sample caveats; flags and presets justified by measurements.
  7. Build-vs-buy for the vision/search core and vendor lifecycle.
  8. Data retention of inputs/outputs/corrections (corrections are the most valuable data).

## Personal / privacy-sensitive tool

Past: bruxism-tracker (patient + clinician), iso-top (local-first documents), mico (local-first workspace), weddinvaders RSVP.

- Categories: A4, A7, C2, E1, E2, E5, F (all), H1/H2 (LLM opt-in), K2, M3.
- Typical stack: Next.js + Prisma + SQLite on a Railway volume (hosted) or Electron + local FastAPI sidecar + SQLite (desktop); IndexedDB for sensitive text; OS keychain for keys.
- Questions: what data is sensitive and must never reach the cloud; what metadata may; consent/egress notices; staging env; seeded demo/test mode login; deletion/export; positioning guards (what this product must not become).

## B2B / internal service (regulated or workflow-heavy)

Past: light-eqms (document control, Google Workspace as store), mico (manager workspace), iso-top.

- Categories: A3, A7, C (all), D3, D4, E, F (all), G (all), K2, L3, M (all), N (all).
- Typical stack: Python FastAPI + Pydantic + SQLite->Postgres, React/TS/Vite, ports + fakes, Docker image built in Actions, CodeQL + audit + ZAP gates, Claude review gate.
- Questions: who owns the data and the identity authority (customer's workspace/ACLs vs your backend); RBAC tiers; separation of duties enforce or not; workflow state machine and vocabulary with the design partner; numbering/versioning (stored vs display); audit durability; compliance invariants as tests; customer-contradicts-decision => opt-in alternates; price ceiling => free self-hostable components.

## Local-first desktop / CLI / agent-orchestrating tool

Past: mico, iso-top, determinator (idea).

- Categories: A, C (C7, C9), D3, E1-E3, F3/F4, G (all), H9, K, L, N.
- Typical stack: Python (Typer, FastAPI localhost, SQLite WAL, Pydantic) + React/Vite UI with committed build; or Electron + PyInstaller sidecar.
- Questions: dependency-approval constraint; localhost security posture (bind, token, CSRF, Origin); trust boundary with any agent (file sidecar); scheduling/unattended behaviour; CLI/UI parity; packaging (pipx, uv, PyInstaller); what is disposable vs durable; backup scope.

## Static / backendless app or content site

Past: weddinvaders, Word_guess, monsort.

- Categories: A, B, C1, E2 (localStorage), F3 (BYOK), M3 (Pages), L.
- Questions: where does state live; what happens on a new device; admin without a backend (unauthenticated local admin is acceptable only if data is local); single-file offline distribution (vite-plugin-singlefile); later backend seam (store interface).

## Mobile-first product app (Android primary)

Past: irri-vision (PWA, Android phone + laptop), bruxism-tracker (PWA + push), find-the-photos (mobile-first web).

- Categories: B (all), C1, F, M3, L.
- Typical choice: PWA direct install; Capacitor only if camera/install/native APIs demand; upload queue with retry; on-device quality checks; Hebrew RTL; icon-only buttons.
- Questions: install path for non-technical users (Windows too), camera/GPS/push needs, connectivity assumption, store requirement, device performance budget (drop heavy dependencies for mobile), deployment cadence and auto-update.

## Data / ML pipeline that becomes a product

Past: irri-vision (PoC pipeline -> product).

- Categories: C3, C5, D4, E, H, L4, M.
- Questions: PoC vs product scope boundary (what must not be touched: crawlers, benchmarks); package the pipeline as a library with stage ABCs and a config factory; flags/presets backed by benchmark tables; caching of paid calls; mock job for frontend development; monorepo layout (poc symlinks); evaluation harness retained.
