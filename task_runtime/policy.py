# Planning permits only known observational operations. Shell is deliberately
# excluded: the legacy shell allowlist includes write-capable command options.
READ_ONLY = {"web_search", "memory_search", "project_read", "cdl_keywords", "google_seo_rules", "cdl_articles"}


def enforce(name):
    from store import store
    if store.get("mode") == "plan" and name not in READ_ONLY:
        raise PermissionError(f"Plan mode blocks tool: {name}")
