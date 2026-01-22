# Skill Management

Tools for auditing, optimizing, and curating your Claude Code skills and plugins.

## Skills

### skill-curator

Audit and optimize your installed Claude Code skills/plugins. Helps you:

- **Find duplicates**: Identify identical agents across different plugins
- **Detect overlaps**: Spot skills with similar purposes
- **Calculate savings**: Estimate token reduction from cleanup
- **Recommend changes**: Get actionable keep/remove/add suggestions
- **Gap analysis**: Identify missing capabilities in your setup

## Usage

Share your `/config` or `/skills` output and ask:

- "Audit my skills"
- "Find duplicate plugins"
- "Optimize my token usage"
- "What skills should I remove?"

## Example

```text
User: Here's my /skills output: [paste config]

Claude: ## 📊 Current State
- Total agents: 25 (1.4k tokens)
- Total skills: 50 (3.5k tokens)

## 🔴 Duplicates Found
| Item | Locations | Recommendation |
|------|-----------|----------------|
| code-reviewer | superpowers, comprehensive-review, git-pr-workflows | Keep superpowers, remove others |

## Estimated Savings: 400 tokens (8% reduction)
```
