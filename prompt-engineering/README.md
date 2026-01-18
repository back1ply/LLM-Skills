# Prompt Engineering Plugin

> Expert prompt engineering assistance based on Forward Future's "Humanity's Last Prompt Engineering Guide"

![Status](https://img.shields.io/badge/Status-Available-green.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)

## Overview

This plugin helps users craft effective prompts for AI models (ChatGPT, Claude, Gemini) using proven techniques and best practices.

## Skills Included

### humanitys-last-prompt-engineer

Expert prompt engineering assistant that applies 11 foundational techniques to help users write, improve, and fix prompts.

**Activates when user**:

- Wants to write or improve prompts
- Has a prompt that's not working well
- Needs prompt templates for specific tasks
- Wants to learn prompting techniques

**What it provides**:

- Diagnostic workflow for analyzing prompts
- 11 prompting techniques with when-to-use guidance
- Common problems and fixes table
- Structured output format for improvements
- Role-based templates (Sales, Marketing, Ops, etc.)
- Quality scorecard for prompt evaluation

## Installation

```bash
/plugin install prompt-engineering@LLM-Skills
```

## Usage

Skills activate automatically. Examples:

```text
User: "Help me improve this prompt: Write a summary"
Claude: [Uses humanitys-last-prompt-engineer skill to diagnose and improve]

User: "Why isn't my prompt working well?"
Claude: [Applies diagnostic checklist and suggests fixes]

User: "What's the best technique for brainstorming?"
Claude: [Recommends Tree of Thoughts with examples]
```

## The 11 Techniques

| Technique | Best For |
| --------- | -------- |
| Zero-Shot | Simple, obvious tasks |
| Few-Shot | Specific structure/tone/format |
| System Prompt | Behavior/format rules |
| Role Prompt | Specific expertise/persona |
| Contextual | Tasks needing background/data |
| Step-Back | Complex reasoning |
| Chain-of-Thought | Math, logic, planning |
| Self-Consistency | High-stakes, ambiguous tasks |
| Tree of Thoughts | Brainstorming, multiple paths |
| ReAct | Tool use (search, code) |
| APE | Optimizing prompts at scale |

## Reference Materials

The skill includes detailed reference files:

- `role-templates.md` - 21 templates across 7 business roles
- `scorecard.md` - Quality checklist and refinement worksheet
- `techniques-detailed.md` - Deep-dive examples for each technique

## Attribution

Based on "Humanity's Last Prompt Engineering Guide" by Matthew Berman & Nick Wentz.

**Sources:**

- 📄 Article: [Humanity's Last Prompt Engineering Guide](https://www.forwardfuture.ai/p/humanity-s-last-prompt-engineering-guide)
- 🌐 Website: [Forward Future](https://forwardfuture.ai)
- 📺 YouTube: [@matthew_berman](https://youtube.com/@matthew_berman)
- 🐦 X/Twitter: [@forward_future_](https://x.com/forward_future_)

## License

MIT License - see [LICENSE](../LICENSE) for details.
