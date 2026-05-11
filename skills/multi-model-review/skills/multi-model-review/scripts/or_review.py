#!/usr/bin/env python3
"""
OpenRouter parallel multi-model query helper.

Usage:
    python or_review.py --models "openai/gpt-4o,google/gemini-2.5-pro-preview" \\
                        --prompt "Review this code: ..." \\
                        [--system "You are an expert code reviewer..."]

Output:
    JSON dict mapping model IDs to their response strings.
    Errors per model are included inline as "ERROR: ..." strings.

Requires:
    OPENROUTER_API_KEY environment variable.
    httpx  (pip install httpx)
"""
import asyncio
import argparse
import json
import os
import sys

try:
    import httpx
except ImportError:
    print(json.dumps({"error": "httpx not installed. Run: pip install httpx"}))
    sys.exit(1)

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


async def query(
    client: httpx.AsyncClient,
    model: str,
    prompt: str,
    system: str | None,
) -> tuple[str, str]:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        r = await client.post(
            BASE_URL,
            headers={
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                "X-Title": "Multi-Model Review",
            },
            json={"model": model, "messages": messages},
            timeout=120.0,
        )
        r.raise_for_status()
        return model, r.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        return model, f"ERROR {e.response.status_code}: {e.response.text[:300]}"
    except Exception as e:
        return model, f"ERROR: {e}"


async def main() -> None:
    ap = argparse.ArgumentParser(description="Query multiple OpenRouter models in parallel")
    ap.add_argument("--models", required=True, help="Comma-separated model IDs")
    ap.add_argument("--prompt", required=True, help="User prompt / content to review")
    ap.add_argument("--system", default=None, help="System prompt (optional)")
    args = ap.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(json.dumps({"error": "OPENROUTER_API_KEY environment variable not set"}))
        sys.exit(1)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if not models:
        print(json.dumps({"error": "No valid model IDs in --models"}))
        sys.exit(1)

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[query(client, model, args.prompt, args.system) for model in models]
        )

    print(json.dumps(
        {model: response for model, response in results},
        indent=2,
        ensure_ascii=False,
    ))


asyncio.run(main())
