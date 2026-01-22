---
name: skill-curator
description: Audit and optimize Claude Code skills/plugins. Use when user wants to review installed skills, find duplicates, remove bloat, identify gaps, or optimize token usage. Analyzes skill configurations and recommends changes.
---

# Skill Curator

Help users audit, optimize, and curate their Claude Code skills and plugins for maximum efficiency.

## Quick Start

```text
1. User shares their current skill/plugin configuration (from /config or /skills output)
2. Analyze: Identify duplicates, overlaps, and bloat
3. Categorize: Group by purpose (code review, dev workflow, language-specific, etc.)
4. Recommend: Suggest removals, consolidations, and potential additions
5. Estimate: Calculate token savings
```

## Core Analysis Framework

### 1. Identify Duplicates (Exact Matches)

Look for:

- Same agent name across different plugins (e.g., `code-reviewer` in 3+ plugins)
- Plugins from same author with overlapping versions
- Skills with identical descriptions but different names

**Action:** Keep one, remove others. Prefer official > well-maintained community > generic.

### 2. Identify Overlaps (Similar Purpose)

| Category          | Common Overlaps                                                |
| ----------------- | -------------------------------------------------------------- |
| **Code Review**   | code-reviewer, architect-review, security-auditor, pr-reviewer |
| **Git Workflows** | commit-commands, git-workflows, pr-toolkit                     |
| **Planning**      | planning-with-files, write-plan, execute-plan                  |
| **Testing**       | test-driven-development, e2e-testing, python-testing           |

**Action:** Keep the most comprehensive one unless specialized versions serve distinct purposes.

### 3. Assess Relevance

For each installed skill, ask:

- Does the user's tech stack match? (Python skills for JS developer = bloat)
- When was it last used? (Never used = candidate for removal)
- Is it too generic? (Generic advice vs. actionable workflows)

### 4. Calculate Token Efficiency

```text
Token Efficiency Score = Usefulness × Frequency of Use / Token Cost

Priority removal: High tokens + Low usefulness + Never used
Priority keep: Any tokens + High usefulness + Frequently used
```

## Output Format

```markdown
## 📊 Current State

- Total agents: X (Y tokens)
- Total skills: X (Y tokens)
- Estimated overhead: X tokens

## 🔴 Duplicates Found

| Item | Locations        | Recommendation      |
| ---- | ---------------- | ------------------- |
| name | plugin1, plugin2 | Remove from plugin2 |

## 🟡 Overlaps Detected

| Category    | Items    | Tokens | Recommendation |
| ----------- | -------- | ------ | -------------- |
| Code Review | 4 agents | 500    | Keep 1-2       |

## 🟢 Unique & Useful

[Items that serve distinct purposes - no action needed]

## 💡 Recommendations

1. **Remove:** [specific items] → saves X tokens
2. **Consider Removing:** [items based on user's stack]
3. **Consider Adding:** [gaps identified]

## Estimated Savings: X tokens (Y% reduction)
```

## Decision Matrix

| Keep                          | Remove                  |
| ----------------------------- | ----------------------- |
| Official plugins              | Duplicate agents        |
| Actively used skills          | Never-used niche skills |
| Stack-specific (user's stack) | Wrong-stack skills      |
| Comprehensive tools           | Subsets of other tools  |
| Unique capabilities           | Redundant capabilities  |

## Plugin Quality Signals

**High Quality (Keep):**

- From official marketplace (anthropics/\*)
- Well-documented with examples
- Active maintenance (recent updates)
- Focused purpose, not bloated

**Low Quality (Remove Candidates):**

- Vague descriptions
- Duplicates functionality
- No clear use case
- Outdated (6+ months no updates)

## Gap Analysis

After cleanup, check for missing capabilities:

| Gap                 | Suggested Addition                                           |
| ------------------- | ------------------------------------------------------------ |
| No testing workflow | `test-driven-development`                                    |
| No planning system  | `planning-with-files` or `superpowers`                       |
| No code review      | `feature-dev` (lightweight) or `superpowers` (comprehensive) |
| No git workflow     | `commit-commands`                                            |

## Important Rules

- **ALWAYS** show token savings estimates
- **ALWAYS** explain why something is a duplicate vs. complementary
- **NEVER** recommend removing something without understanding user's workflow
- **ASK** about tech stack before recommending stack-specific removals
- **PRIORITIZE** removing high-token duplicates over low-token unique skills
- Consider that some overlap is intentional (tiered tools for different contexts)

## Example Diagnosis

**User has:**

- 5 different code-reviewer agents (500 tokens)
- Python skills but uses JavaScript
- 3 planning-related skills

**Recommendation:**

```text
1. Remove 4 code-reviewers, keep superpowers:code-reviewer → saves 300 tokens
2. Remove Python skills (wrong stack) → saves 200 tokens
3. Keep all 3 planning skills (different purposes: write/execute/file-based)
```
