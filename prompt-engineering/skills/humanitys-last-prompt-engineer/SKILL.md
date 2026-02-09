---
name: humanitys-last-prompt-engineer
description: This skill should be used when the user asks to "write a prompt", "improve my prompt", "fix this prompt", "optimize a prompt", "learn prompting techniques", "get prompt templates", or mentions prompt engineering, prompt quality, or prompt rewriting. Applies 11 foundational techniques from Forward Future's guide.
---

# Humanity's Last Prompt Engineer

Craft effective prompts using proven techniques from Forward Future's prompt engineering guide. Diagnose weak prompts, apply the right technique, and deliver concrete rewrites.

> **Source**: Based on "Humanity's Last Prompt Engineering Guide" by Matthew Berman & Nick Wentz (Forward Future).
> <https://www.forwardfuture.ai/p/humanity-s-last-prompt-engineering-guide>

---

## Core Workflow

Follow these five steps for every prompt request:

```text
1. Receive the prompt (or a description of what the user needs)
2. Diagnose: Identify what's missing (role, context, format, task clarity)
3. Select technique(s): Determine which of the 11 techniques applies best
4. Rewrite: Produce an improved prompt
5. Explain: Briefly describe why the changes work
```

### Step 1: Diagnose the Prompt

Evaluate against these 6 diagnostic questions:

| # | Question | If Missing |
|---|----------|------------|
| 1 | Is the task clearly defined? | Add a specific action verb |
| 2 | Is there a role/persona? | Add "You are a [expert]..." |
| 3 | Is input/context complete? | Add background data or scenario |
| 4 | Is output format specified? | Add format constraint (bullets, JSON, table) |
| 5 | Is reasoning requested (if needed)? | Add "think step by step" or "explain logic" |
| 6 | Is it broken into steps (if complex)? | Decompose into subtasks |

### Step 2: Select the Right Technique

| Technique | When to Apply | Complexity |
|-----------|--------------|------------|
| **Zero-Shot** | Simple, obvious tasks requiring no examples | Low |
| **Few-Shot** | Need specific structure, tone, or output format | Low |
| **System Prompt** | Control persistent behavior or format rules | Low |
| **Role Prompt** | Need specific domain expertise or persona | Low |
| **Contextual** | Task requires background data or domain knowledge | Medium |
| **Step-Back** | Complex reasoning benefits from broader perspective first | Medium |
| **Chain-of-Thought** | Math, logic, planning, or multi-step reasoning | Medium |
| **Self-Consistency** | High-stakes or ambiguous tasks needing multiple reasoning paths | High |
| **Tree of Thoughts** | Brainstorming, exploration of multiple valid solution paths | High |
| **ReAct** | Tasks requiring tool use (search, code execution, APIs) | High |
| **APE** | Optimizing prompt performance at scale with automated testing | High |

For detailed examples, tips by experience level, and advanced usage of each technique, see **`references/techniques-detailed.md`**.

### Step 3: Apply the Prompt Formula

Every strong prompt contains four components:

- **Role**: Define expertise — "You are a [specific expert]..."
- **Task**: Use a clear action verb — Summarize, List, Write, Analyze, Compare, Generate
- **Input**: Provide what to work with — text, data, scenario, constraints
- **Format**: Specify response structure — bullets, JSON, table, word count, tone

**Example transformation:**

```text
Weak:  "Help me with marketing"
Strong: "You are a B2B SaaS copywriter. Write 3 LinkedIn post variations
         promoting our new analytics feature. Each post should be under
         150 words, use a professional but approachable tone, and end
         with a clear CTA."
```

### Step 4: Fix Common Problems

| Problem | Diagnosis | Fix |
|---------|-----------|-----|
| Too vague | No specifics or constraints | Add specifics: "3 bullet points focusing on X" |
| Wrong audience | No target reader defined | Add target: "for a busy executive" |
| Missing role | No expertise context | Add persona: "You are a brand copywriter" |
| Unstructured output | No format specified | Specify: "as a numbered list with explanations" |
| Shallow reasoning | No thinking requested | Add: "explain your logic" or "think step by step" |
| Inconsistent results | Single inference path | Apply Self-Consistency: generate 3 answers, pick majority |

### Step 5: Deliver the Output

Structure every response using this format:

```markdown
## Analysis
[What's working in the original prompt, what's missing or weak]

## Technique Applied
[Which technique(s) were selected and why they fit this case]

## Improved Prompt
[The complete rewritten prompt, ready to copy-paste]

## Why This Works
[1-2 sentences explaining the key improvements]
```

---

## Temperature Guide

Match temperature to the task type:

| Range | Best For | Examples |
|-------|----------|---------|
| **0-0.3** | Factual, precise, deterministic | Summaries, data analysis, extraction |
| **0.4-0.6** | Balanced (default) | General tasks, explanations |
| **0.7-1.0** | Creative, exploratory | Brainstorming, writing, ideation |

---

## Operational Rules

- Diagnose before rewriting — never skip the analysis step
- Explain which technique is being applied and why
- Provide a concrete, copy-pasteable improved prompt in every response
- Never just list tips without delivering a rewritten prompt
- Never over-complicate simple prompts — match complexity to the task
- Offer 2-3 variations when multiple techniques fit equally well
- Score the improved prompt against the diagnostic questions to verify quality

---

## Reference Files

For detailed guidance and tools, consult:

- **`references/techniques-detailed.md`** — Extended examples, tips by experience level, and advanced usage for all 11 techniques
- **`references/role-templates.md`** — Ready-to-use role-based prompt templates for common business scenarios (operations, marketing, sales, HR)
- **`references/scorecard.md`** — Prompt quality scorecard (1-35 rating) and refinement worksheet for systematic prompt evaluation
