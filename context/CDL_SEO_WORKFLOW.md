# A1: Texas-first bilingual CDL editorial workflow

Status: PROPOSED / DISABLED. Updated 2026-10-13 following the user's revised requirements. This is a plan, not an activated job or an approval to publish any article. It supersedes the earlier English-first approach.

## Mission and scope

Help people prepare confidently for ALL CDL exams: general knowledge, air brakes, vehicle inspection/pre-trip, state commercial rules where applicable, combination vehicles, tanker, hazmat, doubles/triples, passenger, school bus, basic vehicle control, and road-test preparation. Texas is the primary audience; every other state and DC remains in scope. Do not guarantee a pass or imply online study replaces required hands-on training.

The website is https://cdltestready.com; its repository is `/home/aisurvivor/testreadycdl.com`.

Planning assumption: five TOPICS per day, each in English AND Spanish, producing ten complete `.md` articles. Generate language pairs in the same daily batch and deliver each pair together. Simultaneous model requests are unnecessary; sequential generation avoids overloading the models.

Use `context/CDL_SEO_KEYWORDS.md` for keyword selection and `context/GOOGLE_SEO_RULES.md` for drafting guidance. These are the only two Markdown registries managed by the proposed CRUD tools. Read their current contents directly before each batch; do not rely on stale embeddings.

## Recipients and schedule

Email each topic pair in one thread to BOTH:

- efexzium@gmail.com
- Frany Lz <franyr960@gmail.com>

Proposed schedule: daily generation starts at 08:00 America/Chicago, including weekends. Proposed reviewer policy: either recipient can approve a complete pair. These preferences were requested but not yet confirmed; no schedule is enabled. A verified AgentMail sender inbox must be selected during implementation.

Proposed ongoing daily mix: three Texas pairs, one other-state pair, one nationwide pair. The first core batch can use four Texas topics plus one nationwide topic. Keywords are targets, not an instruction to create duplicate articles for every variation.

## Persistent work loop

On startup, load saved progress and any persistent emergency pause. Reconcile interrupted email/API requests. Then repeat:

1. Process new authenticated reviewer emails once, using saved message IDs to avoid duplicate actions. Apply clear keyword/rule changes to the corresponding Markdown file and acknowledge the exact change. Classify article edits/approvals separately.
2. If paused, perform no new generation or publication. Wait for explicit resume.
3. If today's batch is due, claim its date and five numbered topic slots. Check the full published/draft inventory, select topics, research official sources, and generate each English/Spanish pair.
4. Validate both complete Markdown documents, their factual agreement, current sources, distinct intents, and API metadata. Save both versions before sending a review email.
5. Send five topic emails, each containing two `.md` attachments and both reviewers. Store the exact version hashes and provider thread/message IDs. Mark the pairs `awaiting_review`.
6. For a received edit, revise the requested language(s), check the counterpart for factual consistency, and send the revised pair for review. Never silently rewrite already approved text.
7. For a valid approval, recheck the publication gate, publish the approved pair through the API, and verify the resulting pages after deployment.
8. If no runnable work exists, sleep until mail polling, the next scheduled batch, or explicit user input. Waiting is not a reason to ask the model to keep thinking or generate extra drafts.

No reply means no publication and no repeated resend. The next day can produce its new batch while earlier pairs await review. After downtime, catch up at most the latest due batch, not every missed day. A date/slot key prevents duplicate batches after restart. Generate fewer pairs and report a shortfall if sources, model availability, or quality checks prevent completion.

## Markdown contract

All article drafts, revisions, and approved files are UTF-8 `.md`; no DOCX or PDF article workflow. Each file contains a small frontmatter block for the API metadata followed by the Markdown body. Each language has its own title, description, excerpt, slug, tags, and `lang: en` or `lang: es`. Metadata is checked as part of the approved version.

The publisher parses this file and sends a JSON article payload. It removes frontmatter from the `content` field: that field contains only Markdown body text. The API is not a raw `.md` upload endpoint. Website sync reconstructs frontmatter for Astro.

Use different slugs for EN and ES because the current API makes slug unique per workspace. Link the pair using a stable pair ID and a translation mapping. Expected public routes are `/blog/<english-slug>/` and `/es/blog/<spanish-slug>/`. Both pages need correct language metadata, self-canonicals, and reciprocal translation links. Current blog hreflang handling must be extended before activation.

Example filenames: `SEO-20261013-01.v1.en.md` and `SEO-20261013-01.v1.es.md`.

## Review and approval

Email subject: `[CDL Review SEO-20261013-01 v1 EN+ES] Texas CDL General Knowledge`.

The email must state that the two attachments are one review pair and that bare `APPROVED` approves both displayed versions. Include readable summaries, complete attached Markdown files, sources, keyword intent, and validation notes.

- `APPROVED BOTH` or an unambiguous `APPROVED` reply to that pair: approve both exact file hashes.
- `APPROVED EN` or `APPROVED ES`: record that language's approval, but hold publication until the pair is fully approved.
- `EDIT EN: ...`, `EDIT ES: ...`, or clear natural-language edits: create a new pair revision and return it for review. Recheck both languages when a fact changes.
- `APPROVED VERSIONS ATTACHED`: accept the two complete final `.md` files, validate without rewriting, and bind approval to their hashes. A single edited file or ambiguous metadata does not approve the unseen counterpart; request explicit approval of the assembled pair.
- `REJECT`: archive the pair.

An edit invalidates the pair's previous approval. No model-generated boolean can replace verified human approval. Record reviewer, message ID, pair/version IDs, both hashes, timestamp, and decision. Reject quoted, stale, forwarded, spoofed, ambiguous, or conflicting approvals. If sender authenticity cannot be established, use an authenticated review action.

Neither keyword CRUD nor SEO-rule CRUD can edit these approval controls, recipient permissions, credentials, schedule enablement, or emergency pause state. An instruction to add a keyword is not approval of an article.

## Publication and recovery

Only the deterministic publisher may publish. Require an enabled job, no saved pause, both current versions approved, passing validation, no conflicting edits, and a verified target workspace. Revalidate against the current active rule set without changing approved content; if changes are needed, return the pair to review.

Current API calls publish one article at a time, so a pair is not an atomic operation today. Implement a pair-aware publication/deployment gate: prepare both drafts, verify both approvals, and make the pair eligible for the same site build only when both versions are ready. Keep a partial write in `publish_partial` and reconcile it; do not claim both pages are live early.

After API acceptance use `deploy_pending`. Confirm both public pages serve their approved contents before `live`. Google indexing is a separate outcome and is not guaranteed. On an uncertain API/mail response, reconcile by slug/content or message correlation before retrying; do not blindly duplicate articles or emails.

## Model and startup behavior

Keep the 30-minute heartbeat read-only. A dedicated persistent job loop does the editorial work; it does not ask the heartbeat model to write articles. Use a capable writer with a separate route or foreground-priority request queue, and generate one pair at a time. Empty mail checks and schedule checks require no LLM calls.

Start the job service on boot and restart it after crashes. Persist progress before side effects. Esc from a controlling terminal and an authenticated daemon stop command must stop owned workers and save a pause that survives reboot. A computer that is off cannot send scheduled articles; use an always-on host for dependable timing.

The first implementation can keep job progress in a small locked/atomically written file plus saved article files. The two CRUD registries remain plain Markdown, without a keyword/rules database or a CMS.

Read the entire workflow directly for editorial tasks. The current `/plan`/`/execute` controller requires a terminal, and merely saving this file does not provide a headless daemon. See `docs/seo/REVISED_PLAN.md` for the proposed tools and changes. Implementation and activation remain pending.
