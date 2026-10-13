# Google SEO guidance and CDLTestready editorial rules

Updated: 2026-10-13. Plain Markdown source of truth for the proposed `google_seo_rules` CRUD tool. Editing this file changes drafting guidance only; it cannot enable jobs, change reviewers, remove publishing approval, or grant credentials. The tool is not implemented yet.

Entries distinguish published Google guidance from CDLTestready editorial policy. A user-created preference must not be attributed to Google without an official supporting source. Recheck linked guidance when updating it.

## SEO-001 — Helpful, accurate answers

Type: Google guidance
Status: active
Rule: Write for learners, answer the page's question clearly, and contribute useful explanation beyond a summary of other pages. Do not use a preferred word count as a Google requirement.
Source: https://developers.google.com/search/docs/fundamentals/creating-helpful-content

## SEO-002 — Useful AI-assisted content

Type: Google guidance
Status: active
Rule: AI-assisted drafting must add value for readers. Avoid producing many low-value pages mainly to manipulate search rankings. Five topic pairs per day is a production target, not a ranking signal.
Source: https://developers.google.com/search/docs/fundamentals/using-gen-ai-content
Source: https://developers.google.com/search/docs/essentials/spam-policies

## SEO-003 — Titles and descriptions

Type: Google guidance
Status: active
Rule: Use unique, concise, descriptive titles and page-specific descriptions. Do not keyword-stuff. Character targets can be local editing preferences, but are not fixed Google limits.
Source: https://developers.google.com/search/docs/appearance/title-link
Source: https://developers.google.com/search/docs/appearance/snippet

## SEO-004 — Bilingual pages

Type: Google guidance
Status: active
Rule: Give English and Spanish versions separate URLs and explicit language annotations. Link the actual counterpart pages with reciprocal hreflang entries, including self references. Each page should use an appropriate self-canonical, rather than treating its translation as the canonical original.
Source: https://developers.google.com/search/docs/specialty/international/localized-versions

## SEO-005 — Honest article metadata

Type: Google guidance
Status: active
Rule: Article/BlogPosting markup must describe the visible article honestly, including author and dates. Validate the markup; eligibility does not guarantee indexing or a special search appearance.
Source: https://developers.google.com/search/docs/appearance/structured-data/article

## SEO-006 — CDL sources and jurisdiction

Type: CDLTestready editorial policy
Status: active
Rule: Verify procedures, numbers, fees, test availability, and eligibility against current FMCSA and state licensing sources. Distinguish federal requirements, state rules, and testing-location differences. Do not present expired waivers as current policy.
Source: https://www.fmcsa.dot.gov/registration/commercial-drivers-license/drivers

## SEO-007 — Texas testing language

Type: Texas factual requirement for editorial accuracy
Status: active
Rule: Texas DPS states that CDL knowledge exams have been English-only since June 1, 2026; skills tests are also in English. Spanish articles should help learners understand concepts and English testing vocabulary without claiming that the official tests are offered in Spanish. Reverify before publication.
Source: https://www.dps.texas.gov/section/driver-license/how-do-i-apply-commercial-driver-license

## SEO-008 — English and Spanish together

Type: CDLTestready editorial policy
Status: active
Rule: Prepare both language versions of each selected topic in the same batch. Localize query wording and explanations naturally, verify that facts agree, and include useful English/Spanish terminology. Both documents must be complete Markdown files before a review email is sent.

## SEO-009 — Confidence without guarantees

Type: CDLTestready editorial policy
Status: active
Rule: Help learners prepare confidently for all CDL exams: core knowledge, air brakes, vehicle inspection, commercial rules where applicable, combination vehicles, endorsements, basic control, and road testing. Use explanations and realistic readiness checks. Do not guarantee passing, claim official exam questions, fabricate experience, or imply that online preparation replaces required training.

## SEO-010 — Relevant links and original practice

Type: CDLTestready editorial policy
Status: active
Rule: Add relevant working internal links and original practice examples with explanations. Link to actual available features only. Keep official references near the factual claims they support; do not copy a competitor's question bank.

## SEO-011 — Avoid duplicate topic pages

Type: CDLTestready editorial policy
Status: active
Rule: Match keywords to intent and existing URLs. Prefer an approved update when a page already covers the topic. State variants require meaningful local information, not only a swapped state name.

## SEO-012 — Markdown-only articles

Type: CDLTestready editorial policy / API integration requirement
Status: active
Rule: Store and exchange articles as UTF-8 `.md` files. The API receives Markdown body text in its JSON `content` field, with title, slug, description, excerpt, dates, tags, and language as separate fields. Never place file frontmatter inside `content`. No DOCX/PDF article workflow is planned.

## Proposed email CRUD examples

- “Show me all SEO rules.”
- “Add an editorial rule: every inspection article includes an English-Spanish vocabulary table.”
- “Update SEO-003: use shorter descriptions as our editorial preference.”
- “Delete our custom rule SEO-010.”

The proposed tool creates, reads, updates, or deletes identified sections in this file. Clearly requested changes from verified reviewers are applied with a short before/after email summary. Ambiguous requests need clarification. This file does not contain or control publishing authorization.
