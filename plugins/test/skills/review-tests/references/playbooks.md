# Domain playbooks: behaviors that are easy to miss

Use when a change touches one of these areas. Each item is a candidate behavior to check against the diff. Not every item applies; list only those the change can affect, and give each a risk level (see `test-strategy.md`).

## Auth
- Expired, revoked and malformed sessions or tokens are rejected, and the user is sent to sign-in.
- Permissions: a user without the role cannot reach or act on the resource, including by changing an ID in the URL or request.
- Password and identifier rules at boundaries; lockout or rate limiting after repeated failures.
- Logout invalidates the session on every device that the design promises.
- Sign-up and sign-in do not leak whether an account exists.

## Payments
- Amounts: rounding, currency, zero, negative, maximum, and totals after discounts or tax.
- Idempotency: a retried or double-submitted payment charges once.
- Failure paths: declined, timeout after charge, webhook arrives before or after the redirect.
- Refunds and partial refunds reconcile with the original charge.
- No card or secret data is written to logs or the database.

## Forms
- Required, optional and conditional fields; whitespace-only and very long input.
- Validation messages appear at the right moment and clear when fixed.
- Submit twice, submit offline, and back-button after submit.
- Values survive a validation error without being cleared.
- Autofill and paste produce the same stored value as typing.

## CRUD and data
- Create, read, update and delete each work for one record, many records, and an empty list.
- Update of a record changed by someone else (concurrent edit) follows the design: last write, conflict, or merge.
- Delete is soft or hard as designed; related records are handled (cascade or block).
- Pagination and sorting at page boundaries and with zero or one record.
- Migration: existing rows are valid after the change; old and new code can read the data during rollout.

## i18n and RTL
- Hebrew, Arabic and other RTL text: layout mirrors, icons that imply direction flip, numbers and dates format per locale.
- Text expansion: long translations do not overflow or truncate key actions.
- Sorting and search behave correctly for non-ASCII characters and for mixed-direction text.
- Dates and times use the user's time zone, including around daylight-saving changes.

## Mobile
- Small and large viewports; rotation keeps state.
- Touch targets are large enough and do not overlap.
- Offline and poor network: the user sees a clear state and nothing is lost on retry.
- Background and resume: the app restores where the user was.
- Permissions (camera, location, notifications) denied and later granted.

## API and integration (added with any API change)
- Old clients still work: unchanged fields, defaults for new required fields, and error shapes.
- Unknown fields are ignored or rejected as designed, consistently.
- Timeouts and retries from the caller are safe.
