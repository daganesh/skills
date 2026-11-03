# create-feedback-form

Adds an in-app feedback / bug-report form to a project: form UI, issue model and storage, and delivery (app DB, email, GitHub issue or other).

- **Use when:** "add a feedback form", "report a bug button", in-app issue reporting.
- **Flow:** `SKILL.md` runs 5 phases: discover and ask → form → issue model/storage → delivery → verify and hand over.
- **Inputs it asks for:** destination, types, severities, screenshot/system-info opt-outs, recipient/assignee, button location (all with defaults).
- **Related:** the feedback tickets it creates can feed [`delivery-pipeline`](../delivery-pipeline/README.md); tests for the form follow [`plan-tests-for-change`](../plan-tests-for-change/README.md).

Entry point: [`SKILL.md`](SKILL.md) · Up: [skills index](../README.md)
