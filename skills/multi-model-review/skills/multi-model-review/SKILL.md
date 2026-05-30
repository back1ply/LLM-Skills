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
- If no task phrase, omit `--system` entirely

**Locate content:**
- File path mentioned → `--file <path>`
- Content in conversation → `--prompt "<content>"`
- Neither → ask: *"Please provide the content to review, or a file path."*

---

### Step 2 — Find the script

Locate via glob: `**/multi-model-review/scripts/or_review.py`

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
