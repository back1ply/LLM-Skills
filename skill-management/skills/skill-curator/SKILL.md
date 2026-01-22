---
name: skill-curator
description: Audit and optimize AI assistant skills across any platform. Use when user wants to review installed skills, find duplicates, detect overlaps, identify gaps, optimize for efficiency, or troubleshoot skill conflicts. Supports Gemini, Claude, Cursor, Copilot, Windsurf, and custom setups.
---

# Skill Curator

A comprehensive skill auditing system for AI coding assistants. Automatically discover, analyze, and optimize skills across any platform.

## Supported Platforms

| Platform | Skill Locations | Config Format |
| ---------- | ----------------- | --------------- |
| **Gemini/Antigravity** | `.agent/skills/`, MCP servers | `SKILL.md` + JSON |
| **Claude Code** | `.claude/`, plugins, `CLAUDE.md` | Markdown + JSON |
| **Cursor** | `.cursor/rules/`, `.cursorrules` | Markdown |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Markdown |
| **Windsurf** | `.windsurfrules`, `.codeium/` | Markdown |
| **Custom** | User-specified paths | Various |

---

## Phase 0: Quick Start Mode

Choose analysis depth:

```text
Quick or Full Analysis?

[Q] Quick: Auto-detect everything, use smart defaults (2 min)
[F] Full: Complete profile questionnaire + deep analysis (5 min)
```

### Quick Mode: Auto-Profile from Workspace

Instead of asking questions, detect automatically:

| Detection | Files to Check | Inference |
| ----------- | ---------------- | ----------- |
| **Tech Stack** | `package.json`, `requirements.txt`, `*.csproj`, `go.mod`, `Cargo.toml` | Primary language/framework |
| **Workflow** | `.github/`, `.gitlab-ci.yml`, `CODEOWNERS` | Solo vs team indicators |
| **Priority** | Existing skill categories | Security skills = security priority |
| **Platform** | `.agent/`, `.claude/`, `.cursor/` | AI assistant in use |

**Quick Mode Weights:**

- Relevance: 35% (based on detected stack match)
- Uniqueness: 25%
- Quality: 20%
- Efficiency: 15%
- Usage: 5% (estimated from activation triggers)

---

## Phase 1: User Profile Discovery

> Skip this in Quick mode

Ask these questions to personalize recommendations:

```markdown
## Quick Profile

1. **Tech Stack:** What languages/frameworks do you primarily use?
   - Examples: Python/FastAPI, TypeScript/React, Go, Rust, etc.

2. **Workflow Type:** How do you work?
   - [ ] Solo developer
   - [ ] Small team (2-5)
   - [ ] Large team / Enterprise

3. **AI Usage Priorities:** Rank 1-3 (1 = highest)
   - [ ] Speed (get things done fast)
   - [ ] Quality (thorough reviews, best practices)
   - [ ] Security (vulnerability detection, compliance)

4. **Primary Use Cases:** What do you use AI assistance for most?
   - [ ] Writing new code
   - [ ] Code review / refactoring
   - [ ] Debugging
   - [ ] Testing
   - [ ] Documentation
   - [ ] Planning / Architecture
```

Store this profile mentally to personalize all recommendations.

---

## Phase 2: Automated Discovery

### Step 1: Detect Platform

Check for platform indicators in this order:

```text
1. .agent/skills/     → Gemini/Antigravity
2. .claude/           → Claude Code
3. .cursor/           → Cursor
4. .github/copilot-*  → GitHub Copilot
5. .windsurfrules     → Windsurf
6. Ask user           → Custom/Unknown
```

### Step 2: Scan Skill Directories

Execute discovery based on detected platform:

**For Gemini/Antigravity:**

```text
- Scan: .agent/skills/**/SKILL.md
- Check: MCP server configurations
- Parse: Each SKILL.md frontmatter (name, description)
```

**For Claude Code:**

```text
- Scan: .claude/settings.json for plugins
- Check: CLAUDE.md files in project roots
- Parse: Plugin manifests and skill definitions
```

**For Cursor:**

```text
- Scan: .cursor/rules/*.md
- Check: .cursorrules in project root
- Parse: Rule definitions and contexts
```

**For Copilot/Windsurf:**

```text
- Scan: Instruction files in standard locations
- Parse: Markdown content for capability definitions
```

### Step 3: Build Skill Inventory

Create a structured inventory:

```markdown
| # | Skill Name | Source | Description | Est. Tokens |
| --- | ------------ | -------- | ------------- | ------------- |
| 1 | skill-name | path   | description | ~500        |
```

---

## Phase 2.5: Deep Skill Analysis

Go beyond frontmatter—read the full skill content:

### Extraction Targets

| Extraction | How to Find | Purpose |
| ------------ | ------------- | --------- |
| **Trigger Keywords** | "When to Use", "Use when", "Use this skill" sections | Better activation matching |
| **Anti-Patterns** | "Never", "Don't", "Avoid", "Forbidden" sections | Conflict detection |
| **Dependencies** | Tool references, MCP mentions, "Requires" statements | Dependency graph |
| **Token Estimate** | `character_count ÷ 4` | Accurate context sizing |
| **Complexity Score** | Count of phases, sections, rules, tables | Maintenance burden |
| **Examples Count** | Number of code blocks | Quality indicator |

### Complexity Scoring

| Metric | Low (1-3) | Medium (4-6) | High (7-10) |
| -------- | ----------- | -------------- | ------------- |
| **Phases/Sections** | 1-2 | 3-5 | 6+ |
| **Rules Count** | 1-3 | 4-8 | 9+ |
| **Code Examples** | 0-1 | 2-4 | 5+ |
| **Total Lines** | <100 | 100-300 | 300+ |

---

## Phase 3: Semantic Similarity Analysis

### Capability Extraction

For each skill, extract:

1. **Actions (Verbs):** What does it DO?
   - `review`, `generate`, `test`, `plan`, `debug`, `refactor`, `document`

2. **Domains (Nouns):** What does it OPERATE ON?
   - `code`, `tests`, `git`, `docs`, `architecture`, `security`, `performance`

3. **Capability Signature:** `[Actions] × [Domains]`
   - Example: `code-reviewer` → `[review] × [code]`
   - Example: `test-generator` → `[generate] × [tests]`

### Overlap Detection Matrix

Compare capability signatures:

| Overlap Type | Definition | Action |
| -------------- | ------------ | -------- |
| **Exact Duplicate** | Same actions AND same domains | Remove one |
| **Superset** | Skill A covers all of Skill B + more | Consider removing B |
| **Partial Overlap** | Some shared capabilities | Evaluate which is better |
| **Complementary** | Different actions OR different domains | Keep both |

### Semantic Grouping

Group skills by primary purpose:

| Category | Typical Actions | Typical Domains |
| ---------- | ----------------- | -------------------- |
| **Code Quality** | review, refactor, lint | code, style |
| **Testing** | generate, run, validate | tests, coverage |
| **Git/VCS** | commit, branch, merge | git, pr |
| **Planning** | plan, design, architect | architecture, tasks |
| **Documentation** | document, explain, summarize | docs, comments |
| **Security** | audit, scan, validate | security, auth |

---

## Phase 3.5: Conflict Detection

Beyond overlaps, detect **contradictions** between skills:

### Conflict Types

| Conflict Type | Example | Severity |
| --------------- | --------- | ---------- |
| **Opposing Rules** | Skill A: "Always use IFERROR" vs Skill B: "Never use IFERROR" | 🔴 High |
| **Style Clashes** | Skill A: "Use snake_case" vs Skill B: "Use camelCase" | 🟡 Medium |
| **Trigger Conflicts** | Both skills claim same activation phrase | 🟠 Medium |
| **Version Conflicts** | Skill A targets Node 18, Skill B requires Node 20 | 🟡 Medium |

### Detection Method

1. **Extract Rules:** Find all `ALWAYS`, `NEVER`, `MUST`, `DON'T`, `FORBIDDEN` statements
2. **Normalize Targets:** Extract the subject of each rule (function names, patterns, tools)
3. **Compare Polarity:** Match `ALWAYS X` against `NEVER X` patterns
4. **Score Confidence:** Higher confidence for explicit contradictions

### Conflict Report

```markdown
## ⚠️ Conflicts Detected

| Skills | Conflict | Severity | Resolution |
| -------- | ---------- | ---------- | ------------ |
| A ↔ B | A says "Always X", B says "Never X" | 🔴 High | Remove one or add scope limits |
```

---

## Phase 4: Weighted Scoring System

Calculate a composite score for each skill:

### Scoring Factors

| Factor | Weight | Score 0-10 | How to Assess |
| -------- | -------- | ------------ | --------------- |
| **Relevance** | 30% | 0-10 | Match to user's tech stack |
| **Uniqueness** | 25% | 0-10 | No other skill provides this |
| **Quality** | 20% | 0-10 | Docs, examples, maintenance |
| **Efficiency** | 15% | 0-10 | Value per token |
| **Usage** | 10% | 0-10 | How often it's activated |

### Score Calculation

```text
Final Score = (Relevance × 0.30) + (Uniqueness × 0.25) + 
              (Quality × 0.20) + (Efficiency × 0.15) + (Usage × 0.10)
```

### Health Indicators

Add health metrics beyond scoring:

| Metric | Score 0-10 | Assessment Method |
| -------- | ------------ | ------------------- |
| **Freshness** | 10 = <30 days old, 0 = >1 year | File modification date |
| **Completeness** | 10 = all sections, 0 = bare | Has examples, rules, anti-patterns |
| **Specificity** | 10 = focused, 0 = too broad | Single clear purpose vs kitchen sink |
| **Testability** | 10 = clear success criteria | Has verification/validation steps |

### Recommendation Tiers

| Score | Tier | Recommendation |
| ------- | ------ | ---------------- |
| 8-10 | 🟢 **Essential** | Keep - high value |
| 6-7.9 | 🟡 **Useful** | Keep unless cleanup needed |
| 4-5.9 | 🟠 **Marginal** | Consider removing |
| 0-3.9 | 🔴 **Remove** | Low value, remove |

---

## Phase 5: Analysis Output

Generate a comprehensive report:

```markdown
## 📊 Skill Inventory

- **Platform Detected:** [Platform Name]
- **Total Skills Found:** X
- **Estimated Token Overhead:** ~Y tokens

---

## 👤 User Profile Summary

- **Stack:** [Languages/Frameworks]
- **Workflow:** [Solo/Team/Enterprise]
- **Priority:** [Speed/Quality/Security]

---

## 🔴 Duplicates & Overlaps

| Skills | Overlap Type | Recommendation | Token Savings |
| -------- | -------------- | ---------------- | --------------- |
| A, B   | Exact        | Remove B       | ~300          |

---

## ⚠️ Conflicts

| Skills | Issue | Severity | Action |
| -------- | ------- | ---------- | -------- |
| A ↔ B  | Opposing rules on X | 🔴 High | Review |

---

## 🏥 Health Report

| Skill | Fresh | Complete | Specific | Testable | Health |
| ------- | ------- | ---------- | ---------- | ---------- | -------- |
| name  | 8     | 6        | 9        | 4        | 🟡 6.8 |

---

## 📈 Skill Scores

| Skill | Rel | Uniq | Qual | Eff | Use | **Score** | Tier |
| -------- | ----- | ------ | ------ | ----- | ----- | ----------- | ------ |
| name  | 8   | 9    | 7    | 6   | 8   | **7.6**   | 🟡   |

---

## 💡 Recommendations

### Remove (🔴 Low Value)
1. `skill-name` — Reason → saves ~X tokens

### Consider Removing (🟠 Marginal)
1. `skill-name` — Reason

### Keep (🟢🟡 Valuable)
1. `skill-name` — Why it's valuable

### Gaps Identified
1. Missing capability → Suggested skill to add

---

## 📉 Summary

- **Before:** X skills, ~Y tokens
- **After:** X skills, ~Y tokens
- **Savings:** Z tokens (N% reduction)
```

---

## Phase 5.5: Dependency Mapping

Map relationships between skills:

### Dependency Types

| Type | Indicator | Example |
| ------ | ----------- | --------- |
| **Requires** | Skill mentions another by name | "Use the X skill first" |
| **Enhances** | Skill extends another's capability | "After code review, use this for..." |
| **Conflicts** | Mutually exclusive usage | "Don't use with skill Y" |
| **MCP Dependency** | Requires specific MCP server | "Requires powerbi-desktop-mcp" |

### Visual Dependency Graph

```text
┌─────────────────┐
│ skill-curator   │
└────────┬────────┘
         │ enhances
         ▼
┌─────────────────┐     ┌─────────────────┐
│ writing-dax     │ ◄── │ no-calculate-dax│
└─────────────────┘     └─────────────────┘
         │ requires MCP
         ▼
┌─────────────────┐
│ powerbi-mcp     │
└─────────────────┘
```

### Dependency Insights

| Status | Meaning | Action |
| -------- | --------- | -------- |
| **Orphan** | No dependencies, not depended on | Safe to remove if low value |
| **Critical** | Many skills depend on this | Careful before removing |
| **Broken** | Depends on missing skill/MCP | Fix or remove |
| **Circular** | A → B → A | Refactor to break cycle |

---

## Phase 6: Actionable Outputs

### Backup Commands

Before making changes, backup current configuration:

**Gemini/Antigravity:**

```bash
cp -r .agent/skills .agent/skills.backup.$(date +%Y%m%d)
```

**Claude Code:**

```bash
cp -r .claude .claude.backup.$(date +%Y%m%d)
```

**Cursor:**

```bash
cp -r .cursor/rules .cursor/rules.backup.$(date +%Y%m%d)
```

### Auto-Consolidation Suggestions

When two skills have >70% capability overlap, offer a merge:

```markdown
🔀 **Merge Suggestion:** skill-a + skill-b → skill-combined

**Shared Capabilities:**
- [capability 1]
- [capability 2]

**Unique to A:**
- [capability 3]

**Unique to B:**
- [capability 4]

**Proposed Action:** Generate merged SKILL.md draft
**Token Savings:** ~500 (30% reduction)
```

### Removal Commands

Provide exact commands for each removal:

```bash
# Remove skill: [skill-name]
rm -rf .agent/skills/[skill-name]

# Or for single-file skills:
rm .cursor/rules/[rule-name].md
```

### Installation Commands

For recommended additions:

**Gemini (via MCP skill-loader):**

```text
Use mcp_agent-skill-loader_install_skill with skill_name: "[skill-name]"
```

**Claude Code:**

```bash
claude plugins add [plugin-name]
```

**Manual:**

```bash
# Create skill directory
mkdir -p .agent/skills/[skill-name]
# Then create SKILL.md with appropriate content
```

### Verification Steps

After changes:

```text
1. List skills to confirm changes took effect
2. Test a sample prompt that would trigger the skill
3. Verify no errors in AI assistant startup
4. Confirm token reduction in context usage (if measurable)
```

---

## Important Rules

1. **ALWAYS** offer Quick vs Full mode at start
2. **ALWAYS** use automated discovery — don't ask users to paste config
3. **ALWAYS** calculate semantic overlap, not just name matching
4. **ALWAYS** check for conflicts between skill rules
5. **ALWAYS** provide weighted scores with justification
6. **ALWAYS** give exact commands, not vague instructions
7. **ALWAYS** show dependency relationships for critical skills
8. **NEVER** recommend removing a skill without understanding user's workflow
9. **NEVER** assume platform — detect or ask
10. **ASK** about tech stack before stack-specific recommendations
11. **PRIORITIZE** removing high-token duplicates over low-token unique skills
12. **CONSIDER** that some overlap is intentional (tiered tools for contexts)

---

## Example Workflow

**Scenario:** User on Gemini with Python/FastAPI stack, solo developer, quality-focused

**Discovery finds:**

- 3 code review skills (similar capabilities)
- 2 Python skills (both relevant)
- 1 JavaScript testing skill (wrong stack)
- 1 planning skill (unique)

**Analysis:**

| Skill | Rel | Uniq | Qual | Eff | Use | Score | Health | Action |
| ------- | ----- | ------ | ------ | ----- | ----- | ------- | -------- | -------- |
| code-review-pro | 9 | 3 | 8 | 7 | 9 | **7.0** | 🟢 8.5 | 🟡 Keep (best of 3) |
| code-review-lite | 9 | 2 | 5 | 8 | 3 | **5.3** | 🟡 6.0 | 🟠 Remove (subset) |
| code-review-basic | 9 | 2 | 4 | 9 | 2 | **4.9** | 🔴 4.0 | 🔴 Remove (subset) |
| python-expert | 10 | 8 | 9 | 7 | 8 | **8.6** | 🟢 9.0 | 🟢 Keep |
| python-tips | 10 | 4 | 6 | 8 | 5 | **6.7** | 🟡 7.0 | 🟡 Keep (complementary) |
| js-testing | 2 | 7 | 7 | 6 | 1 | **4.3** | 🟡 6.5 | 🔴 Remove (wrong stack) |
| planning-system | 9 | 10 | 8 | 6 | 7 | **8.3** | 🟢 8.0 | 🟢 Keep |

**Conflicts Found:**

- None detected ✅

**Result:** Remove 3 skills, save ~800 tokens, 43% reduction

---

## Appendix: Skill Portfolio Templates

Recommend skill sets based on user profile:

### Python Data Scientist

| Category | Recommended Skills |
| ---------- | ------------------- |
| Core | python-expert, jupyter-notebooks |
| Quality | code-review, testing-patterns |
| Data | etl-pipeline-design, data-validation |
| ML | experiment-tracking, model-deployment |
| **Estimated Token Budget** | ~3000 tokens |

### TypeScript Full-Stack

| Category | Recommended Skills |
| ---------- | ------------------- |
| Core | typescript-expert, react-patterns |
| Quality | code-review, testing-patterns |
| API | rest-api-design, graphql-patterns |
| Infra | docker-compose, kubernetes-basics |
| **Estimated Token Budget** | ~3500 tokens |

### Power BI / DAX Developer

| Category | Recommended Skills |
| ---------- | ------------------- |
| Core | writing-dax-measures, no-calculate-dax |
| Data | etl-pipeline-design |
| Quality | code-review |
| Prompting | humanitys-last-prompt-engineer |
| **Estimated Token Budget** | ~2500 tokens |

### DevOps / Platform Engineer

| Category | Recommended Skills |
| ---------- | ------------------- |
| Core | infrastructure-as-code, kubernetes-patterns |
| Quality | code-review, security-scanning |
| CI/CD | pipeline-design, deployment-strategies |
| Monitoring | observability-patterns, incident-response |
| **Estimated Token Budget** | ~3000 tokens |

### Solo Generalist

| Category | Recommended Skills |
| ---------- | ------------------- |
| Core | code-review, testing-patterns |
| Planning | planning-system, architecture-design |
| Docs | documentation-generator |
| Prompting | humanitys-last-prompt-engineer |
| Meta | skill-curator |
| **Estimated Token Budget** | ~2000 tokens |
