#!/usr/bin/env python3
"""
OpenRouter parallel multi-model query helper.

Usage:
    # Recommended — preset handles models + system prompt:
    python or_review.py --preset code --file myfile.py
    cat myfile.py | python or_review.py --preset security

    # List presets:
    python or_review.py --list-presets

    # Custom models (--system optional, defaults to None):
    python or_review.py --models "openai/gpt-5.5,google/gemini-3.1-pro-preview" \\
                        --prompt "Review this..." \\
                        --system "You are an expert..."

Output (JSON):
    {
      "results": { "<model-id>": { "content", "elapsed_s", "prompt_tokens",
                                   "completion_tokens", "cost_usd" } },
      "meta":    { "preset", "models", "total_elapsed_s", "total_prompt_tokens",
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

try:
    import httpx
except ImportError:
    print(json.dumps({"error": "httpx not installed. Run: pip install httpx"}))
    sys.exit(1)

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

PRESETS: dict[str, dict] = {
    "code": {
        "models": ["anthropic/claude-opus-4.7", "openai/gpt-5.5"],
        "system": "You are an expert code reviewer. Analyze for: bugs, edge cases, security issues, performance problems, and maintainability. Reference specific constructs or line areas. Rate each finding: Critical / Warning / Suggestion.",
    },
    "code-web": {
        "models": ["anthropic/claude-opus-4.7", "google/gemini-3.1-pro-preview"],
        "system": "You are an expert UI/web engineer. Review for: component correctness, state bugs, unnecessary re-renders, accessibility (WCAG 2.2), layout edge cases, and browser compatibility. Rate each finding: Critical / Warning / Suggestion.",
    },
    "code-sql": {
        "models": ["anthropic/claude-opus-4.7", "google/gemini-3.1-pro-preview"],
        "system": "You are a database engineer fluent in Postgres, BigQuery, Snowflake, and MySQL. Review for: query correctness, NULL semantics, cartesian join risk, implicit type coercions, missing indexes, and dialect-specific pitfalls. Flag any query that silently returns wrong results. Rate: Error / Warning / Note.",
    },
    "code-cli": {
        "models": ["openai/gpt-5.5", "anthropic/claude-opus-4.7"],
        "system": "You are a senior backend/systems engineer. Review for: API contract correctness, race conditions, improper error propagation, N+1 queries, missing idempotency, resource leaks, and scalability bottlenecks. Rate: Critical / Warning / Suggestion.",
    },
    "code-live": {
        "models": ["openai/gpt-5.5", "google/gemini-3.1-pro-preview"],
        "system": "You are an expert code reviewer focused on algorithmic correctness. Analyze for: logic errors, off-by-one errors, edge cases (empty input, overflow, underflow), incorrect complexity, and subtle bugs. Rate: Critical / Warning / Suggestion.",
    },
    "budget": {
        "models": ["moonshotai/kimi-k2.6", "deepseek/deepseek-v4-pro"],
        "system": "You are an expert code reviewer. Analyze for: bugs, edge cases, security issues, performance problems, and maintainability. Reference specific constructs or line areas. Rate each finding: Critical / Warning / Suggestion.",
    },
    "security": {
        "models": ["google/gemini-3.1-pro-preview", "anthropic/claude-opus-4.7"],
        "system": "You are a security engineer. Analyze for vulnerabilities: injection attacks, auth flaws, sensitive data exposure, cryptographic weaknesses, missing input validation, OWASP Top 10. Each finding: severity (Critical / High / Medium / Low) + remediation step.",
    },
    "arch": {
        "models": ["google/gemini-3.1-pro-preview", "anthropic/claude-sonnet-4.6"],
        "system": "You are a senior software architect. Review for: separation of concerns, scalability bottlenecks, tight coupling, missing abstractions, operational gaps (observability, failure modes). Call out tradeoffs explicitly.",
    },
    "writing": {
        "models": ["anthropic/claude-sonnet-4.6", "openai/gpt-5.5"],
        "system": "You are a professional editor. Review for: clarity, logical flow, tone consistency, unsupported claims, and structural weaknesses. Distinguish must-fix from polish.",
    },
    "math": {
        "models": ["openai/o4-mini-high", "google/gemini-3.1-pro-preview"],
        "system": "You are an expert mathematician and scientist. Check every logical step, formula, proof, or derivation. Flag: incorrect reasoning chains, wrong assumptions, unit errors, missing edge cases, and claims that lack justification. Rate each finding: Error / Warning / Note.",
    },
    "docs": {
        "models": ["google/gemini-3.1-pro-preview", "openai/gpt-5.5"],
        "system": "You are a meticulous analyst reviewing a long document. Identify: internal contradictions, unsupported claims, missing sections, logical gaps, and any conclusions that do not follow from the evidence. Cite the specific location of each finding.",
    },
    "translate": {
        "models": ["openai/gpt-5.5", "google/gemini-3.1-pro-preview"],
        "system": "You are a professional translator and linguist. Review this translation for: accuracy of meaning, idiomatic naturalness in the target language, register consistency, cultural appropriateness, and any omissions or additions versus the source. Rate: Critical mistranslation / Awkward phrasing / Style suggestion.",
    },
    "creative": {
        "models": ["anthropic/claude-sonnet-4.6", "google/gemini-3.1-pro-preview"],
        "system": "You are a literary editor with deep genre expertise. Evaluate this creative writing for: narrative momentum, character consistency, dialogue authenticity, show-vs-tell balance, sensory grounding, and tonal control. Distinguish structural issues from line-level suggestions.",
    },
    "quick": {
        "models": ["openai/gpt-4.1-mini", "google/gemini-3.1-flash-lite"],
        "system": "Review the following and identify the most important issues. Be concise and direct.",
    },
    "free": {
        "models": ["openrouter/free", "openrouter/free"],
        "system": "Review the following and identify the most important issues. Be thorough but concise.",
    },
}


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
            json={"model": model, "messages": messages, "max_tokens": max_tokens},
            timeout=timeout,
        )
        r.raise_for_status()
        elapsed = round(time.monotonic() - start, 2)
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        cost = usage.get("cost") or usage.get("total_cost")
        result = {
            "content": content,
            "elapsed_s": elapsed,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "cost_usd": cost,
        }
        print(f"  ✓ {model} ({elapsed:.1f}s)", file=sys.stderr)
        return model, result

    except httpx.HTTPStatusError as e:
        elapsed = round(time.monotonic() - start, 2)
        if e.response.status_code == 429 and _attempt == 0:
            print(f"  ↺ {model} rate-limited, retrying in 5s...", file=sys.stderr)
            await asyncio.sleep(5)
            return await _query(client, model, prompt, system, max_tokens, timeout, _attempt=1)
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
        epilog="Available presets: " + ", ".join(PRESETS.keys()),
    )
    ap.add_argument(
        "--preset",
        choices=list(PRESETS.keys()),
        metavar="PRESET",
        help="Built-in preset (sets models + system prompt). Choices: " + ", ".join(PRESETS.keys()),
    )
    ap.add_argument("--models", help="Comma-separated model IDs (overrides preset models)")
    ap.add_argument("--system", help="System prompt (overrides preset system prompt)")
    ap.add_argument("--prompt", help="Content to review (or use --file / pipe via stdin)")
    ap.add_argument("--file", help="Path to file to review")
    ap.add_argument("--max-tokens", type=int, default=2000, metavar="N", help="Max tokens per model response (default: 2000)")
    ap.add_argument("--timeout", type=float, default=120.0, metavar="SEC", help="Request timeout in seconds (default: 120)")
    ap.add_argument("--list-presets", action="store_true", help="List presets with their models and exit")
    args = ap.parse_args()

    if args.list_presets:
        col = max(len(k) for k in PRESETS)
        for name, cfg in PRESETS.items():
            print(f"  {name:{col}}  {', '.join(cfg['models'])}")
        sys.exit(0)

    # Resolve content
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
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
    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
        system = args.system or (PRESETS[args.preset]["system"] if args.preset else None)
    elif args.preset:
        models = PRESETS[args.preset]["models"]
        system = args.system or PRESETS[args.preset]["system"]
    else:
        ap.error("Either --preset or --models is required")

    if not models:
        print(json.dumps({"error": "No valid model IDs provided"}))
        sys.exit(1)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(json.dumps({"error": "OPENROUTER_API_KEY environment variable not set"}))
        sys.exit(1)

    label = args.preset or "custom"
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
                "preset": args.preset,
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
