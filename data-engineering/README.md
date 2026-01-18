# Data Engineering Plugin for Claude Code

> Build robust ETL/ELT pipelines with best practices for ingestion, transformation, orchestration, and troubleshooting.

## Overview

The Data Engineering plugin provides Claude Code with expertise in designing and implementing modern data pipelines. Based on industry best practices from O'Reilly's "Understanding ETL" guide.

## What This Plugin Provides

### ✅ Pipeline Design

- Source/destination evaluation checklists
- Batch vs. streaming decision framework
- Ingestion solution selection (declarative vs. imperative)

### ✅ Transformation Patterns

- 9 transformation patterns (enrichment, filtering, aggregation, etc.)
- 4 update patterns (overwrite, insert, upsert, delete)
- SQL examples for common operations

### ✅ Orchestration Patterns

- DAG design and decomposition
- Backfill, event-driven, and conditional logic
- Retry mechanisms and error handling

### ✅ Troubleshooting

- Observability metrics (freshness, volume, quality)
- Assertions and data validation
- Incident response and recovery

## Installation

### From LLM-Skills Marketplace

```bash
# Add the marketplace
/plugin marketplace add back1ply/LLM-Skills

# Install the Data Engineering plugin
/plugin install data-engineering@LLM-Skills
```

## Usage

Ask Claude to help with ETL/ELT tasks:

```text
User: "Design a pipeline to ingest data from Stripe API"
Claude: [Uses etl-pipeline-design skill to evaluate source, recommend approach]
```

```text
User: "How should I handle CDC in my warehouse?"
Claude: [Provides upsert patterns with MERGE examples]
```

## Skills Included

| Skill                  | Description                           |
|------------------------|---------------------------------------|
| `etl-pipeline-design`  | Comprehensive ETL/ELT pipeline design |

## Source

Based on *Understanding ETL (Updated Edition)* by Matt Palmer, O'Reilly Media, 2025.

## License

MIT License - See root LICENSE file

---

**Install now**: `/plugin install data-engineering@LLM-Skills`
