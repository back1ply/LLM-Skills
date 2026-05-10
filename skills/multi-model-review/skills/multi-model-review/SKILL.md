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

| Task | Models | Rationale |
|------|--------|-----------|
| **Code review** | `openai/gpt-4o` + `google/gemini-2.5-pro-preview` | Different training data, broad coverage |
| **Security audit** | `openai/o3` + `anthropic/claude-opus-4` | Deep reasoning + safety-trained |
| **Architecture** | `google/gemini-2.5-pro-preview` + `openai/o3` | Long context + structured reasoning |
| **Writing critique** | `google/gemini-2.5-flash` + `meta-llama/llama-4-maverick` | Fast + voice diversity |
| **Quick check** | `openai/gpt-4o-mini` + `google/gemini-2.5-flash` | Cheap, low latency |

Default when unsure: **Code review** preset.

**Cost warning**: If the input exceeds ~8,000 tokens, warn the user before proceeding —
costs multiply per model. `o3` + `claude-opus-4` can run $0.10–$0.50 per review.

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
  --models "openai/gpt-4o,google/gemini-2.5-pro-preview" \
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
  --models "openai/gpt-4o,google/gemini-2.5-pro-preview" \
  --prompt "Review this function: ..." \
  --system "You are an expert code reviewer..."
```
