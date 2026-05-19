---
name: multi-model-review
description: Query 2–3 AI models in parallel via OpenRouter and synthesize their responses into a unified review. Use when the user says "get a second opinion", "ask GPT", "ask Gemini", "multi-model review", "council review", "validate this", "what does [model] think", or wants cross-model validation of code, architecture, security, writing, math, or documents. Requires OPENROUTER_API_KEY set in the environment.
when_to_use: Also invoke proactively for high-stakes work — security-sensitive code, architecture decisions before implementation, production-bound logic, or any case where a single model's blind spots could cause real harm.
allowed-tools: Bash Glob
---

# Multi-Model Review

Query multiple AI models in parallel via OpenRouter and synthesize their responses.
Uses the bundled `scripts/or_review.py` helper — requires `python` and `httpx` on PATH.

## Prerequisites

`OPENROUTER_API_KEY` must be set in Claude Code's environment. Add to user settings:

```json
{ "env": { "OPENROUTER_API_KEY": "sk-or-..." } }
```

Or export before launching: `export OPENROUTER_API_KEY=sk-or-...`

---

## Step 1 — Select a preset

Match the user's task to the best preset. The `--preset` flag selects the right models **and** system prompt automatically — no manual configuration needed.

| Task | `--preset` | Models | Benchmark backing |
|------|-----------|--------|-------------------|
| **Code review** | `code` | `anthropic/claude-opus-4.7` + `openai/gpt-5.5` | Both top-3 SWE-Bench Verified; different training lineages catch different bugs |
| **Security audit** | `security` | `google/gemini-3.1-pro-preview` + `anthropic/claude-opus-4.7` | Gemini 94.3% GPQA Diamond; Anthropic safety-trained #1 coder |
| **Architecture** | `arch` | `google/gemini-3.1-pro-preview` + `anthropic/claude-sonnet-4.6` | Both 1M+ context; structured reasoning at lower cost than Opus |
| **Writing critique** | `writing` | `anthropic/claude-sonnet-4.6` + `openai/gpt-5.5` | Claude #1 EQ-Bench Creative (1936 ELO); GPT-5.5 trained for reduced sycophancy |
| **Math / science** | `math` | `openai/o4-mini-high` + `google/gemini-3.1-pro-preview` | o4-mini 99.5% AIME 2025; Gemini 94.3% GPQA Diamond |
| **Long document** | `docs` | `google/gemini-3.1-pro-preview` + `openai/gpt-5.5` | Both 1M+ context; Gemini leads long-context recall |
| **Translation** | `translate` | `openai/gpt-5.5` + `google/gemini-3.1-pro-preview` | GPT-5.5 leads FLORES European; Gemini leads CJK + French |
| **Creative writing** | `creative` | `anthropic/claude-sonnet-4.6` + `google/gemini-3.1-pro-preview` | Claude #1 EQ-Bench narrative; Gemini #1 Chatbot Arena creative |
| **Quick check** | `quick` | `openai/gpt-4.1-mini` + `google/gemini-3.1-flash-lite` | Cheap, low latency — good for non-critical checks |
| **Free** | `free` | `openrouter/free` × 2 | Zero cost; each call independently routed to a random free model |

### Coding specialists — pick by benchmark

| Task | `--preset` | Models | Benchmark |
|------|-----------|--------|-----------|
| **UI / Web** | `code-web` | `anthropic/claude-opus-4.7` + `google/gemini-3.1-pro-preview` | Opus #1 WebDev Arena (1570 ELO); best for components, canvas, CSS |
| **SQL / data** | `code-sql` | `anthropic/claude-opus-4.7` + `google/gemini-3.1-pro-preview` | Opus #1 BIRD accuracy; Gemini leads BigQuery/Snowflake dialects |
| **CLI / systems** | `code-cli` | `openai/gpt-5.5` + `anthropic/claude-opus-4.7` | GPT-5.5 82.7% Terminal-Bench 2.0 (#1); Opus #2 — best agentic CLI pair |
| **Algorithms** | `code-live` | `openai/gpt-5.5` + `google/gemini-3.1-pro-preview` | LiveCodeBench (contamination-proof); different provider lineages |
| **Budget coding** | `budget` | `moonshotai/kimi-k2.6` + `deepseek/deepseek-v4-pro` | ~6× cheaper than code preset; comparable review quality |

Default when task is unclear: **`code`**.

> **Cost warning**: If the input exceeds ~5,000 tokens, warn the user before proceeding — costs multiply per model.
> - `claude-opus-4.7` ($5/M in · $25/M out) + `gpt-5.5` ($5/M in · $30/M out) — tier-1 pair; ~$0.20–$1.00/review on large files
> - `gemini-3.1-pro-preview` ($2/M in · $12/M out) — middle tier; appears in many presets as a cost-efficient partner
> - `budget` preset ($0.75/M + $0.44/M in): near-frontier code review at ~6× lower cost
> - `quick` and `free` presets: always safe to run without warning

---

## Step 2 — Run the script

### 2a. Find the script

```
Glob("**/multi-model-review/scripts/or_review.py")
```

If multiple paths are returned, prefer the one **not** containing `/cache/` in its path. Use the first result as `<script_path>`.

### 2b. Run with preset + content

**File input** (preferred — no escaping issues):
```bash
python "<script_path>" --preset code --file "<absolute_path_to_file>"
```

**Heredoc / inline content** (when the user pastes code directly):
```bash
python "<script_path>" --preset code << 'MMREVIEW'
<paste content here>
MMREVIEW
```

**Piped input**:
```bash
cat "<file_path>" | python "<script_path>" --preset security
```

**Short inline string** (only for simple content without special chars):
```bash
python "<script_path>" --preset quick --prompt "Review this function: ..."
```

### 2c. Overrides

Use `--models` to swap models while keeping the preset's system prompt:
```bash
python "<script_path>" --preset code --models "openai/gpt-5.5,google/gemini-3.1-pro-preview"
```

Use `--system` to replace the system prompt entirely:
```bash
python "<script_path>" --models "openai/gpt-5.5,anthropic/claude-opus-4.7" \
  --file myfile.py --system "You are a Python 2/3 compatibility expert..."
```

Use `--max-tokens N` to limit response length (default 2000). Use `--list-presets` to see all preset details.

The script prints progress to **stderr** as each model completes, and outputs JSON to **stdout**.

---

## Step 3 — Synthesize responses

The script prints JSON with this structure:
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
    "preset": "code",
    "models": ["...", "..."],
    "total_elapsed_s": 2.14,
    "total_prompt_tokens": 1046,
    "total_completion_tokens": 824,
    "total_cost_usd": 0.027
  }
}
```

Parse each model's response from `results[model-id].content`. Apply this protocol:

| Situation | Action |
|-----------|--------|
| Both models agree | **High-confidence finding** — present as settled |
| One model unique | "Worth considering (flagged by [model] only)" |
| Models conflict | Surface both positions, explain tradeoff, let user decide |
| Security finding from **any** model | Always escalate regardless of disagreement |

> **Bias awareness — apply to every synthesis:**
> - **Verbosity bias**: A longer response isn't more reliable. Weight specificity and concrete examples over length.
> - **Solo findings**: A finding from only one model is unconfirmed, not dismissed — flag it clearly.
> - If a model returns an `ERROR:...` string, note it was unavailable and weight findings from the remaining model(s) accordingly.

### Output format

```
## Multi-Model Review — [Task Type]
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

Omit any section that has no entries. If `meta.total_cost_usd` is null, omit the cost from the header.

---

## Standalone usage

```bash
# List all presets with their models:
python scripts/or_review.py --list-presets

# File review:
python scripts/or_review.py --preset code --file myfile.py

# Piped input:
cat myfile.py | python scripts/or_review.py --preset security

# Heredoc for inline content:
python scripts/or_review.py --preset arch << 'EOF'
paste architecture description here
EOF

# Custom models + system prompt:
python scripts/or_review.py \
  --models "openai/gpt-5.5,google/gemini-3.1-pro-preview" \
  --file myfile.py \
  --system "You are a Python 2/3 compatibility expert..."

# Budget review with max-tokens cap:
python scripts/or_review.py --preset budget --file myfile.py --max-tokens 1500
```
