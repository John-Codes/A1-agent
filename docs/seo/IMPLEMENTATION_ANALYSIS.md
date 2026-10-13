# A1 recurring SEO job: initial implementation analysis

Revision notice: `REVISED_PLAN.md` supersedes the English-first count, optional DOCX handling, and initial SQLite recommendation. Current scope is five English/Spanish topic pairs, Markdown-only articles, two Markdown-backed CRUD tools, and a minimal single-host progress file. This document retains the original API/startup audit.

Inspected 2026-10-13 on branch `feature/plan-execute-task-loop`. This is a design and research deliverable. No job tool, service installation, email delivery, API write, or production deployment was performed. Existing code changes on the branch were preserved.

## What already exists

| Capability | Evidence | Assessment |
| --- | --- | --- |
| Email send/read/reply | `tools/agentmail/actions.py`, `tools/agentmail/client.py` | Reuse client; key is configured, sender still needs selection and a delivery check |
| Tool execution and live output | `task_runtime/worker.py`, `task_runtime/supervisor.py` | Reuse workers and events; the controller currently requires an interactive terminal |
| Durable interactive task queue | `task_runtime/state.py` | Useful prototype, but one JSON plan is insufficient for daily batches, article versions, mail receipts, and approvals |
| Read-only heartbeat | `heartbeat/worker.py` | Observer only; do not use its small model as an always-running content planner |
| Article storage | `../testreadycdl.com/exam-api/app.py` | Correct service is EXAM API, not `cdl-api` newsletter/analytics service |
| Article quality report | `../testreadycdl.com/exam-api/quality/validator.py` | Checks limited formatting/length properties; not an SEO or factual-quality certification |
| Static blog deployment | `../testreadycdl.com/scripts/sync-blog.mjs`, `.github/workflows/deploy.yml` | Published API articles materialize as Markdown, then Astro/Docker/Render deploy; schedule configured every 30 minutes |
| Container restart | `deploy/run_thor_container.sh` | Already specifies `--restart unless-stopped`, but its volumes omit a durable editorial-job database |

Read-only live checks: site `/blog/` returned HTTP 200; public article listing returned HTTP 200 and 14 published English articles. These prove reachability/read access, not write access, deliverability, CI health, or successful deployment of new articles.

## Existing article API contract

Production base: `https://exam-api-acfz.onrender.com`

Workspace path: `/api/v1/workspaces/ws_1`

| Operation | Endpoint | Current behavior |
| --- | --- | --- |
| Inventory | `GET /articles?page=1&limit=200` | Public requests see published only; authenticated admin can include drafts; paginate |
| Fetch/reconcile | `GET /articles/{slug}` | Unpublished article requires admin token |
| Validate | `POST /articles?dryRun=true` | Requires `X-Admin-Token`; returns quality report without inserting |
| Create draft | `POST /articles` | Requires `X-Admin-Token`; explicit `status: draft`; quality report must pass |
| Update/publish | `PUT /articles/{slug}` | Requires `X-Admin-Token`; supports merged edits/status but currently lacks quality recheck and approval enforcement |

Payload fields: `slug`, `title`, `description`, `excerpt`, `content` (Markdown body), `tags`, `publishedDate`, optional `updatedDate`, `status`, `lang` (`en`/`es`). Do not send frontmatter in `content`; the sync script creates it. Current schema requires a publication-date string even for drafts; actual publication must use an honest date. Add proper date validation and explicit draft-versus-publish date semantics during implementation.

Admin credentials must live in the publisher service, not model prompts, emails, browser bundles, or context Markdown. Use a dedicated, scoped publishing identity/endpoint rather than giving the drafting model a general admin token. Existing APIs use a general token, so least-privilege scope and the approval gate require implementation.

## Fixes before production automation

1. **Quality and approval on every publication path.** `create_article` validates quality; `update_article` validates only the Article schema. A draft can currently be changed to published without the equivalent quality check. Apply validation to the merged candidate and every publish transition. Require a valid approval receipt for the immutable version. Use an atomic version/hash comparison so edits cannot race approval. Check create-with-published as well as update-with-published; do not leave a second bypass path.
2. **Fetch all articles before deleting files.** `sync-blog.mjs` fetches only `?limit=200` and removes local files absent from the result. Article 201 and onward make that result incomplete. With 14 currently published and five new publications daily, this threshold would be crossed during day 38. Paginate to completion, validate every page, detect duplicate/invalid slugs, and abort without modifying the existing snapshot on any fetch/parse failure. Ideally use a server snapshot/version or cursor to avoid concurrent inserts shifting page boundaries.
3. **Correct the SEO validator's claims.** It attributes an 800-word minimum and rigid heading thresholds to Google and says a passing score meets Google guidance. Those are local heuristics, not Google's requirements. Warnings for 60/160-character title/description targets can combine into a failing score despite their nominal severity. Separate editorial requirements, warnings, semantic usefulness, and factual review. Never claim a score predicts ranking.
4. **Fix idle deployment detection.** The workflow compares API-generated files to a fresh Git checkout. When API content differs from committed Markdown, a later run can rebuild the same content again even after it was deployed. Compare a complete content manifest/hash to the last successfully deployed snapshot; advance it only after successful deployment.
5. **Use isolated test storage.** `DEPLOYMENT.md` says the dev-test API shares production's MongoDB database/workspace. A different hostname is not an isolated write environment. Provision a disposable database/workspace and verify the connection before any CRUD integration tests. Do not run the existing end-to-end publish/cleanup test against that shared workspace.
6. **Make editorial data durable.** Store jobs, article versions, source manifests, approvals, message IDs, outbox records, pause state, and publication receipts in SQLite with transactions on a persisted local volume, or an equivalent service database. Back it up. The current container mounts do not preserve these new files across container replacement.
7. **Render approved metadata honestly.** Current BlogPosting markup uses the organization as author but has no per-article human-review metadata/image field in the API schema. Add those fields only if the editorial process will supply real values, and carry them through sync/schema/templates. Validate safe Markdown/HTML and link schemes; do not render arbitrary active content from an email attachment.

Relevant Google references: [no preferred word count/helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content), [title guidance](https://developers.google.com/search/docs/appearance/title-link), [description guidance](https://developers.google.com/search/docs/appearance/snippet). No production fixes were applied in this analysis.

## Proposed reusable job system

Implement `job_runtime/` with scheduling, storage, workers, events, and pause/resume. Register `cdl_seo_daily` as its first job type. Other recurring tasks can later register their own handlers and permissions.

Suggested future control interface (not available yet):

```text
/jobs
/job status cdl_seo_daily
/job pause cdl_seo_daily
/job resume cdl_seo_daily
/job run cdl_seo_daily --preview
```

Suggested structured tools: `job_status`, `job_pause`, `job_resume`, `cdl_article_inventory`, `cdl_article_validate`, `cdl_article_save_draft`, and `cdl_article_publish_approved`. The last tool accepts an article/version ID; it looks up verified approval itself. An LLM-supplied `approved: true` is never sufficient.

Separate the scheduler, writer, review processor, and publisher. The scheduler uses clocks and persisted state, not model reasoning. The writer sees research tools and a draft-only content client. The publisher rechecks immutable approval and quality using its own credentials. Keep human foreground tasks responsive through a separate `SEO_LLM_PROVIDER/MODEL/API_BASE` route or a shared queue that gives foreground work priority. Limit SEO generation concurrency to one initially. Treat model outages as resumable blocked work; never mark a missing batch complete.

Use a unique key `(job_id, local_date)` and five numbered slots. Store retry counts and leases. Workers claim slots transactionally; after a crash, expired leases return to reconciliation. Never reset the daily count or outbox on startup. A retry resumes the same article ID. Changes requested by a reviewer create a version of that article, not an extra new daily slot.

State flow:

```text
scheduled → researching → drafting → validating → awaiting_review
awaiting_review → changes_requested → validating → awaiting_review
awaiting_review → approved → publishing → deploy_pending → live
any active stage → blocked / paused / review_conflict
```

Receiving a rejection archives only that proposal. Receiving nothing leaves it waiting. Store and expose next-run time, today's draft count, pending-review count, active step, last error, last successful model call, and latest live URLs. A1's heartbeat can report these fields without driving the work.

## Startup, restart, and emergency stop

For this workstation, a user systemd service is the straightforward option. `loginctl show-user aisurvivor -p Linger` reports `Linger=yes`, so a user service can be configured for boot without an interactive login. The session could not connect to the user service-manager bus; whether an A1 unit is currently enabled/running could not be verified.

The repository's existing `aone-services.service` points to `/home/john/A1/...` and a Thor Tailscale address, not this checkout. It is a one-shot container-start helper. Do not install it unchanged for `/home/aisurvivor/A1-agent`.

Proposed service, AFTER the module exists and has been tested:

```ini
[Unit]
Description=A1 persistent job scheduler

[Service]
Type=simple
WorkingDirectory=/home/aisurvivor/A1-agent
ExecStart=/home/aisurvivor/A1-agent/.venv/bin/python -m job_runtime.daemon
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=15
KillMode=control-group
TimeoutStopSec=5
UMask=0077

[Install]
WantedBy=default.target
```

Have the app load secrets through its existing configuration loader and retry unavailable network services with bounded backoff. Do not run dependency installation every time the machine boots. Store job files outside transient checkout/container layers. Alternatively, extend the existing Docker deployment with a persisted job-state volume and run a single scheduler there; do not independently schedule the same job on Thor and the workstation.

The long-running daemon can sleep until its next scheduled run or email-poll event. It does not keep a model generating continuously. A persistent systemd calendar timer plus one-shot workers is another valid design, but approval polling/publication also needs an event handler. Use one scheduling owner, not both competing schedules.

At shutdown, cancel workers and save state. At startup, reconcile uncertain external requests. Persist `paused=true` before killing workers when an emergency stop is requested. A restarted service must honor that flag. Terminal Esc, a CLI stop command, and an authenticated API stop route must all signal the daemon, not only the terminal's own process. Current heartbeat pause is process-local and does not meet this requirement.

Local systemd service/timer manuals were available at `/usr/share/man/man5/systemd.service.5.gz` and `systemd.timer.5.gz`; no unit was installed or enabled.

## Receiving edits and sending reliably

For a machine without a public HTTPS callback, start with AgentMail polling every five minutes: list new messages, fetch only unseen ones, and use a durable message cursor plus message-ID deduplication. While there is no mail, there are no LLM calls. Retain a small overlap window and follow pagination so outages do not lose reviews. Query the exact inbox/thread rather than treating all received mail as task instructions.

A1 currently lacks an attachment-fetch method. Add [Get Attachment](https://docs.agentmail.to/api-reference/inboxes/messages/get-attachment), preserve original bytes and their hash, and fetch fresh signed download URLs when needed. AgentMail also exposes [extracted reply/attachment text](https://docs.agentmail.to/reply-extraction). Use extracted replies to avoid quoted approvals, but never treat lossy document text extraction as proof of an exact final approved layout/content. Reject unsupported or ambiguous formats; do not execute attachments or embedded macros.

For an always-on public receiver, signed [AgentMail message.received webhooks](https://docs.agentmail.to/api-reference/webhooks/events/message-received) are an alternative. Verify the raw payload signature/timestamp using the documented API webhook scheme; do not confuse it with the separate MCP-events scheme. Deduplicate events, then validate sender identity and the article/version binding. Polling authenticated provider APIs does not by itself prove the claimed From address is genuine either. Use authenticated review links if trusted inbound-authentication data is insufficient.

Maintain an outbox per article version and delivery attempt. Before sending, persist the intent and correlation ID; after sending, persist message/thread IDs. A crash between the provider accepting mail and recording the response is ambiguous: inspect sent messages for the correlation ID before retrying. Confirm any provider idempotency support before claiming exactly-once delivery. Unresolved outcomes become `delivery_uncertain`, not an automatic resend storm. Track bounces/delivery status separately from API acceptance.

Publishing has the same uncertainty problem: look up the existing slug, compare the approved content and status, and then reconcile. If already published identically, proceed to deploy verification. If different, stop for a conflict instead of overwriting it.

## Implementation sequence and evidence required

1. Fix article validation/approval paths, sync pagination and atomic snapshotting, and deployment change detection in the CDL project. Test against isolated storage.
2. Build durable job/state/outbox and a headless runner in A1. Load `context/CDL_SEO_WORKFLOW.md` directly for this job; do not depend on a few semantic-memory snippets.
3. Add draft/publish client tools and attachment-aware review ingestion. Validate the exact approved version through the whole pipeline.
4. Generate one complete five-article review batch locally, with current source verification and duplicate checks. Review it before enabling scheduled delivery.
5. Confirm the sender inbox, reviewer policy, time zone/time, writing route, and deploy health. Send the review batch only within the activated workflow's authorization, then process a controlled approval/edit round trip.
6. Install the service and enable the job after its behavior is reviewed. Confirm boot recovery, pause persistence, and public-page verification.

Required tests include: duplicate startup does not create a second batch; DST does not duplicate a day; offline catch-up creates at most one due batch; approval without identity/version proof fails; quoted/stale approval fails; edit invalidates approval; final attachment survives publication unchanged; both-reviewer policy works if selected; conflicting reviews pause; repeated inbound events are harmless; send timeout does not blindly resend; publish timeout does not duplicate; 201+ articles are all retained; partial inventory fetch cannot delete files; failed deployment is not marked live; no model calls while waiting; emergency pause survives reboot and blocks publishing.

Open choices are schedule and one-versus-two-reviewer approval. Proposed values are 08:00 America/Chicago and either reviewer, pending the user's answer. Select a sender and a healthy writing model during implementation. The last heartbeat work exposed local Ollama generation timeouts; do not assume the installed small model is adequate for unattended article writing.
