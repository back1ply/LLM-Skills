# LLM Skills Marketplace

> Professional Claude Code skills for domain-specific code generation and best practices

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Plugin-blue.svg)](https://code.claude.com/)

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
```
User: "Create a Year-over-Year sales growth measure in DAX"
Claude: [Automatically uses writing-dax-measures skill]
```

You can also explicitly invoke:
```
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

## 🌟 Roadmap

### Coming Soon

- **SQL Query Optimization** - Generate performant SQL with index hints
- **React Component Patterns** - Type-safe components with best practices
- **Python Data Analysis** - Pandas/NumPy with performance patterns
- **Terraform Infrastructure** - AWS/Azure with security best practices

### Planned Domains

- TypeScript/JavaScript optimization
- Git workflow patterns
- API design patterns
- Database schema design
- CI/CD pipeline patterns

**Want to contribute?** Open an issue or PR!

## 📚 Documentation

### For Users

- [Installing from Marketplaces](https://code.claude.com/docs/en/discover-plugins)
- [Managing Plugins](https://code.claude.com/docs/en/plugins)
- [Plugin Reference](https://code.claude.com/docs/en/plugins-reference)

### For Plugin Developers

- [Creating Plugins](https://code.claude.com/docs/en/plugins)
- [Creating Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Marketplace Schema](https://anthropic.com/claude-code/marketplace.schema.json)

## 🤝 Contributing

We welcome contributions! Here's how:

### Suggest a New Skill

1. Open an issue with:
   - Domain/technology
   - Key anti-patterns to avoid
   - Performance best practices
   - Common calculation patterns
   - Link to authoritative sources

2. We'll research and create the skill

### Improve Existing Skills

1. Test skills with real-world scenarios
2. Report missing patterns or anti-patterns
3. Submit PRs with improvements
4. Share benchmarking results

### Quality Requirements

New skills must:
- ✅ Be based on authoritative sources
- ✅ Include pre-generation workflow
- ✅ List forbidden patterns with alternatives
- ✅ Provide performance optimization rules
- ✅ Include common calculation patterns
- ✅ Have quick reference tables
- ✅ Include pre-submission validation
- ✅ Be tested with real examples

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
