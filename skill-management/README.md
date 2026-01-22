# Skill Management

Tools for auditing, optimizing, discovering, and curating your Claude Code skills and plugins.

## Skills

### skill-curator

Audit and optimize your installed Claude Code skills/plugins. Helps you:

- **Find duplicates**: Identify identical agents across different plugins
- **Detect overlaps**: Spot skills with similar purposes
- **Calculate savings**: Estimate token reduction from cleanup
- **Recommend changes**: Get actionable keep/remove/add suggestions
- **Gap analysis**: Identify missing capabilities in your setup

### skill-finder

Discover new plugins, skills, and MCP servers via web search. Helps you:

- **Gap detection**: Recognizes when Claude is missing capabilities for a task
- **Web search**: Searches GitHub and marketplaces for solutions (99% on GitHub)
- **MCP discovery**: Finds MCP servers for service integrations
- **Install guidance**: Provides exact install commands for found plugins
- **Proactive suggestions**: Offers to search when it detects missing capabilities

## Usage

### Auditing (skill-curator)

Share your `/config` or `/skills` output and ask:

- "Audit my skills"
- "Find duplicate plugins"
- "Optimize my token usage"
- "What skills should I remove?"

### Discovery (skill-finder)

Ask Claude to find plugins or let it proactively detect gaps:

- "Find a plugin for browser automation"
- "Search for a PostgreSQL MCP server"
- "What skills exist for Kubernetes?"
- "I need an integration with Slack"
- (Or Claude offers: "I notice I don't have X capability. Want me to search for a plugin?")

## Examples

### Audit Example (skill-curator)

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

### Discovery Example (skill-finder)

```text
User: I need to automate browser testing

Claude: Let me search for browser automation plugins...

[Searches: "browser automation claude code plugin github"]

## 🔍 Discovery Results

### Found: playwright@claude-plugins-official ⭐ Recommended
- **Source:** Official Marketplace (Microsoft, Endorsed)
- **Capabilities:** Browser control, screenshots, PDF generation, form filling
- **Install:**
  ```bash
  claude mcp add playwright
  ```

Shall I help you install this?
```

### Proactive Gap Detection

```text
User: Query my PostgreSQL database for active users

Claude: I'd need database access for this query. I notice there's no
PostgreSQL MCP configured. Let me find one...

[Searches: "postgresql MCP server github"]

Found: mcp-server-postgres (Official Anthropic MCP)
- Direct SQL queries, schema inspection
- Install: Add to .mcp.json with connection string

Would you like the setup instructions?
```
