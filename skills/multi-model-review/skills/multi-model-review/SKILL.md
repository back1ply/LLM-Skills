---
name: multi-model-review
description: Query 2–3 AI models in parallel via OpenRouter and synthesize their responses into a unified review. Use when the user says "get a second opinion", "ask GPT", "ask Gemini", "multi-model review", "council review", "what does [model] think", or wants cross-model validation of code, architecture, security, or writing. Requires OPENROUTER_API_KEY set in the environment.
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

## Step 1 — Detect task type, select preset

| Task | Models | Benchmark backing |
|------|--------|-------------------|
| **Code review** | `anthropic/claude-opus-4.7` + `openai/gpt-5.5` | Both top-3 SWE-Bench Verified; different training lineages catch different bugs |
| **Security audit** | `google/gemini-3.1-pro-preview` + `anthropic/claude-opus-4.7` | Gemini 94.3% GPQA Diamond (deep science/logic reasoning) + Anthropic safety-trained #1 coder |
| **Architecture** | `google/gemini-3.1-pro-preview` + `anthropic/claude-sonnet-4.6` | Both 1M+ context; strong structured reasoning at lower cost than Opus |
| **Writing critique** | `anthropic/claude-sonnet-4.6` + `openai/gpt-5.5` | Claude Sonnet #1 EQ-Bench Creative Writing (1936 ELO); GPT-5.5 leads LMArena writing category + trained for reduced sycophancy |
| **Math / science** | `openai/o4-mini-high` + `google/gemini-3.1-pro-preview` | o4-mini 99.5% AIME 2025 (best math reasoning); Gemini 94.3% GPQA Diamond (graduate science) |
| **Long document** | `google/gemini-3.1-pro-preview` + `openai/gpt-5.5` | Both 1M+ context windows; Gemini leads long-context recall; GPT-5.5 adds breadth and reasoning depth |
| **Translation** | `openai/gpt-5.5` + `google/gemini-3.1-pro-preview` | GPT-5.5 leads FLORES for most European language pairs; Gemini leads CJK, Portuguese, French, Ukrainian |
| **Creative writing** | `anthropic/claude-sonnet-4.6` + `google/gemini-3.1-pro-preview` | Claude Sonnet #1 EQ-Bench (1936 ELO, narrative quality); Gemini #1 Chatbot Arena creative writing category |
| **Quick check** | `openai/gpt-4.1-mini` + `google/gemini-3.1-flash-lite` | Cheap, low latency — flash-lite at $0.25/M input |

### Coding variants — pick by benchmark

| Task | Models | Benchmark |
|------|--------|-----------|
| **Code · WebDev Arena** | `anthropic/claude-opus-4.7` + `google/gemini-3.1-pro-preview` | Opus #1 WebDev Arena (1570 ELO); Gemini top-5 on UI/web tasks — different provider lineages catch different component/canvas bugs |
| **Code · BIRD (SQL)** | `anthropic/claude-opus-4.7` + `google/gemini-3.1-pro-preview` | Opus #1 BIRD execution accuracy May 2026; Gemini #1 BIRD single-model track + leads BigQuery/Snowflake dialects |
| **Code · Terminal-Bench** | `openai/gpt-5.5` + `anthropic/claude-opus-4.7` | GPT-5.5 82.7% Terminal-Bench 2.0 (CLI/server tasks, #1); Opus 4.7 69.4% (#2) — different training lineages, best agentic CLI pair |
| **Code · LiveCodeBench** | `openai/gpt-5.5` + `google/gemini-3.1-pro-preview` | Only contamination-proof coding benchmark (problems released after training cutoffs); both top-3 on coding leaderboards with different provider lineages |
| **Code · Budget** | `moonshotai/kimi-k2.6` + `deepseek/deepseek-v4-pro` | Kimi K2.6 ties GPT-5.5 on coding ($0.75/M in); DeepSeek V4 Pro 89/100 coding score ($0.44/M in) — combined ~6× cheaper than Opus+GPT-5.5 with comparable code-review quality |

Default when unsure: **Code review** preset.

> **Aggregator validation (May 2026)**: LMArena human-preference Elo, Artificial Analysis Intelligence Index, and OpenRouter usage all confirm the same three models at the statistical frontier — `openai/gpt-5.5` (LMArena 1506 Elo), `gemini-3.1-pro-preview` (1505), `claude-opus-4.7` (1503) — statistically tied within 95% CI. Use task-specific benchmarks above to break ties; aggregate rank alone is insufficient.

> **Always-latest aliases**: OpenRouter supports `~author/family-latest` slugs (e.g. `~anthropic/claude-opus-latest`, `~google/gemini-pro-latest`) that auto-resolve to the newest model in a family — useful if you want to stay current without editing prompts.

**Cost warning**: If the input exceeds ~8,000 tokens, warn the user before proceeding — costs multiply per model.
- `claude-opus-4.7` ($5/M in · $25/M out) + `openai/gpt-5.5` ($5/M in · $30/M out) — tier-1 pair; both appear in most high-quality presets
- `gemini-3.1-pro-preview` ($2/M in · $12/M out): middle tier; best context/value tradeoff; appears in many presets as a cost-efficient second model
- `moonshotai/kimi-k2.6` ($0.75/M in · $3.50/M out) + `deepseek/deepseek-v4-pro` ($0.44/M in · $0.87/M out): budget coding pair — use Code · Budget to get near-frontier code review at ~6× lower cost
- `openai/gpt-4.1-mini` + `google/gemini-3.1-flash-lite` ($0.25/M in): use Quick check for anything non-critical
- Presets with two Opus/GPT-5.5-class models can run $0.30–$2.00 per review on large files — warn the user if input > 5,000 tokens

---

## Step 2 — Locate and run the helper script

### 2a. Find the script

Use `Glob` to locate the installed helper regardless of where the skill was installed:

```
Glob("**/multi-model-review/scripts/or_review.py")
```

Take the first result as `<script_path>`.

### 2b. Run it via Bash

```bash
python "<script_path>" \
  --models "anthropic/claude-opus-4.7,openai/gpt-5" \
  --prompt "<the code or text to review>" \
  --system "<system prompt from below>"
```

The script queries all models in parallel and prints JSON to stdout:
`{ "model-id": "response text", ... }`

### System prompts — copy-paste per task

**Code review**
> You are an expert code reviewer. Analyze for: bugs, edge cases, security issues, performance problems, and maintainability. Reference specific constructs or line areas. Rate each finding: Critical / Warning / Suggestion.

**Security audit**
> You are a security engineer. Analyze for vulnerabilities: injection attacks, auth flaws, sensitive data exposure, cryptographic weaknesses, missing input validation, OWASP Top 10. Each finding: severity (Critical / High / Medium / Low) + remediation step.

**Architecture**
> You are a senior software architect. Review for: separation of concerns, scalability bottlenecks, tight coupling, missing abstractions, operational gaps (observability, failure modes). Call out tradeoffs explicitly.

**Writing critique**
> You are a professional editor. Review for: clarity, logical flow, tone consistency, unsupported claims, and structural weaknesses. Distinguish must-fix from polish.

**Math / science**
> You are an expert mathematician and scientist. Check every logical step, formula, proof, or derivation. Flag: incorrect reasoning chains, wrong assumptions, unit errors, missing edge cases, and claims that lack justification. Rate each finding: Error / Warning / Note.

**Long document**
> You are a meticulous analyst reviewing a long document. Identify: internal contradictions, unsupported claims, missing sections, logical gaps, and any conclusions that do not follow from the evidence. Cite the specific location of each finding.

**Translation**
> You are a professional translator and linguist. Review this translation for: accuracy of meaning, idiomatic naturalness in the target language, register consistency, cultural appropriateness, and any omissions or additions versus the source. Rate: Critical mistranslation / Awkward phrasing / Style suggestion.

**Creative writing**
> You are a literary editor with deep genre expertise. Evaluate this creative writing for: narrative momentum, character consistency, dialogue authenticity, show-vs-tell balance, sensory grounding, and tonal control. Distinguish structural issues from line-level suggestions.

**Code · WebDev Arena**
> You are an expert UI/web engineer. Review for: component correctness, state bugs, unnecessary re-renders, accessibility (WCAG 2.2), layout edge cases, and browser compatibility. Rate each finding: Critical / Warning / Suggestion.

**Code · BIRD (SQL)**
> You are a database engineer fluent in Postgres, BigQuery, Snowflake, and MySQL. Review for: query correctness, NULL semantics, cartesian join risk, implicit type coercions, missing indexes, and dialect-specific pitfalls. Flag any query that silently returns wrong results. Rate: Error / Warning / Note.

**Code · Terminal-Bench**
> You are a senior backend/systems engineer. Review for: API contract correctness, race conditions, improper error propagation, N+1 queries, missing idempotency, resource leaks, and scalability bottlenecks. Rate: Critical / Warning / Suggestion.

---

## Step 3 — Synthesize responses

Parse the JSON output from stdout. Apply this protocol:

| Situation | Action |
|-----------|--------|
| Both models agree | **High-confidence finding** — present as settled |
| One model unique | "Worth considering (flagged by [model] only)" |
| Models conflict | Surface both positions, explain tradeoff, let user decide |
| Security finding from **any** model | Always escalate regardless of disagreement |

### Output format

```
## Multi-Model Review — [Task Type]
Models: [model-a] · [model-b]

### Agreed findings (high confidence)
- [finding]

### Unique findings
- [model-a]: [finding]
- [model-b]: [finding]

### Conflicts
- **[topic]:** [model-a] says X / [model-b] says Y — [tradeoff note]

### Verdict
[1–2 sentence synthesis]
```

---

## Standalone usage

Run the script directly from any shell without Claude:

```bash
python scripts/or_review.py \
  --models "anthropic/claude-opus-4.7,openai/gpt-5" \
  --prompt "Review this function: ..." \
  --system "You are an expert code reviewer..."
```
