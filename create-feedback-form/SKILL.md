---
name: create-feedback-form
description: Add an in-app feedback / bug-report form to a project - collects type, title, description, severity, optional screenshot and system info, stores it as an issue record and delivers it by email, GitHub issue, or backend DB API. Use when the user wants a "feedback form", "report a bug button", or in-app issue reporting in a new or existing app.
---

# create-feedback-form

Generic, stack-agnostic recipe for an in-app feedback form plus its storage and delivery. Adapt to the host app's framework, UI kit, i18n, styling and test conventions (read the repo's agent/contributor docs first). Follow the repo's existing patterns over anything below.

## Phase 1 - Discover and ask

First inspect the code for answers; only ask about what is still unknown. Never ask what the code already tells you.

**Discover from code (if the app exists):** framework/UI kit, existing menu/header components, i18n, existing backend/DB/ORM and migration tool, existing email or GitHub integration, env/secret handling, existing screenshot or logging libs, test setup, CSS conventions (e.g. RTL/logical properties).

**Ask the user** (one batched question, defaults in bold, accept "defaults"):

1. **Destination** (multi-select allowed):
   - App database (new table via the app's migration tool) -> needs a backend API
   - Email -> which recipient address; which sender/transport (mailto link, SMTP/provider API, serverless fn)
   - GitHub issue (repo `owner/name`; auth path) or another tracker (Jira, Linear, webhook - user details URL, auth, field mapping)
2. **Types**: **bug, feature, other**
3. **Severity levels**: **critical, error, warning, info**
4. **Take screenshot**: **yes, user can opt out**
5. **Attach system info**: **yes, user can opt out** (app version, build/commit, URL/route, user agent, platform, language, viewport, timezone, online state, recent console errors if cheap)
6. **Routing**: recipient address (email), assignee (GitHub login / user id), mention (@user or @team in the body), default labels
7. **Other** (offer, don't force): attach recent logs, contact email for reply, include current user/session id (privacy!), rate limit, offline queue, consent/privacy text, auto-close/resolution workflow, i18n languages
8. **Button location**: **top-right hamburger menu item**, top menu, floating button, footer, other (user details)

Echo the final decisions as a short config summary and get a go-ahead before coding.

## Phase 2 - The form

Fields, in order:

| Field | Control | Notes |
|---|---|---|
| type | select/segmented | configured list, first = default |
| title | single-line text | required, max ~120 chars |
| description | multi-line text | required, max ~5000 chars; prompt "steps to reproduce / what you expected" for bugs |
| severity | select | configured list; hide or default for non-bug types if sensible |
| include screenshot | checkbox | only if enabled; default checked; show preview, let user remove it |
| include system info | checkbox | only if enabled; default checked; let the user expand to see exactly what is sent |
| resolution | **not in the form** | stored field only (see Phase 3) |

Rules:
- Take the screenshot **before** opening the form/modal so the form itself is not in the shot (e.g. `html-to-image`/`html2canvas` on the DOM, or `getDisplayMedia` as fallback). Downscale + compress (JPEG/WebP, ~1280px wide, <500 KB). Failure to capture must not block submit: warn and continue.
- Mask sensitive content: skip elements marked `data-feedback-redact`, password/secret inputs, and anything holding API keys or tokens. Never include secrets in system info.
- Validate with the project's schema lib (e.g. zod) on client and server; trim input; treat all text as untrusted (no `innerHTML`, escape in email HTML, escape/neutralize markdown + @mentions from user text in GitHub bodies).
- States: idle, submitting (disable button), success (thank-you, close), failure (keep the form content, show retry). Never lose the user's text on failure.
- Accessibility: labelled controls, focus trap in dialog, Esc closes, error text via `aria-live`, keyboard-reachable menu entry. Use the app's i18n and logical CSS properties; no magic strings (put types/severities/limits in constants/config).
- Add the entry point at the chosen location; on mobile keep the dialog usable at small viewports (scroll inside the dialog, not the page).

## Phase 3 - Issue model and storage

One shared type used by form, storage and delivery:

```
FeedbackIssue {
  id            uuid (client-generated, idempotency key)
  createdAt     ISO-8601 UTC
  type          enum(config)
  title         string
  description   string
  severity      enum(config)
  screenshot?   data URL / blob ref / storage key
  systemInfo?   { appVersion, build, route, userAgent, platform, language, viewport, timezone, ... }
  resolution    enum: open (default) | in_progress | resolved | wont_fix | duplicate
  resolutionNote? string
  resolvedAt?   ISO-8601
  recipient?    email address (from config, not user input)
  assignee?     string (GitHub login / user id)
  mention?      string (@user / @team)
  labels?       string[]
  delivery      { status: pending|sent|failed, attempts, lastError?, externalRef? (issue URL / message id) }
}
```

- `resolution` is **never shown in the submission form**; it defaults to `open` and is changed by maintainers (admin UI, DB, or by syncing from the tracker's state).
- `recipient`, `assignee`, `mention`, `labels` come from configuration (and optionally per-type/severity routing, e.g. critical -> mention on-call), not from the end user.
- If destination includes the app DB: add a `feedback` table through the project's migration tool (columns mirror the model; screenshot stored in object storage or a blob/text column with size cap; index on `createdAt`, `resolution`, `severity`). Add `POST /feedback` (validate, size-limit, rate-limit, idempotent on `id`) and, if useful, an authenticated `GET /feedback` + `PATCH /feedback/:id` for resolution. Add whatever fields the user's extras (Phase 1 q7) require.
- Backendless apps: persist unsent items locally (e.g. localStorage/IndexedDB outbox) so offline or failed deliveries can retry; cap the outbox size.

## Phase 4 - Delivery

Define one interface and one adapter per destination; the form talks only to the interface. Support multiple destinations at once via a fan-out that records per-destination result.

```
interface IFeedbackSink { send(issue: FeedbackIssue): Promise<DeliveryResult> }
```

- **Backend DB (API)**: `POST` JSON to the feedback endpoint; handle 4xx (show validation error, don't retry) vs 5xx/network (queue + retry with backoff).
- **Email**:
  - No backend: `mailto:` link prefilled with subject `[type/severity] title` and body (can't attach screenshots - say so, offer download/copy) or a form-to-email service.
  - With backend/serverless: send via provider API/SMTP from the server, screenshot as attachment/inline image. Recipient and credentials live server-side only.
  - Subject: `[<type>][<severity>] <title>`; body: description, system info, issue id.
- **GitHub**:
  - Create the issue via `POST /repos/{owner}/{repo}/issues` with title `[<severity>] <title>`, markdown body (description, collapsed `<details>` system info, issue id), labels from type/severity, `assignees`, and the mention line.
  - Never put a GitHub token in client code. Use a server/serverless proxy holding a fine-grained token (issues: write on that repo only), or a `repository_dispatch`/Actions workflow, or fall back to opening `https://github.com/{owner}/{repo}/issues/new?title=...&body=...&labels=...` in a new tab for the user to confirm (URL length-limited; screenshot can't be attached - tell the user to paste it).
  - Screenshots: upload to the repo/storage and link, or attach manually in fallback mode; don't inline huge base64 in the body.
- **Other tracker/webhook**: map `FeedbackIssue` to its payload per the user's details, same retry rules.
- Record `delivery.status`, `attempts`, `externalRef`; surface a clear success or failure in the UI. Log failures without logging secrets or full screenshots.
- Secrets/config via env vars; document each in the README/.env.example.

## Phase 5 - Verify and hand over

- Tests at the project's levels: unit (validation, issue builder, per-sink payload mapping with the transport mocked), component (required fields, opt-out checkboxes hide/skip screenshot and system info, failure keeps text, `resolution` field absent), e2e (open from the chosen button location, submit, see success against a stubbed endpoint).
- Run the repo's lint, typecheck, tests, build.
- Manually check: screenshot excludes the dialog, redaction works, small viewport, RTL if supported, offline path.
- Summarize to the user: chosen config, files added, required env vars/secrets and how to obtain them, and anything that fell back (e.g. mailto without attachment).
