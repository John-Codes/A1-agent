# Daily SEO

enabled: false
content_title: CDL daily SEO
author: Sergio
keywords:
pairs_per_day: 5
timezone: America/Chicago

Each slot creates one English and one Spanish Markdown draft for human review.
content_title defines what the content is about. keywords accepts comma-separated
target phrases. Each phrase becomes one topic pair; blank uses the keyword registry.
Run /seo start in A1 to enable. Settings are reread every 15 seconds.
The daily quota resets at midnight in the timezone above; missed days are skipped.
Keywords live in CDL_SEO_KEYWORDS.md; editorial guidance in GOOGLE_SEO_RULES.md.
Each active keyword is used once, avoiding duplicate articles. Add new topics as needed.
Failed/interrupted slots count toward the quota and are not automatically retried.
