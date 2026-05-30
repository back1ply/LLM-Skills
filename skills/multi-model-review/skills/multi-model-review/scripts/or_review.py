#!/usr/bin/env python3
"""
OpenRouter parallel multi-model query helper.

Usage:
    python or_review.py --models "openai/gpt-5.5,anthropic/claude-opus-4.8" \\
                        --file myfile.py \\
                        --system "Check for race conditions and resource leaks."

    cat myfile.py | python or_review.py \\
                        --models "deepseek/deepseek-v4-pro,moonshotai/kimi-k2.6" \\
                        --system "Security audit — OWASP Top 10."

    # No system prompt (general review):
    python or_review.py --models "openai/gpt-5.5,anthropic/claude-opus-4.8" --file myfile.py

Output (JSON):
    {
      "results": { "<model-id>": { "content", "elapsed_s", "prompt_tokens",
                                   "completion_tokens", "cost_usd" } },
      "meta":    { "models", "total_elapsed_s", "total_prompt_tokens",
                   "total_completion_tokens", "total_cost_usd" }
    }

Requires:
    OPENROUTER_API_KEY environment variable.
    httpx (pip install httpx)
"""
import asyncio
import argparse
import json
import os
import sys
import time

# Force UTF-8 on all stdio — Windows defaults to cp1252/cp850 which breaks
# non-ASCII content in model responses, progress symbols, and piped input.
for _s in (sys.stdin, sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except Exception:
            pass

try:
    import httpx
except ImportError:
    print(json.dumps({"error": "httpx not installed. Run: pip install httpx"}))
    sys.exit(1)

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


async def _query(
    client: httpx.AsyncClient,
    model: str,
    prompt: str,
    system: str | None,
    max_tokens: int,
    timeout: float,
    _attempt: int = 0,
) -> tuple[str, dict]:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    start = time.monotonic()
    try:
        r = await client.post(
            BASE_URL,
            headers={
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                "X-Title": "Multi-Model Review",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "include_reasoning": True,
                "transforms": ["middle-out"],
            },
            timeout=timeout,
        )
        r.raise_for_status()
        elapsed = round(time.monotonic() - start, 2)
        data = r.json()
        if "error" in data:
            err = data["error"]
            meta = err.get("metadata") or {}
            provider = meta.get("provider_name", "")
            provider_str = f" [provider: {provider}]" if provider else ""
            msg = f"ERROR {err.get('code', '?')}: {err.get('message', str(err))}{provider_str}"
            print(f"  ✗ {model}: {msg}", file=sys.stderr)
            return model, {"content": msg, "elapsed_s": elapsed}
        msg = data["choices"][0]["message"]
        content = msg["content"]
        if not content:
            if _attempt == 0:
                print(f"  ↺ {model} empty response (cold start?), retrying...", file=sys.stderr)
                return await _query(client, model, prompt, system, max_tokens, timeout, _attempt=1)
            return model, {"content": "ERROR: empty response (model cold start?)", "elapsed_s": elapsed}
        reasoning = msg.get("reasoning") or msg.get("reasoning_content")
        usage = data.get("usage", {})
        cost = usage.get("cost") or usage.get("total_cost")
        result = {
            "content": content,
            "reasoning": reasoning,
            "elapsed_s": elapsed,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "cost_usd": cost,
        }
        print(f"  ✓ {model} ({elapsed:.1f}s)", file=sys.stderr)
        return model, result

    except httpx.HTTPStatusError as e:
        elapsed = round(time.monotonic() - start, 2)
        if e.response.status_code in (429, 502, 503) and _attempt == 0:
            retry_after = e.response.headers.get("Retry-After")
            try:
                wait = float(retry_after) if retry_after else 5
            except ValueError:
                wait = 5
            print(f"  ↺ {model} {e.response.status_code}, retrying in {wait:.0f}s...", file=sys.stderr)
            await asyncio.sleep(wait)
            return await _query(client, model, prompt, system, max_tokens, timeout, _attempt=1)
        try:
            err_body = e.response.json().get("error", {})
            msg = f"ERROR {e.response.status_code}: {err_body.get('message', e.response.text[:300])}"
        except Exception:
            msg = f"ERROR {e.response.status_code}: {e.response.text[:300]}"
        print(f"  ✗ {model}: {msg}", file=sys.stderr)
        return model, {"content": msg, "elapsed_s": elapsed}

    except Exception as e:
        elapsed = round(time.monotonic() - start, 2)
        msg = f"ERROR: {e}"
        print(f"  ✗ {model}: {msg}", file=sys.stderr)
        return model, {"content": msg, "elapsed_s": elapsed}


async def main() -> None:
    ap = argparse.ArgumentParser(
        description="Query multiple OpenRouter models in parallel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--models", required=True, help="Comma-separated OpenRouter model IDs (e.g. 'openai/gpt-5.5,anthropic/claude-opus-4.8')")
    ap.add_argument("--system", help="System prompt (overrides preset system prompt)")
    ap.add_argument("--prompt", help="Content to review (or use --file / pipe via stdin)")
    ap.add_argument("--file", help="Path to file to review")
    ap.add_argument("--max-tokens", type=int, default=2000, metavar="N", help="Max tokens per model response (default: 2000)")
    ap.add_argument("--timeout", type=float, default=120.0, metavar="SEC", help="Request timeout in seconds (default: 120)")
    args = ap.parse_args()

    # Resolve content
    if args.file:
        try:
            with open(args.file, encoding="utf-8", errors="replace") as f:
                prompt = f.read()
        except OSError as e:
            print(json.dumps({"error": f"Cannot read file: {e}"}))
            sys.exit(1)
    elif args.prompt:
        prompt = args.prompt
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read()
    else:
        ap.error("Provide content via --prompt, --file, or stdin (pipe or heredoc)")

    if not prompt.strip():
        print(json.dumps({"error": "Empty input — nothing to review"}))
        sys.exit(1)

    # Resolve models + system prompt
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    system = args.system

    if not models:
        print(json.dumps({"error": "No valid model IDs provided"}))
        sys.exit(1)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(json.dumps({"error": "OPENROUTER_API_KEY environment variable not set"}))
        sys.exit(1)

    label = ",".join(models)
    print(f"Querying {len(models)} model(s) [{label}] in parallel...", file=sys.stderr)
    wall_start = time.monotonic()

    async with httpx.AsyncClient() as client:
        raw = await asyncio.gather(
            *[_query(client, m, prompt, system, args.max_tokens, args.timeout) for m in models]
        )

    total_elapsed = round(time.monotonic() - wall_start, 2)
    results: dict[str, dict] = {model: data for model, data in raw}

    total_prompt = sum(r.get("prompt_tokens") or 0 for r in results.values())
    total_completion = sum(r.get("completion_tokens") or 0 for r in results.values())
    costs = [r["cost_usd"] for r in results.values() if r.get("cost_usd") is not None]
    total_cost = round(sum(costs), 6) if costs else None

    print(json.dumps(
        {
            "results": results,
            "meta": {
                "models": models,
                "total_elapsed_s": total_elapsed,
                "total_prompt_tokens": total_prompt or None,
                "total_completion_tokens": total_completion or None,
                "total_cost_usd": total_cost,
            },
        },
        indent=2,
        ensure_ascii=False,
    ))


asyncio.run(main())
