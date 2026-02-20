"""Deep Dive — research agent that searches the web and synthesizes briefings."""

import json
import os
import sys
from datetime import datetime

import anthropic
import httpx

BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

client = anthropic.Anthropic()


def send(msg: dict) -> None:
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def log(text: str) -> None:
    print(text, file=sys.stderr, flush=True)


def brave_search(query: str, count: int = 8) -> list[dict]:
    """Search the web via Brave Search API."""
    try:
        resp = httpx.get(
            BRAVE_SEARCH_URL,
            params={"q": query, "count": count},
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": BRAVE_API_KEY,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
            })
        return results
    except Exception as e:
        log(f"Search error: {e}")
        return []


def research(query: str, message_id: str) -> str:
    """Search the web, then synthesize a briefing with Claude."""
    send({
        "type": "activity",
        "tool": "brave_search",
        "description": f"Searching: {query}",
        "message_id": message_id,
    })

    results = brave_search(query)

    if not results:
        return "I couldn't find any results for that query. Try rephrasing?"

    sources_block = "\n\n".join(
        f"[{i+1}] {r['title']}\nURL: {r['url']}\n{r['description']}"
        for i, r in enumerate(results)
    )

    send({
        "type": "activity",
        "tool": "thinking",
        "description": "Synthesizing briefing...",
        "message_id": message_id,
    })

    today = datetime.now().strftime("%B %d, %Y")

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        system=(
            f"You are Deep Dive, a research assistant. Today is {today}. "
            "The user asked a question and you searched the web. "
            "Synthesize the search results into a clear, well-structured briefing. "
            "Include inline citations like [1], [2] etc. referencing the sources. "
            "End with a Sources section listing each numbered source with its URL. "
            "Be concise but thorough. Use markdown formatting."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Question: {query}\n\n"
                f"Search results:\n{sources_block}"
            ),
        }],
    )

    return response.content[0].text


def main():
    send({"type": "ready"})
    log("Deep Dive ready")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        if msg["type"] == "shutdown":
            log("Shutting down")
            break

        if msg["type"] == "message":
            mid = msg["message_id"]
            query = msg["content"]

            try:
                result = research(query, mid)
                send({
                    "type": "response",
                    "content": result,
                    "message_id": mid,
                    "done": True,
                })
            except Exception as e:
                log(f"Error: {e}")
                send({
                    "type": "error",
                    "error": str(e),
                    "message_id": mid,
                })
                send({
                    "type": "response",
                    "content": f"Something went wrong: {e}",
                    "message_id": mid,
                    "done": True,
                })


if __name__ == "__main__":
    main()
