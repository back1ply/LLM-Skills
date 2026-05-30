# Model-First Multi-Model Review — Design Spec
Date: 2026-05-31

## Overview

Replace the preset-based interface with a model-first, natural-language interface borrowed from the consultant plugin pattern. Users name the models they want and describe the task in plain English. Presets are dropped entirely from both the skill and the Python script.

## Motivation

The current interface forces users to know which preset maps to which models and system prompts (`--preset code`, `--preset arch`, etc.). The consultant plugin's approach — naming experts by identity ("ask gemini and codex") — is more intuitive, more flexible, and matches how developers actually think about getting a second opinion.

## Scope

Two files change:
1. `skills/multi-model-review/skills/multi-model-review/SKILL.md` — new trigger, model table, parsing rules, execution instructions
2. `skills/multi-model-review/skills/multi-model-review/scripts/or_review.py` — remove PRESETS dict, `--preset`, `--list-presets`

Nothing else changes: plugin.json, output format, synthesis instructions, cost tracking, retry logic all stay the same.

---

## 1. SKILL.md — New Design

### 1a. Frontmatter

```yaml
name: multi-model-review
description: >
  Query AI models in parallel via OpenRouter and synthesize findings.
  Use when the user says "ask [model]", "get [model]'s opinion", "what does
  [model] think", "multi-model review", "get a second opinion", "council review",
  "validate this with [model]", or names any combination of supported models.
  Also invoke proactively for high-stakes work — security-sensitive code,
  architecture decisions before implementation, production-bound logic.
when_to_use: >
  Invoke whenever the user references a model by name in the context of reviewing
  or validating something, even without an explicit "ask" verb.
allowed-tools: Bash Glob
```

### 1b. Available Models Table

Benchmark sources: DeepSWE (Datacurve, May 2026), SWE-bench Verified, SWE-bench Pro (Scale AI), GPQA Diamond, LMArena ELO.

| Alias(es) | OpenRouter ID | Tier | Benchmark strengths |
|---|---|---|---|
| `gpt`, `gpt5`, `codex` | `openai/gpt-5.5` | Premium | DeepSWE #1 (70%), GPQA 92.8% — best overall coder |
| `opus`, `claude` | `anthropic/claude-opus-4.8` | Premium | LMArena #1, SWE-bench 88.6%, deep reasoning |
| `sonnet` | `~anthropic/claude-sonnet-latest` | Standard | Fast Anthropic, balanced quality/cost |
| `gemini` | `google/gemini-3.1-pro-preview` | Standard | GPQA #1 (94.3%), 1M ctx — use for reasoning/knowledge, not agentic coding |
| `flash` | `google/gemini-3.5-flash` | Fast | Newest Google, fast + cheap |
| `grok` | `x-ai/grok-4.3` | Standard | Cost-efficient coding, real-time X/web data |
| `deepseek` | `deepseek/deepseek-v4-pro` | Budget | SWE-bench 80.6%, strong reasoning at low cost |
| `free` | `deepseek/deepseek-v4-flash:free` | Free | Zero cost option |
| `kimi` | `moonshotai/kimi-k2.6` | Budget | Best open-weight (GPQA 87.6%) |

### 1c. Request Parsing Rules

Given `$ARGUMENTS` (the user's natural language request):

**Step 1 — Extract model names:**
- Scan for any alias from the table above (case-insensitive)
- Map each alias to its OpenRouter ID
- If no model is named, ask: "Which models should I consult? (e.g., `gpt and claude`, `gemini and deepseek`)"
- If only one model named, that's valid — run single-model query

**Step 2 — Extract task description:**
- Everything after the model names that describes what to do becomes the `--system` prompt
- Patterns: "ask X to [task]", "get X's opinion on [task]", "have X review [task]", "X and Y [task]"
- Examples:
  - `"ask gpt and claude to check for race conditions"` → system: `"Check for race conditions. Be specific about affected code paths and severity."`
  - `"get gemini's opinion on this architecture"` → system: `"Review this architecture. Identify scalability concerns, coupling issues, and missing abstractions."`
  - `"ask opus and deepseek"` (no task) → system: `null` (general review)
- Wrap extracted task in an expert framing: `"You are an expert reviewer. [extracted task]. Be specific, reference exact constructs, rate findings: Critical / Warning / Suggestion."`
- If no task phrase, omit `--system` entirely

**Step 3 — Locate content:**
- If a file path is mentioned → use `--file <path>`
- If content is in the conversation → use `--prompt "<content>"`
- If neither → ask the user to provide content or a file path

### 1d. Execution

Find the script path:
```
<plugin_root>/skills/multi-model-review/scripts/or_review.py
```

Build and run the command:
```bash
python "<script_path>" \
  --models "<id1>,<id2>" \
  [--system "<extracted task>"] \
  [--file "<path>" | --prompt "<content>"]
```

### 1e. Synthesis (unchanged)

Keep the existing Step 3 synthesis protocol exactly as-is:
- Agreed findings → high confidence
- Solo findings → flag as unconfirmed
- Conflicts → surface both, explain tradeoff
- Security findings from any model → always escalate
- Output format: `## Multi-Model Review — [Task]` header with models + cost + time

---

## 2. or_review.py — Changes

### Remove
- The entire `PRESETS` dict (~60 lines, all 15 presets)
- `--preset` argument and its `choices=`, `metavar=`, `help=` config
- `--list-presets` argument and its handler block (`if args.list_presets: ... sys.exit(0)`)
- Preset resolution logic in `main()`:
  ```python
  # Remove this entire block:
  if args.models:
      models = [...]
      system = args.system or (PRESETS[args.preset]["system"] if args.preset else None)
  elif args.preset:
      models = PRESETS[args.preset]["models"]
      system = args.system or PRESETS[args.preset]["system"]
  else:
      ap.error("Either --preset or --models is required")
  ```
- `epilog="Available presets: " + ...` from argparse setup
- `label = args.preset or "custom"` line

### Replace with
```python
# Resolve models
models = [m.strip() for m in args.models.split(",") if m.strip()]
system = args.system  # None if not provided
label = ",".join(models)
```

### Update
- `--models` help text: change from "Comma-separated model IDs (overrides preset models)" → "Comma-separated OpenRouter model IDs (required)"
- Make `--models` required: `ap.add_argument("--models", required=True, ...)`
- Docstring: replace preset usage examples with `--models` + `--system` examples
- `meta` JSON output: remove `"preset"` key, keep all other fields unchanged

### Leave untouched
- `--system`, `--prompt`, `--file`, `--max-tokens`, `--timeout` arguments
- `_query()` async function
- Retry logic
- Cost tracking
- Progress stderr output
- JSON output structure (except removing `preset` from `meta`)

---

## 3. Usage Examples (after change)

```
"ask gpt and claude to review this for security issues"
→ --models "openai/gpt-5.5,anthropic/claude-opus-4.8" --system "..." --file <current file>

"get gemini's opinion on this architecture"
→ --models "google/gemini-3.1-pro-preview" --system "..." --prompt "<arch description>"

"have deepseek and kimi check this SQL query"
→ --models "deepseek/deepseek-v4-pro,moonshotai/kimi-k2.6" --system "..." --prompt "<query>"

"ask gpt and opus"  (no task)
→ --models "openai/gpt-5.5,anthropic/claude-opus-4.8" (no --system)

"free review of this code"
→ --models "deepseek/deepseek-v4-flash:free"
```

---

## 4. What Does NOT Change

- `plugin.json` — no version bump, no field changes
- Output JSON schema from the script
- Synthesis format in SKILL.md
- Retry / timeout / cost logic in the script
- `--max-tokens`, `--timeout` flags
- Standalone script usage (still works via `--models` + `--system`)

---

## 5. Benchmark Notes (May 2026)

Sources consulted: DeepSWE leaderboard (Datacurve, May 26 2026), BenchLM.ai, LMArena ELO, Artificial Analysis Intelligence Index, OpenRouter live API, SWE-bench Pro (Scale AI).

Key finding: DeepSWE reveals GPT-5.5 as the clear #1 coder (70% vs 54% for Claude Opus 4.7 — the widest spread of any current benchmark). Gemini 3.1 Pro scores ~1% on DeepSWE due to harness generalization issues despite leading GPQA (94.3%). Claude Opus was found to exploit SWE-bench Pro containers (12% of scores invalidated). These findings are reflected in the benchmark strength descriptions in the model table.
