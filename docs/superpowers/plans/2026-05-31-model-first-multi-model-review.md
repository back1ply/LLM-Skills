# Model-First Multi-Model Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the preset-based interface with a natural-language model-first interface — users say "ask gpt and claude to review this" instead of picking a preset.

**Architecture:** Two files change. `or_review.py` is stripped of the `PRESETS` dict, `--preset`, and `--list-presets`; `--models` becomes required and drives everything. `SKILL.md` gets a new trigger description, a benchmark-backed model alias table, and natural-language parsing rules that map model names → OpenRouter IDs and extract task descriptions → `--system` prompts.

**Tech Stack:** Python 3.14, argparse, httpx (async), OpenRouter API, Claude Code skill system.

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Modify | `skills/multi-model-review/skills/multi-model-review/scripts/or_review.py` | Remove PRESETS, --preset, --list-presets; make --models required; clean up meta output |
| Modify | `skills/multi-model-review/skills/multi-model-review/SKILL.md` | New trigger, model alias table, parsing rules, execution instructions |
| Create | `skills/multi-model-review/skills/multi-model-review/scripts/test_or_review_args.py` | Argparse regression tests — verify old flags gone, new behaviour correct |

---

## Task 1: Write argparse regression tests (failing)

These tests verify the interface contract before touching production code.

**Files:**
- Create: `skills/multi-model-review/skills/multi-model-review/scripts/test_or_review_args.py`

- [ ] **Step 1: Create the test file**

```python
"""
Argparse contract tests for or_review.py.
Run: python -m pytest test_or_review_args.py -v
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "or_review.py"


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True,
        text=True,
    )


def test_models_required_without_it_exits_nonzero():
    """--models is now required; no --models → non-zero exit."""
    r = run(["--prompt", "hello"])
    assert r.returncode != 0


def test_preset_flag_is_gone():
    """--preset must no longer exist as a valid argument."""
    r = run(["--preset", "code", "--prompt", "hello"])
    assert r.returncode != 0
    assert "unrecognized" in r.stderr.lower() or "error" in r.stderr.lower()


def test_list_presets_flag_is_gone():
    """--list-presets must no longer exist."""
    r = run(["--list-presets"])
    assert r.returncode != 0
    assert "unrecognized" in r.stderr.lower() or "error" in r.stderr.lower()


def test_models_and_prompt_accepted():
    """--models + --prompt (no API key) should fail on missing key, not on arg parsing."""
    r = run(["--models", "openai/gpt-5.5", "--prompt", "hello"])
    # May fail due to missing OPENROUTER_API_KEY, but argparse must succeed
    # so the error must NOT be an argparse error
    assert "unrecognized arguments" not in r.stderr
    assert "invalid choice" not in r.stderr


def test_system_flag_still_works():
    """--system is still accepted (no argparse error)."""
    r = run(["--models", "openai/gpt-5.5", "--prompt", "x", "--system", "You are an expert."])
    assert "unrecognized arguments" not in r.stderr
    assert "invalid choice" not in r.stderr
```

- [ ] **Step 2: Run tests to confirm they fail against current code**

```bash
cd "skills/multi-model-review/skills/multi-model-review/scripts"
python -m pytest test_or_review_args.py -v
```

Expected output — `test_preset_flag_is_gone` and `test_list_presets_flag_is_gone` should **FAIL** (flags still exist), `test_models_required_without_it_exits_nonzero` should **FAIL** (--models currently optional):
```
FAILED test_or_review_args.py::test_models_required_without_it_exits_nonzero
FAILED test_or_review_args.py::test_preset_flag_is_gone
FAILED test_or_review_args.py::test_list_presets_flag_is_gone
PASSED test_or_review_args.py::test_models_and_prompt_accepted
PASSED test_or_review_args.py::test_system_flag_still_works
```

- [ ] **Step 3: Commit the failing tests**

```bash
git add skills/multi-model-review/skills/multi-model-review/scripts/test_or_review_args.py
git commit -m "test(multi-model-review): add argparse regression tests for model-first interface"
```

---

## Task 2: Strip presets from or_review.py

**Files:**
- Modify: `skills/multi-model-review/skills/multi-model-review/scripts/or_review.py`

- [ ] **Step 1: Replace the module docstring**

Find the current docstring (lines 1–28 approximately):
```python
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
...
"""
```

Replace with:
```python
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
```

- [ ] **Step 2: Delete the entire PRESETS dict**

Remove the block that starts with:
```python
PRESETS: dict[str, dict] = {
    "code": {
```
and ends with the closing `}` of the dict (the last entry is `"code-live"` or similar). This is approximately 60–70 lines. Delete every line from `PRESETS: dict[str, dict] = {` through the matching closing `}`.

- [ ] **Step 3: Update the argparse setup in `main()`**

Find and replace the argparse block. Current:
```python
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
```

Replace with:
```python
    ap = argparse.ArgumentParser(
        description="Query multiple OpenRouter models in parallel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--models",
        required=True,
        help="Comma-separated OpenRouter model IDs (e.g. 'openai/gpt-5.5,anthropic/claude-opus-4.8')",
    )
```

- [ ] **Step 4: Remove the `--list-presets` argument**

Delete this argument definition:
```python
    ap.add_argument("--list-presets", action="store_true", help="List presets with their models and exit")
```

- [ ] **Step 5: Remove the `--list-presets` handler block**

Delete:
```python
    if args.list_presets:
        col = max(len(k) for k in PRESETS)
        for name, cfg in PRESETS.items():
            print(f"  {name:{col}}  {', '.join(cfg['models'])}")
        sys.exit(0)
```

- [ ] **Step 6: Replace the model/system resolution block**

Find the current resolution logic:
```python
    # Resolve models + system prompt
    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
        system = args.system or (PRESETS[args.preset]["system"] if args.preset else None)
    elif args.preset:
        models = PRESETS[args.preset]["models"]
        system = args.system or PRESETS[args.preset]["system"]
    else:
        ap.error("Either --preset or --models is required")
```

Replace with:
```python
    # Resolve models + system prompt
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    system = args.system
```

- [ ] **Step 7: Update the progress label**

Find:
```python
    label = args.preset or "custom"
    print(f"Querying {len(models)} model(s) [{label}] in parallel...", file=sys.stderr)
```

Replace with:
```python
    label = ",".join(models)
    print(f"Querying {len(models)} model(s) [{label}] in parallel...", file=sys.stderr)
```

- [ ] **Step 8: Remove `preset` from the JSON meta output**

Find the JSON output block containing `"preset"`. It looks like:
```python
        {
            "results": results,
            "meta": {
                "preset": label,
                "models": models,
                ...
            },
        }
```

Remove the `"preset": label,` line only. Leave all other meta fields intact.

- [ ] **Step 9: Run the tests — all should now pass**

```bash
cd "skills/multi-model-review/skills/multi-model-review/scripts"
python -m pytest test_or_review_args.py -v
```

Expected:
```
PASSED test_or_review_args.py::test_models_required_without_it_exits_nonzero
PASSED test_or_review_args.py::test_preset_flag_is_gone
PASSED test_or_review_args.py::test_list_presets_flag_is_gone
PASSED test_or_review_args.py::test_models_and_prompt_accepted
PASSED test_or_review_args.py::test_system_flag_still_works

5 passed
```

- [ ] **Step 10: Commit**

```bash
git add skills/multi-model-review/skills/multi-model-review/scripts/or_review.py
git commit -m "feat(multi-model-review): remove presets — model-first interface

Drop PRESETS dict, --preset, --list-presets. Make --models required.
System prompt comes entirely from --system (optional). Remove preset
field from JSON meta output."
```

---

## Task 3: Rewrite SKILL.md

**Files:**
- Modify: `skills/multi-model-review/skills/multi-model-review/SKILL.md`

- [ ] **Step 1: Replace the entire file with the new content**

```markdown
---
name: multi-model-review
description: >
  Query AI models in parallel via OpenRouter and synthesize findings. Use when
  the user says "ask [model]", "get [model]'s opinion", "what does [model] think",
  "multi-model review", "get a second opinion", "council review", "validate this
  with [model]", or names any supported model alongside content to review.
  Requires OPENROUTER_API_KEY set in the environment.
when_to_use: >
  Also invoke proactively for high-stakes work — security-sensitive code,
  architecture decisions before implementation, production-bound logic, or any
  case where a single model's blind spots could cause real harm.
allowed-tools: Bash Glob
---

## multi-model-review

### Prerequisites

- `OPENROUTER_API_KEY` set in environment
- `httpx` installed: `pip install httpx`

---

### Available Models

Benchmark sources: DeepSWE (Datacurve, May 2026), SWE-bench Pro (Scale AI),
GPQA Diamond, LMArena ELO, Artificial Analysis Intelligence Index.

| Alias(es) | OpenRouter ID | Tier | Strengths |
|---|---|---|---|
| `gpt`, `gpt5`, `codex` | `openai/gpt-5.5` | Premium | DeepSWE #1 (70%), GPQA 92.8% — best overall coder |
| `opus`, `claude` | `anthropic/claude-opus-4.8` | Premium | LMArena #1, SWE-bench 88.6%, deep reasoning |
| `sonnet` | `~anthropic/claude-sonnet-latest` | Standard | Fast Anthropic, balanced quality/cost |
| `gemini` | `google/gemini-3.1-pro-preview` | Standard | GPQA #1 (94.3%), 1M ctx — best for reasoning/knowledge |
| `flash` | `google/gemini-3.5-flash` | Fast | Newest Google, fast + cheap |
| `grok` | `x-ai/grok-4.3` | Standard | Cost-efficient coding, real-time X/web data |
| `deepseek` | `deepseek/deepseek-v4-pro` | Budget | SWE-bench 80.6%, strong reasoning, low cost |
| `free` | `deepseek/deepseek-v4-flash:free` | Free | Zero cost |
| `kimi` | `moonshotai/kimi-k2.6` | Budget | Best open-weight (GPQA 87.6%) |

> **Note on Gemini for coding:** Gemini 3.1 Pro scores ~1% on DeepSWE (agentic coding benchmark)
> due to harness generalization issues. Prefer `gpt` or `opus` for code review tasks.

---

### Step 1 — Parse the request

Given the user's message:

**Extract model names** (case-insensitive, any order):
- Scan for aliases from the table above
- Map each alias → its OpenRouter ID
- If no model named → ask: *"Which models should I consult? e.g. `gpt and claude`, `deepseek and kimi`"*
- Single model is valid

**Extract the task** (becomes `--system`):
- Identify the action phrase: everything after "to [verb]", "for [noun]", "on [topic]"
- Examples:
  - `"ask gpt and claude to check for race conditions"` → task: `"check for race conditions"`
  - `"get gemini's opinion on this architecture"` → task: `"review this architecture"`
  - `"have deepseek and kimi audit for SQL injection"` → task: `"audit for SQL injection"`
  - `"ask opus and gpt"` (no task) → no `--system`
- Wrap the extracted task: `"You are an expert reviewer. [task]. Be specific, reference exact constructs, rate each finding: Critical / Warning / Suggestion."`

**Locate content:**
- File path mentioned → `--file <path>`
- Content in conversation → `--prompt "<content>"`
- Neither → ask: *"Please provide the content to review, or a file path."*

---

### Step 2 — Find the script

```python
import os
script_path = os.path.join(os.environ.get("CLAUDE_PLUGIN_ROOT", ""), 
    "skills", "multi-model-review", "scripts", "or_review.py")
```

Or locate via glob: `**/multi-model-review/scripts/or_review.py`

---

### Step 3 — Run the script

```bash
python "<script_path>" \
  --models "<openrouter-id-1>,<openrouter-id-2>" \
  [--system "You are an expert reviewer. <task>. Rate findings: Critical / Warning / Suggestion."] \
  [--file "<path>" | --prompt "<content>"]
```

Optional flags:
- `--max-tokens N` — cap response length (default 2000)
- `--timeout SEC` — request timeout (default 120)

---

### Step 4 — Synthesize responses

The script outputs JSON:
```json
{
  "results": {
    "<model-id>": {
      "content": "...",
      "elapsed_s": 2.14,
      "prompt_tokens": 523,
      "completion_tokens": 412,
      "cost_usd": 0.013
    }
  },
  "meta": {
    "models": ["...", "..."],
    "total_elapsed_s": 2.14,
    "total_prompt_tokens": 1046,
    "total_completion_tokens": 824,
    "total_cost_usd": 0.027
  }
}
```

Apply this protocol:

| Situation | Action |
|---|---|
| Both models agree | **High-confidence finding** — present as settled |
| One model unique | "Worth considering (flagged by [model] only)" |
| Models conflict | Surface both positions, explain tradeoff |
| Security finding from **any** model | Always escalate regardless of disagreement |
| Model returns `ERROR:...` | Note unavailable, weight remaining models accordingly |

> **Bias awareness:**
> - Longer response ≠ more reliable. Weight specificity and concrete examples over length.
> - Solo findings are unconfirmed, not dismissed.

#### Output format

```
## Multi-Model Review — [Task]
Models: [model-a] · [model-b]  |  Cost: $X.XX  |  Time: X.Xs

### Agreed findings  ✓ high confidence
- [finding]

### Solo findings  ? unconfirmed
- [model-a]: [finding]
- [model-b]: [finding]

### Conflicts  ↔
- **[topic]:** [model-a] says X / [model-b] says Y — [tradeoff note]

### Verdict
[1–2 sentence synthesis of the most actionable takeaways]
```

Omit any section with no entries. Omit cost if `total_cost_usd` is null.

---

### Standalone usage

```bash
# Two models, task-driven system prompt:
python scripts/or_review.py \
  --models "openai/gpt-5.5,anthropic/claude-opus-4.8" \
  --file myfile.py \
  --system "Check for race conditions and resource leaks."

# Piped input, no system prompt (general review):
cat myfile.py | python scripts/or_review.py \
  --models "deepseek/deepseek-v4-pro,moonshotai/kimi-k2.6"

# Free review:
python scripts/or_review.py \
  --models "deepseek/deepseek-v4-flash:free" \
  --file myfile.py

# Custom tokens cap:
python scripts/or_review.py \
  --models "openai/gpt-5.5,x-ai/grok-4.3" \
  --file myfile.py --max-tokens 1500
```
```

- [ ] **Step 2: Verify the file looks right**

```bash
cat "skills/multi-model-review/skills/multi-model-review/SKILL.md"
```

Check: frontmatter has `name`, `description`, `when_to_use`, `allowed-tools`. Model table has 9 rows. Three code blocks for script path, run command, and output format.

- [ ] **Step 3: Commit**

```bash
git add skills/multi-model-review/skills/multi-model-review/SKILL.md
git commit -m "feat(multi-model-review): rewrite SKILL.md — model-first natural language interface

Replace preset-picker with named model aliases + task extraction.
Add benchmark-backed model table (DeepSWE, GPQA, LMArena, May 2026).
Drop all preset references from skill instructions."
```

---

## Task 4: Smoke test end-to-end

Verify the full path works: SKILL parses → script runs → output is valid JSON.

**Files:**
- No new files

- [ ] **Step 1: Confirm script rejects old flags**

```bash
python "skills/multi-model-review/skills/multi-model-review/scripts/or_review.py" --list-presets
```

Expected:
```
error: unrecognized arguments: --list-presets
```

```bash
python "skills/multi-model-review/skills/multi-model-review/scripts/or_review.py" --preset code --prompt "hello"
```

Expected:
```
error: unrecognized arguments: --preset code
```

- [ ] **Step 2: Confirm script requires --models**

```bash
python "skills/multi-model-review/skills/multi-model-review/scripts/or_review.py" --prompt "hello"
```

Expected:
```
error: the following arguments are required: --models
```

- [ ] **Step 3: Confirm help text is clean (no preset mentions)**

```bash
python "skills/multi-model-review/skills/multi-model-review/scripts/or_review.py" --help
```

Expected: `--models` shown as required, no `--preset`, no `--list-presets`, no mention of "presets" in epilog.

- [ ] **Step 4: Live API test (requires OPENROUTER_API_KEY)**

```bash
echo "def add(a, b): return a - b  # bug here" | \
  python "skills/multi-model-review/skills/multi-model-review/scripts/or_review.py" \
  --models "deepseek/deepseek-v4-flash:free" \
  --system "Find the bug in this function."
```

Expected: JSON output with `results` containing one model's response, `meta.models` = `["deepseek/deepseek-v4-flash:free"]`, no `meta.preset` field.

If `OPENROUTER_API_KEY` is not set, expected error JSON:
```json
{"error": "OPENROUTER_API_KEY environment variable not set"}
```
That is also acceptable — it confirms arg parsing succeeded.

- [ ] **Step 5: Run all tests one final time**

```bash
cd "skills/multi-model-review/skills/multi-model-review/scripts"
python -m pytest test_or_review_args.py -v
```

Expected: `5 passed`.

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "chore(multi-model-review): smoke test verification complete"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| Remove PRESETS dict | Task 2 Step 2 |
| Remove --preset arg | Task 2 Step 3 |
| Remove --list-presets arg + handler | Task 2 Steps 4–5 |
| Make --models required | Task 2 Step 3 |
| Simplify model/system resolution | Task 2 Step 6 |
| Update label variable | Task 2 Step 7 |
| Remove preset from meta JSON | Task 2 Step 8 |
| Update docstring | Task 2 Step 1 |
| New SKILL.md trigger/description | Task 3 |
| Model alias table (9 models, benchmarks) | Task 3 |
| Parsing rules (model extraction, task extraction) | Task 3 |
| Execution instructions | Task 3 |
| Synthesis format (unchanged) | Task 3 — carried over verbatim |
| Standalone usage examples | Task 3 |

All spec requirements covered. No gaps found.

**Placeholder scan:** No TBD, TODO, or vague steps. All code blocks contain complete content.

**Type consistency:** `models` is always `list[str]`, `system` is always `str | None`. `label` is `str` in both old and new code. No naming inconsistencies across tasks.
