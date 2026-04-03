# LLM Skills Marketplace

> Professional Claude Code skills for domain-specific code generation and best practices

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Plugin-blue.svg)](https://code.claude.com/)
[![SkillCheck](https://img.shields.io/badge/SkillCheck-PASS-brightgreen)](https://getskillcheck.com)

A curated marketplace of high-quality skills for Claude Code, focused on enabling first-attempt success in domain-specific code generation.

## 🚀 Quick Start

### Add This Marketplace

```bash
/plugin marketplace add back1ply/LLM-Skills
```

### Browse Available Plugins

```bash
/plugin
# Navigate to "Discover" tab to see all available plugins
```

### Install a Plugin

```bash
/plugin install dax@LLM-Skills
```

## 📦 Available Plugins

### DAX for Power BI

**Status**: ✅ Available
**Version**: 1.0.0
**Category**: Productivity

Generate correct DAX measures for Power BI on the first attempt with comprehensive best practices, anti-pattern detection, and performance optimization.

**Installation**:

```bash
/plugin install dax@LLM-Skills
```

**What it provides**:

- ✅ Pre-generation workflow with live schema extraction
- ✅ Anti-pattern detection (deprecated functions, Excel/SQL functions)
- ✅ Performance optimization (filter columns not tables, use variables)
- ✅ Time intelligence patterns (YTD, MTD, QTD, PY, YoY)
- ✅ Common calculation patterns (running totals, rankings)
- ✅ Quick reference table with copy-paste patterns
- ✅ Pre-submission validation checklist

**Read more**: [DAX Plugin Documentation](./dax/README.md)

---

### Prompt Engineering

**Status**: ✅ Available
**Version**: 1.0.0
**Category**: Productivity

Expert prompt engineering assistance using 11 foundational techniques from Forward Future's guide. Write, improve, and fix prompts for ChatGPT, Claude, Gemini.

**Installation**:

```bash
/plugin install prompt-engineering@LLM-Skills
```

**What it provides**:

- ✅ Diagnostic workflow for analyzing prompts
- ✅ 11 prompting techniques with when-to-use guidance
- ✅ Common problems and fixes table
- ✅ Role-based templates (Sales, Marketing, Ops, Management, Content, Data, L&D)
- ✅ Quality scorecard for prompt evaluation
- ✅ Detailed technique examples with beginner/intermediate/advanced tips

**Read more**: [Prompt Engineering Plugin Documentation](./prompt-engineering/README.md)

---

### Data Engineering (ETL/ELT)

**Status**: ✅ Available  
**Version**: 1.0.0  
**Category**: Data Engineering

Build robust ETL/ELT pipelines with best practices for ingestion, transformation, orchestration, and troubleshooting.

**Installation**:

```bash
/plugin install data-engineering@LLM-Skills
```

**What it provides**:

- ✅ Source/destination evaluation checklists
- ✅ Batch vs. streaming decision framework
- ✅ 9 transformation patterns with SQL examples
- ✅ 4 update patterns (overwrite, insert, upsert, delete)
- ✅ 8 orchestration design patterns
- ✅ Observability metrics and alerting best practices
- ✅ Incident response and recovery procedures

**Read more**: [Data Engineering Plugin Documentation](./data-engineering/README.md)

---

### Skill Management

**Status**: ✅ Available
**Version**: 1.0.0
**Category**: Productivity

Audit, optimize, and discover Claude Code skills/plugins. Find duplicates, detect overlaps, search for new plugins via GitHub, and get actionable recommendations.

**Installation**:

```bash
/plugin install skill-management@LLM-Skills
```

**What it provides**:

**skill-curator** - Audit & Optimize:
- ✅ Duplicate skill detection across plugins
- ✅ Overlap analysis for similar capabilities
- ✅ Token usage calculation and savings estimation
- ✅ Keep/remove/add recommendations
- ✅ Gap analysis for missing capabilities

**skill-finder** - Discover & Install:
- ✅ Proactive gap detection (Claude offers to search when it lacks capabilities)
- ✅ Web search for plugins/skills on GitHub (99% of results)
- ✅ MCP server discovery for service integrations
- ✅ Exact install commands with marketplace priority
- ✅ Quality signals (stars, activity, documentation)

**Read more**: [Skill Management Plugin Documentation](./skill-management/README.md)

---

### KPI Checklists

**Status**: ✅ Available
**Version**: 1.0.0
**Category**: Business Performance

Develop meaningful, trusted KPIs and reports using the structured ROKS (Results Orientated KPI System) methodology — from strategy alignment through to sustained production.

**Installation**:

```bash
/plugin install kpi@LLM-Skills
```

**What it provides**:

- ✅ 7-step ROKS framework for KPI development
- ✅ Strategy fitness and stakeholder engagement checklists
- ✅ KPI Tree workshop facilitation guides
- ✅ Importance/Availability shortlisting matrix
- ✅ KPI Definition Canvas and templates
- ✅ 53-point Brilliant Dashboards design checklist
- ✅ Go-live checklists: buy-in, data problems, SMED, FMEA
- ✅ PDCA improvement cycle and meeting effectiveness guides

**Read more**: [KPI Plugin Documentation](./kpi/README.md)

---

## 🎯 Marketplace Philosophy

### First-Try Success

Our skills are designed to enable Claude to generate correct code on the first attempt by:

1. **Pre-generation validation** - Extract schema, verify references
2. **Anti-pattern prevention** - Forbidden functions database
3. **Best practice enforcement** - Industry standards from domain experts
4. **Comprehensive patterns** - Common use cases with copy-paste examples

### Research-Driven

Every skill is backed by:

- 📚 Official documentation (Microsoft, SQLBI, etc.)
- 🔬 Real-world benchmarking and testing
- 👥 Community best practices
- ⚡ Performance optimization research

### Quality Standards

Skills must include:

- Clear pre-generation workflow
- Forbidden patterns with alternatives
- Performance optimization rules
- Common calculation patterns
- Quick reference tables
- Pre-submission validation checklists

## 📖 How to Use

### 1. Add the Marketplace

```bash
/plugin marketplace add back1ply/LLM-Skills
```

This makes all plugins in this marketplace discoverable.

### 2. Install Plugins

**Interactive (Recommended)**:

```bash
/plugin
# Navigate to Discover tab
# Select plugin and press Enter
# Choose installation scope (user/project/local)
```

**Command Line**:

```bash
/plugin install <plugin-name>@LLM-Skills

# Examples:
/plugin install dax@LLM-Skills
```

### 3. Use the Skills

Skills activate automatically when relevant. For example:

```text
User: "Create a Year-over-Year sales growth measure in DAX"
Claude: [Automatically uses writing-dax-measures skill]
```

You can also explicitly invoke:

```text
User: "Use the DAX skill to help me write a measure for..."
```

## 🔧 Installation Scopes

Choose where to install plugins:

- **User scope**: Available across all your projects
- **Project scope**: Shared with all collaborators (committed to `.claude/settings.json`)
- **Local scope**: Only for you in this repository (`.claude/settings.local.json`)

## 🛠️ Managing Plugins

### List Installed Plugins

```bash
/plugin list
```

### Disable/Enable Plugins

```bash
/plugin disable dax@LLM-Skills
/plugin enable dax@LLM-Skills
```

### Uninstall Plugins

```bash
/plugin uninstall dax@LLM-Skills
```

### Update Marketplace Listings

```bash
/plugin marketplace update LLM-Skills
```

## 📚 Documentation

### For Users

- [Installing from Marketplaces](https://code.claude.com/docs/en/discover-plugins)
- [Managing Plugins](https://code.claude.com/docs/en/plugins)
- [Plugin Reference](https://code.claude.com/docs/en/plugins-reference)

### For Plugin Developers

- [Creating Plugins](https://code.claude.com/docs/en/plugins)
- [Creating Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Marketplace Schema](https://anthropic.com/claude-code/marketplace.schema.json)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Credits

### Research Sources

Skills in this marketplace are built on research from:

- **SQLBI** - DAX expertise
- **Microsoft Learn** - Official documentation
- **DAX Patterns** - Community patterns
- **Real-world benchmarking** - Tested approaches

### Contributors

- **back1ply** - Marketplace creator and maintainer

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/back1ply/LLM-Skills/issues)
- **Discussions**: [GitHub Discussions](https://github.com/back1ply/LLM-Skills/discussions)

## 🔗 Links

- [Claude Code Documentation](https://code.claude.com/docs)
- [Official Claude Code Marketplace](https://github.com/anthropics/claude-code)
- [Claude Code Plugins](https://claude.com/blog/claude-code-plugins)

---

**Get started now**: `/plugin marketplace add back1ply/LLM-Skills`
