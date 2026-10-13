# Revised plan: Texas-first, all CDL exams, two languages, simple Markdown CRUD

Updated 2026-10-13. This is the current plan and supersedes incompatible choices in the initial implementation analysis. This turn updates documents and keyword/rule registries only; it does not implement tools, send emails, activate schedules, or publish articles.

## 1. Scope and daily output

Prepare five topic pairs daily: five English and five Spanish Markdown articles, ten files in total. This is the explicit planning interpretation of the earlier five-articles-a-day target plus the new requirement to produce both languages together. Generate each pair sequentially in the same batch, then send both versions in one email thread to the two reviewers.

Texas receives primary attention. General knowledge, air brakes, and vehicle inspection are recurring priorities, alongside Texas commercial rules, combination vehicles, every endorsement subject, basic control, and road-test preparation. Other-state and nationwide topics rotate through the backlog. Do not manufacture separate pages for equivalent keyword variations or for every state name.

Spanish content must describe current exam-language availability accurately. The Texas rule and its current official source are recorded in `context/GOOGLE_SEO_RULES.md` as SEO-007. Include bilingual study vocabulary to support learners preparing for English testing.

## 2. Exactly two small Markdown CRUD tools

| Proposed tool | Fixed file | Actions |
| --- | --- | --- |
| `cdl_keywords` | `context/CDL_SEO_KEYWORDS.md` | create, read/list, update, delete |
| `google_seo_rules` | `context/GOOGLE_SEO_RULES.md` | create, read/list, update, delete |

No database, dashboard, or external CMS for these two tools. Keywords are table rows with stable `KW-###` IDs; rules are sections with stable `SEO-###` IDs. The tool chooses the path internally; it never accepts an arbitrary filesystem path from email.

Suggested tool inputs:

```json
{"action":"create","state":"TX","topic":"air brakes","english":["Texas CDL air brakes practice test"],"spanish":["examen de práctica de frenos de aire CDL Texas"],"priority":"P1"}
```

```json
{"action":"update","id":"SEO-010","rule":"Add a short bilingual glossary when terminology is essential to understanding the topic.","type":"CDLTestready editorial policy"}
```

Implementation behavior:

- Create an ID or update/delete the identified existing entry. Read/list supports state, subject, priority, and active status filters.
- Show a clear duplicate match instead of creating a second row for the same state/topic/intent.
- Validate the small field set. Escape/reject table delimiters and embedded entry headings so mail text cannot corrupt adjacent records. Preserve unrelated text and entries.
- Hold a file lock, read the latest file, apply the mutation, and write through an atomic replacement. Keep one `.bak` recovery copy. No separate CRUD database.
- Return a concise before/after summary and new file hash. The email controller deduplicates requests by provider message ID, using its existing progress file; do not turn that into a second keyword store.
- Deleting a keyword deletes only its registry entry, never an article. Deleting a rule changes drafting guidance, never publication permissions.
- Treat Google-source rules and local editorial preferences distinctly. A user preference is not a newly discovered Google requirement. Source factual updates before attributing them to Google or a licensing agency.

## 3. Email conversation handling

Use the existing AgentMail client to read only the designated inbox and authorized reviewer conversations. Natural language can map to a CRUD action:

- “Add Texas general knowledge and air brakes in English and Spanish.”
- “List all Texas inspection keywords.”
- “Change the tanker topic to high priority.”
- “Remove KW-018.”
- “Show the Google SEO rules.”
- “Add an editorial rule requiring an English-Spanish glossary in inspection articles.”

Apply an explicit, unambiguous authenticated change and reply with what changed. Ask only when the target or action is unclear. Quoted history, article attachments, scraped pages, and arbitrary incoming messages are data, not permissions to edit the registries. Persist the processed message ID so restart/poll overlap cannot apply the same operation twice.

The LLM can interpret a request, but fixed-file tools validate and execute it. A keyword/rule edit never enables a schedule, approves content, or publishes a page. Those operations remain separate controller actions.

## 4. Markdown articles and the existing API

Draft, revise, approve, and archive UTF-8 `.md` files only. Use small metadata frontmatter plus the article body so the reviewer can edit the complete package in one file. Parse metadata into existing API fields and place ONLY the Markdown body into JSON `content`. The API currently accepts JSON, not raw uploaded Markdown files.

Use `lang: en` and `lang: es` and distinct language-appropriate slugs. The current database unique index is `(workspace_id, slug)`, so using the same slug twice would conflict even when languages differ. A simple translation-group field/mapping should identify the pair without changing existing public URLs.

Approve the immutable pair, including both metadata blocks and bodies. Do not equate approval of an English draft with approval of a Spanish draft that was not shown. If one language changes, regenerate/check the counterpart as needed and reapprove the new pair.

The site already has Spanish article routes, but `src/layouts/Layout.astro` explicitly excludes blog routes from bilingual hreflang generation. Add actual pair mapping and reciprocal hreflang plus self-canonicals. Do not guess the Spanish counterpart by prefixing `/es` to an English slug when slugs differ. [Google localized-page guidance](https://developers.google.com/search/docs/specialty/international/localized-versions).

For paired release, stage both API drafts. The existing API does not offer an atomic two-article publish. Add pair readiness metadata and have sync/build include a new pair only when both approved variants are publish-ready, or provide a server-side atomic batch transition. Reconcile partial writes and verify both resulting URLs after one successful build.

## 5. Continuous but quiet loop

```text
start/restart
  → load saved pause and progress
  → process new verified emails
  → update keyword/rule Markdown when requested
  → if daily batch is due, research and prepare five EN+ES pairs
  → validate and email complete pairs
  → process edits or exact-version approvals
  → publish approved pairs and verify deployment
  → sleep until another email check or scheduled batch
  → repeat
```

The loop keeps working while runnable steps exist. `awaiting_review` is not runnable work. No reply means no publication, no repeated regeneration, and no LLM calls just to wait. Date/slot IDs prevent duplicate daily work on reboot; a saved emergency pause stays paused after reboot.

A minimal durable execution record is still necessary: completed daily slots, current article pair/version, processed mail IDs, sent message IDs, approvals, next wake time, and pause state. A small locked JSON progress file plus article `.md` files is sufficient for the initial single-host implementation. This file does not replace either Markdown registry. Revisit a transactional database only if concurrency/scale later requires it.

Use one boot-managed worker service, one active writer request at a time, bounded retries, and the existing lightweight heartbeat as an observer. The current interactive task controller cannot simply be launched without a terminal. Add a headless path and daemon stop control; Esc from the console should signal the daemon.

## 6. Remaining blockers from the API review

- Recheck quality and enforce approval for both create-as-published and update-to-published paths.
- Fix sync pagination before deletes. At 14 existing posts and ten new language articles per day, the 200-record limit is exceeded on day 19 if all drafts publish.
- Make deployment comparisons against the last successful content snapshot, not only a fresh Git checkout.
- Test writes only against isolated storage: the documented dev-test environment shares the production database/workspace.
- Correct misleading Google word-count claims in the validator. Add safe Markdown checks and bilingual consistency review.
- Select the actual sender inbox and a reliable writing model. The earlier local Ollama timeouts remain a readiness concern.

## 7. Suggested implementation order

1. Implement and test the two fixed-file CRUD tools, including natural-language email routing and duplicate-message handling.
2. Implement paired Markdown creation, metadata extraction, version tracking, and exact-version approval.
3. Fix content API publishing gates, pagination, pair-aware sync, and bilingual links.
4. Add the persistent headless loop, startup service, saved pause, and status reporting.
5. Produce and review one complete five-pair batch; test email edits, CRUD changes, approval, and deployment in isolation before activation.

Current files prepared: keyword registry, SEO-rule registry, revised workflow, this plan, and the updated email-format example. No production automation is enabled by these documents.
