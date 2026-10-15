# CDLTestReady article tool

This is a thin HTTP client. The exam API owns the instructions and supported
article actions; A1 does not duplicate that workflow in its prompt.

Set these in A1's `.env` and restart:

```text
CDL_ARTICLE_API_URL=http://127.0.0.1:8136
CDL_ARTICLE_WORKSPACE=article_local
CDL_ARTICLE_ADMIN_TOKEN=local-article-test-token
```

The values above are local-only. Production requires the deployed API URL and
its private admin token. Never put that token into tool arguments or prompts.

```text
/cdl_articles {}
/cdl_articles {"action":"list"}
/cdl_articles {"action":"get","slug":"reviewed-article-en"}
/cdl_articles {"action":"publish","slug":"reviewed-article-en"}
```

Model instructions/list/get work in plan mode; model mutations require execution
mode. Direct console commands are explicit user actions in either mode.
Publication requires authorization for the actual content. Daily SEO still
writes local drafts; the agent uses this tool to submit and publish reviewed
content. A successful publish means the article API stores published content.
The website's existing deployment job must sync/build before the page is live.

## Local end-to-end test

1. In the website branch run `scripts/local_stack.sh start` in a terminal.
   It uses Docker MongoDB on 127.0.0.1:27037, a dedicated database, and API :8136.
2. In this A1 checkout launch the real API in another terminal:

```bash
CDL_ARTICLE_API_URL=http://127.0.0.1:8136 \
CDL_ARTICLE_WORKSPACE=article_local \
CDL_ARTICLE_ADMIN_TOKEN=local-article-test-token \
HEARTBEAT_ENABLED=false python -m uvicorn api:app --host 127.0.0.1 --port 8137
```

3. Run `python -m lib.features.cdl_articles.e2e` with A1's installed dependencies.
   This uses real HTTP through A1's dispatcher and the exam API into local MongoDB.
   It covers both languages, draft invisibility, read/update/delete, invalid
   input, authorization, tenant isolation, duplicate create, and publish replay.
   It deletes only its uniquely named test articles.
4. `python -m lib.features.cdl_articles.preview` creates two local review articles.
   Follow the website branch's `lib/features/article_agent/README.md` to sync,
   build, and serve the local review pages. No production API is used.
