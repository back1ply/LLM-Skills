# DAX Plugin for Claude Code

> Generate correct DAX measures for Power BI on the first attempt with comprehensive best practices, anti-pattern detection, and performance optimization.

## Overview

The DAX plugin provides Claude Code with deep expertise in writing DAX (Data Analysis Expressions) for Power BI. It ensures Claude generates syntactically correct, performant, and maintainable DAX code on the first try.

## What This Plugin Provides

### ✅ Pre-Generation Workflow
- Live schema extraction from Power BI
- Table/column validation before code generation
- Requirement analysis (aggregation, time intelligence, iterators)
- Filter context identification

### ✅ Anti-Pattern Detection
- **Deprecated functions**: EARLIER, IFERROR, ISERROR, FIRSTNONBLANK, LASTNONBLANK
- **Excel/SQL functions**: SUMIF, COUNTIF, VLOOKUP (don't exist in DAX)
- **Performance killers**: Table filtering, naked CALCULATE, measures that never return BLANK

### ✅ Performance Optimization
- Filter columns, not tables
- Variables for repeated calculations
- Iterator optimization patterns
- Context transition management

### ✅ Comprehensive Patterns
- **Time Intelligence**: YTD, MTD, QTD, PY, YoY growth
- **Common Calculations**: Running totals, rankings, moving averages
- **Filter Functions**: ALL, ALLSELECTED, ALLEXCEPT, REMOVEFILTERS
- **Relationships**: USERELATIONSHIP, CROSSFILTER

### ✅ Code Quality
- DAX naming conventions
- Documentation standards
- Debugging techniques
- Pre-submission validation checklist

## Installation

### From LLM-Skills Marketplace

```bash
# Add the marketplace
/plugin marketplace add back1ply/LLM-Skills

# Install the DAX plugin
/plugin install dax@LLM-Skills
```

### Verify Installation

The plugin adds the `writing-dax-measures` skill to your Claude Code instance. Claude will automatically use this skill when you request DAX code generation.

## Usage

Simply ask Claude to write DAX measures, and the skill will automatically activate:

```
User: "Create a YoY sales growth measure"
Claude: [Uses writing-dax-measures skill to generate correct DAX]
```

The skill ensures Claude:
1. ✅ Extracts live schema from Power BI MCP
2. ✅ Validates all tables/columns exist
3. ✅ Uses correct DAX functions (no Excel/SQL functions)
4. ✅ Applies performance best practices
5. ✅ Formats code properly with comments
6. ✅ Returns working code on first attempt

## Prerequisites

For full functionality, ensure you have:
- Power BI Desktop running
- Power BI MCP server configured and connected
- Target .pbix file open

The skill will work without MCP for general DAX knowledge, but schema extraction requires active MCP connection.

## What You Get

### Forbidden Functions Database
The skill knows all deprecated and non-existent functions:
- Deprecated (2026): EARLIER, IFERROR, ISERROR, FIRSTNONBLANK, LASTNONBLANK
- Excel functions that don't exist in DAX: SUMIF, COUNTIF, VLOOKUP
- Proper alternatives for each forbidden pattern

### Performance Rules
- Filter columns, not tables (critical for performance)
- Use variables to avoid repetitive calculations
- Minimize iterators and nested iterations
- Pre-aggregate when possible
- Cache measure values outside iterators

### Time Intelligence Patterns
Complete date table requirement checklist and proven patterns for:
- Year-to-Date (YTD), Month-to-Date (MTD), Quarter-to-Date (QTD)
- Previous Year (PY), Same Period Last Year
- Year-over-Year Growth (YoY%)
- Custom time calculations

### Quick Reference
Copy-paste ready patterns for:
- Safe division with DIVIDE()
- Filter removal (ALL, ALLSELECTED, ALLEXCEPT, REMOVEFILTERS)
- Running totals and cumulative calculations
- Rankings (RANKX)
- Moving averages
- Percentage of total
- Related values and lookups

## Research Foundation

This skill is based on extensive research from:
- **SQLBI** - Leading DAX experts (Marco Russo, Alberto Ferrari)
- **Microsoft Learn** - Official DAX documentation
- **DAX Patterns** - Proven calculation patterns
- **DAX Guide** - Comprehensive function reference
- **Real-world testing** - Lessons learned from DAX benchmark solver project

### Key Sources
- [SQLBI Articles](https://www.sqlbi.com/articles/)
- [DAX Patterns](https://www.daxpatterns.com/)
- [DAX Guide](https://dax.guide/)
- [Microsoft DAX Reference](https://learn.microsoft.com/en-us/dax/)

## Key Insight

> **"Prompt quality exceeds model size"**
>
> Accurate schema + avoiding anti-patterns + following best practices = first-try success

From benchmarking research: Both budget and premium models achieve first-attempt success when provided with correct schema and proper guidance on anti-patterns.

## Features

### 🚀 First-Try Success
Generate correct DAX code without iteration cycles.

### ⚡ Performance Optimized
Follow SQLBI and Microsoft best practices for fast query execution.

### 📚 Comprehensive Coverage
- Simple aggregations (SUM, COUNT, AVERAGE)
- Complex calculations (IF, SWITCH, COALESCE)
- Time intelligence (YTD, MTD, PY, YoY)
- Iterator patterns (SUMX, FILTER, RANKX)
- Many-to-many relationships
- Cross-filtering and USERELATIONSHIP

### 🛡️ Error Prevention
- Pre-validates schema references
- Checks function validity
- Avoids deprecated patterns
- Uses DIVIDE() for safe division
- Proper BLANK handling

### 📖 Maintainable Code
- Clear naming conventions
- Inline comments for complex logic
- Formatted for readability
- Self-documenting with variables

## Troubleshooting

### Skill Not Activating

If Claude doesn't use the skill automatically:
1. Explicitly mention "DAX" or "Power BI" in your request
2. Say "Use the DAX skill to help me write..."
3. Verify plugin installation: `/plugin list`

### Schema Extraction Issues

If Claude can't extract schema:
1. Verify Power BI Desktop is running
2. Check Power BI MCP server connection
3. Ensure .pbix file is open
4. Test MCP connection manually

### Function Not Found

If Claude uses a non-existent function:
1. Report the issue - the skill should prevent this
2. Check if it's an Excel function (SUMIF, VLOOKUP)
3. Verify against [DAX Guide](https://dax.guide/)

## Contributing

Found an issue or have a suggestion? Contributions welcome!

1. Test the skill with real DAX scenarios
2. Report any anti-patterns not caught
3. Suggest additional patterns to include
4. Share benchmarking results

## Version History

### v1.0.0 (2026-01-03)
- Initial release
- 14 comprehensive sections
- 50+ code examples
- Pre-generation workflow
- Forbidden functions database
- Performance optimization rules
- Time intelligence patterns
- Common calculation patterns
- Quick reference table
- Pre-submission validation checklist

## License

MIT License - See root LICENSE file

## Credits

Developed by **back1ply** based on:
- DAX Bench Solver repository research
- SQLBI best practices
- Microsoft Learn documentation
- DAX Patterns community knowledge
- Real-world Power BI development experience

---

**Install now**: `/plugin install dax@LLM-Skills`
