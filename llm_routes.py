from llm_route_rows import load_default_row, load_fallback_rows, parse_route_row


def default_route():
    item = parse_route_row(load_default_row())
    return route("default", item["provider"], item["model"], item["api_base"])


def fallback_routes():
    routes = []
    for index, row in enumerate(load_fallback_rows(), start=1):
        item = parse_route_row(row)
        if item["provider"] and item["model"]:
            routes.append(route(f"fallback_{index}", item["provider"], item["model"], item["api_base"]))
    return routes


def route(label, provider, model, api_base=""):
    return {"label": label, "provider": provider, "model": model, "api_base": api_base}


def route_key(item):
    return (item["provider"], item["model"], item.get("api_base") or "")
