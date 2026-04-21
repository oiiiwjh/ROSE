# ROSE — Research Operating System for Erudition

[中文文档](./README-zh.md)

A personal research exploration system built on [Claude Code](https://claude.ai/claude-code) Skills. Use slash commands in the terminal to read papers, get daily recommendations, survey research topics, manage your paper library, and more — all outputs are structured and stored locally.

## Prerequisites

- [Claude Code](https://claude.ai/claude-code) CLI installed
- Python 3.10+ (stdlib only, no external dependencies)
- Network access to arxiv.org and alphaxiv.org

## Quick Start

```bash
# 1. Enter the project directory
cd rose

# 2. First-time setup wizard (interactive research interest configuration)
/setup

# 3. Start using
/daily-papers              # Get today's paper recommendations
/read-paper 2401.12345     # Deep analysis of a paper
/survey-topic 3D Gaussian Splatting   # Quick survey of a research topic
```

## Features

### Skills Overview

| Skill | Purpose | Key Capabilities |
|-------|---------|-----------------|
| `/read-paper` | Paper/blog analysis & Q&A | Arxiv/PDF/blog analysis, depth selection (detailed/brief), code repo linking, topic-grouped Q&A with LaTeX, AlphaXiv integration, library cross-reference |
| `/daily-papers` | Daily paper recommendations | Interest-based filtering, author tracking, batch fetch, interactive selection, dedup check |
| `/survey-topic` | Research topic survey | Topic search, seed paper mode (`--papers`), idea validation (`--idea`), structured output |
| `/analyze-code` | Code repository analysis | Standalone or paper-linked, module-level analysis, paper-code mapping |
| `/manage-library` | Paper library management | Search, browse, tag, rate, promote tmp→papers, author management |
| `/session-digest` | Session summary & archive | Knowledge record, changelog generation, skill optimization suggestions |
| `/setup` | First-time setup | Interactive config of research interests, followed authors, arxiv categories |
| `/publish` | Publish public version | Clean extraction, incremental update, auto git sync |
| `/update` | Check & update system | Remote skill/doc update from GitHub, auto-check on conversation start |

### `/read-paper` — Paper & Blog Analysis

Analyze a paper or blog/project page and generate a structured report. Supports analysis depth selection, code repository linking, follow-up Q&A, and supplementary sources.

```bash
# First analysis (supports arxiv URL, ID, local PDF, blog/project page URL)
/read-paper 2401.12345
/read-paper https://arxiv.org/abs/2401.12345
/read-paper ./paper.pdf
/read-paper https://blog.example.com/post

# Specify analysis depth directly
/read-paper 2401.12345 --detailed    # Deep analysis (methods, formulas, experiments)
/read-paper 2401.12345 --brief       # Quick overview (800-1200 word summary)

# Analyze with associated code repository
/read-paper 2401.12345 --repo https://github.com/author/repo

# Custom analysis angle
/read-paper 2401.12345 --prompt Focus on the loss function design

# Add supplementary sources (for existing papers)
/read-paper 2401-12345 --supplement repo:https://github.com/author/repo
/read-paper 2401-12345 --supplement blog:https://example.com/blog-post

# Follow-up Q&A on previously analyzed papers
/read-paper 2401-12345 How does the attention mechanism differ from standard transformer?
```

**Workflow**: Fetch paper → Choose analysis depth (detailed/brief) → Create temp directory (`library/tmp/`) → Generate meta.md + analysis.md → Q&A and supplementary sources → Optionally collect to permanent library (`library/papers/`)

**Analysis Templates**: Two standalone template files in `.claude/skills/read-paper/`, customizable:
- `template-detailed.md` — Deep analysis (7 sections, including code implementation analysis)
- `template-brief.md` — Quick overview (800-1200 word summary)

### `/daily-papers` — Daily Paper Recommendations

Fetches latest papers from arxiv and intelligently filters recommendations based on your research interests.

```bash
/daily-papers                        # Today's recommendations
/daily-papers --date 2026-04-01      # Specific date
/daily-papers --days 3               # Look back 3 days
/daily-papers --category cs.CV,cs.AI # Override categories
```

**Workflow**: Python script batch-fetches paper listings → Saves CSV → Filters and ranks based on interests.md → Batch-fetches selected paper details → Generates recommendation report + paper stubs → Optionally deep-read or quick-read any paper

### `/survey-topic` — Quick Research Topic Survey

Given a research topic, seed papers, or a research idea document, generates structured analysis through multi-round searching. Supports three modes: topic-based (general search), seed-based (directed search from existing papers), and idea validation (novelty & feasibility analysis).

```bash
# Topic mode — search from scratch
/survey-topic 3D Gaussian Splatting
/survey-topic Hallucination in Vision-Language Models

# Seed mode — build survey from analyzed papers
/survey-topic --papers 2409.02095 2409.02048 2503.05638

# Mixed mode — seed papers with explicit topic
/survey-topic Explicit 3D as Video Intermediate Representation --papers 2409.02095 2409.02048 2503.05638

# Idea validation mode — validate a research idea
/survey-topic --idea path/to/my-idea.md
/survey-topic --idea "Use depth-aware attention for video inpainting"
```

**Seed mode** leverages existing paper analyses (meta.md, analysis.md) to perform directed searches: citation tracking, author tracking, method extension, baseline sourcing, and latest progress. The output includes a seed paper comparison table and technical evolution analysis.

**Idea mode** takes a research idea document (structured or free-form) and conducts adversarial investigation: searches for directly conflicting work, method precedents, alternative solutions, combination overlaps, and concurrent work. Produces a feasibility report (novelty assessment per claim), competitive analysis (per-paper comparison), and a research plan (experiments, baselines, timeline, submission targets).

**Output**:
- Topic/Seed mode: `library/topics/{slug}/overview.md` (survey) + `paper_list.md` (paper list) + meta stubs for key papers
- Idea mode: all of the above, plus `idea_source.md` (archived idea) + `feasibility.md` + `competitive_analysis.md` + `research_plan.md`

### `/analyze-code` — Code Repository Analysis

Analyzes code repository structure and key implementations, optionally cross-referenced with a paper.

```bash
/analyze-code /path/to/repo
/analyze-code https://github.com/author/repo --paper 2401-12345
```

### `/manage-library` — Paper Library Management

Browse, search, and manage your local paper library.

```bash
/manage-library                      # Statistics
/manage-library --search diffusion   # Full-text search
/manage-library --list recent        # Recent papers
/manage-library --list unread        # Unanalyzed papers
/manage-library --tag 2401-12345 vae,generation  # Add tags
/manage-library --tmp                # View temporary papers
/manage-library --promote 2401-12345 # Promote temp paper to permanent
/manage-library --clean              # Check incomplete entries
/manage-library --authors            # View followed authors list
/manage-library --rate 2401-12345 5  # Rate a paper (1-5)
```

### `/session-digest` — Session Summary & Archive

Reviews all activities in the current session and generates knowledge records and system changelogs.

```bash
/session-digest                  # Full workflow (collect → archive → optimization suggestions)
/session-digest --skip-optimize  # Skip skill optimization suggestions
```

**Output**: `library/daily/{date}.md` (knowledge record) + `.claude/changelog/{date}.md` (system changes)

### `/setup` — First-Time Setup

Interactive configuration of research interests and followed authors, generates personalized `library/interests.md`.

```bash
/setup
```

### `/publish` — Publish Public Version

Extracts a clean public version from the current repo to a target directory, skipping personal data and generating universal templates and sample content.

```bash
/publish                          # Default output to ../rose-public/
/publish ~/projects/rose-public/  # Specify output path
```

### `/update` — Check & Update System Files

Fetches latest skills, commands, and documentation from GitHub and safely updates locally. Only updates system files, never touches user data (`library/`).

```bash
/update                  # Full workflow (check → show changes → confirm → update)
/update --check          # Check only
```

**Auto-check**: At the start of each new conversation, ROSE automatically checks GitHub for updates and notifies you.

## Data Storage Structure

```
library/
├── interests.md                    # Research interest configuration (keywords, areas, arxiv categories)
├── tmp/                            # Temporary papers (analyzed but not yet collected)
│   └── {arxiv_id}-{slug}/
│       └── meta.md
├── papers/                         # Permanently collected papers
│   └── 1706-03762-transformer/
│       ├── meta.md                 # Metadata (frontmatter + summary + abstract + translation)
│       ├── analysis.md             # Detailed analysis report
│       ├── qa.md                   # Q&A records
│       └── code_analysis.md        # Code analysis (if applicable)
├── blogs/                          # Blog & project page analyses
│   └── {slug}/
│       ├── meta.md                 # Metadata (frontmatter + summary)
│       └── analysis.md             # Analysis report
├── topics/                         # Research topic surveys & idea validation
│   └── 3d-gaussian-splatting/
│       ├── overview.md
│       ├── paper_list.md
│       ├── idea_source.md          # Original idea archive (idea mode only)
│       ├── feasibility.md          # Feasibility report (idea mode only)
│       ├── competitive_analysis.md # Competitive analysis (idea mode only)
│       └── research_plan.md        # Research plan (idea mode only)
└── daily/                          # Daily records
    ├── 2026-04-02.md               # Paper recommendations + knowledge outputs
    └── 2026-04-02_raw.csv          # Raw paper listing data
```

### Paper Directory Naming Convention

`{arxiv_id}-{method_slug}`

- `.` in arxiv ID replaced with `-`
- method_slug is a short English identifier for the paper's core method/model
- Examples: `2604-01030-diff3r`, `2602-08169-spherical-steering`

### meta.md Format

Each paper's meta.md contains YAML frontmatter and three body sections:

```markdown
---
title: "Paper Title"
authors: ["Author 1", "Author 2"]
date: "2026-04-01"
arxiv_id: "2604.01030"
url: "https://arxiv.org/abs/2604.01030"
tags: [3dgs, feed-forward, differentiable-optimization]
status: meta_only | analyzed | reviewed
rating: 4  # Optional, 1-5 rating
content_type: paper  # paper | blog, type of content
source_site: ""  # Optional, for blog content: origin site name
related_papers: []  # Optional, arxiv IDs of related papers
---

## Summary
(2-3 sentences summarizing the core problem, method, and contribution)

## Abstract
(Original English abstract)

## Abstract Translation
(Chinese translation)
```

## Customizing Research Interests

Edit `library/interests.md` to configure your research areas:

```markdown
# Research Interests

## Primary Areas
- Your primary research areas

## Keywords
- Keywords for paper filtering

## Arxiv Categories
- cs.CV
- cs.AI
- (arxiv categories you follow)
```

This configuration affects `/daily-papers` filtering/ranking and `/survey-topic` search scope.

## System Architecture

```
.claude/
├── commands/           # Slash command entry points (thin wrappers)
│   ├── read-paper.md
│   ├── daily-papers.md
│   ├── survey-topic.md
│   ├── analyze-code.md
│   ├── manage-library.md
│   ├── session-digest.md
│   ├── setup.md
│   ├── publish.md
│   └── update.md
├── skills/             # Skill implementations (prompts + scripts)
│   ├── read-paper/
│   │   ├── read-paper.md       # Skill prompt
│   │   ├── template-detailed.md # Deep analysis template
│   │   ├── template-brief.md   # Quick overview template
│   │   └── arxiv_fetch.py      # Paper metadata fetcher
│   ├── daily-papers/
│   │   ├── daily-papers.md
│   │   └── arxiv_daily.py      # Batch paper listing + alphaxiv details
│   ├── survey-topic/
│   ├── analyze-code/
│   ├── manage-library/
│   ├── session-digest/
│   ├── setup/
│   ├── publish/
│   └── update/         # Auto-update check + check_update.sh
└── changelog/          # System changelogs
```

**Design Principles**:

- **Commands are thin wrappers**: Only reference prompts in skills/, no logic
- **Skills are self-contained**: Each skill's prompt and scripts live in the same directory
- **Python scripts use stdlib only**: Zero external dependencies, runs anywhere
- **Data-logic separation**: `library/` stores data, `.claude/` stores logic

## Extending & Evolving

- **Add a new skill**: Create subdirectory in `.claude/skills/` → Write prompt and scripts → Add entry in `.claude/commands/` → Update CLAUDE.md
- **Modify existing skill**: Edit `.claude/skills/{name}/*.md` directly, takes effect immediately
- **Feature roadmap**: See [ROADMAP.md](./ROADMAP.md)

## Contributing

Contributions welcome — new skills, feature improvements, or bug fixes.

**Workflow**:

1. Fork this repo and clone locally
2. Make your changes (add/modify skills, fix bugs, etc.)
3. Run `/publish` to generate a clean release version, verify your changes work correctly
4. Submit a PR describing your changes and motivation

**Adding a New Skill**:

1. Create skill directory at `.claude/skills/{name}/`, write prompt (`.md`) and scripts (if needed)
2. Add command entry at `.claude/commands/{name}.md`
3. Update the Skills table in `CLAUDE.md` and feature descriptions in `README.md` / `README-zh.md`
4. Python scripts must use stdlib only, no external dependencies

**Notes**:

- Do not commit personal data (`library/papers/`, `library/tmp/`, `library/daily/`, etc.)
- Do not commit `.claude/settings.local.json` (excluded in `.gitignore`)
- Skill prompts are in Chinese, code comments in English

## Related Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Claude Code project instructions (conventions and internal rules) |
| `ROADMAP.md` | Feature roadmap and idea collection |
| `library/interests.md` | Research interest configuration |

## References
https://www.alphaxiv.org/skills/alphaxiv-paper-lookup/SKILL.md
