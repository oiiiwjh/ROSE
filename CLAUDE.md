# ROSE — Research Operating System for Erudition

> 当前版本: v1.0.4 | [变更日志](.claude/changelog/)

基于 Claude Code Skills 的科研探索系统。通过 slash commands 实现论文阅读分析、每日推荐、方向调研等功能。

## 目录结构

- `.claude/commands/` — Slash command 入口（薄包装，引用 skills/）
- `.claude/skills/{name}/` — 每个 Skill 独立目录（prompt + 脚本 + 扩展文件）
- `library/` — 所有研究数据存储
  - `library/README.md` — 自动生成的论文索引（由 `generate_index.py` 维护，勿手动编辑）
  - `library/interests.md` — 用户研究兴趣配置（影响推荐过滤）
  - `library/tmp/{arxiv_id}-{method_slug}/` — 临时论文（所有论文先进 tmp，确认收藏后转正）
  - `library/papers/{arxiv_id}-{method_slug}/` — 正式收藏的论文（meta.md, analysis.md, qa.md, sources.md, notes.md）
  - `library/topics/{slug}/` — 按研究方向存储（overview.md, paper_list.md）
  - `library/daily/{YYYY-MM-DD}.md` — 每日知识记录（论文推荐 + 会话知识产出）
- `.claude/changelog/{YYYY-MM-DD}.md` — 系统功能变更日志（skill 变更、debug 修复等）

## 可用 Skills

| 命令 | 用途 | 示例 |
|------|------|------|
| `/read-paper` | 论文分析与 Q&A | `/read-paper 2401.12345` 首次分析；`--detailed` / `--brief` 指定深度；`--supplement repo:...` 补充信息源；分析后自动关联库存论文 |
| `/analyze-code` | 独立代码仓库分析 | `/analyze-code /path/to/repo --paper 2401-12345`（不关联论文时使用，关联论文用 read-paper --repo） |
| `/daily-papers` | 每日论文推荐 | `/daily-papers` 或 `/daily-papers --date 2024-01-15` |
| `/survey-topic` | 研究方向快速掌握 | `/survey-topic 3D Gaussian Splatting`；种子模式：`/survey-topic --papers 2409.02095 2409.02048`；混合：`/survey-topic 显式3D作为视频表示 --papers 2409.02095 2409.02048 2503.05638`；Idea 验证：`/survey-topic --idea path/to/idea.md` 或 `/survey-topic --idea "用depth-aware attention做video inpainting"` |
| `/manage-library` | 本地库管理 | `/manage-library --search diffusion`、`--authors`、`--rate <id> <score>` |
| `/session-digest` | 会话总结归档 | `/session-digest` 完整流程；`/session-digest --skip-optimize` 跳过优化建议 |
| `/setup` | 首次使用引导 | `/setup` 交互式配置研究兴趣、关注作者 |
| `/publish` | 发布公共版本 | `/publish` 或 `/publish ~/projects/rose-public/` |
| `/update` | 检查并更新系统文件 | `/update` 完整流程；`/update --check` 仅检查 |

## 约定

- 论文目录名：`{arxiv_id}-{method_slug}`，其中 arxiv ID 的 `.` 替换为 `-`，method_slug 是论文核心方法/模型的简短英文标识（如 `2401-12345-nerf`、`2503-08017-adaptive-token-pruning`）
- 日期格式：ISO `YYYY-MM-DD`
- 分析输出语言：中文为主
- meta.md 使用 YAML frontmatter
- Python 脚本随 skill 就近存放，仅使用 stdlib，无外部依赖

## meta.md 格式

```markdown
---
title: "Paper Title"
authors: ["Author 1", "Author 2"]
date: "2024-01-15"
arxiv_id: "2401.12345"
url: "https://arxiv.org/abs/2401.12345"
tags: [diffusion, image-generation]
status: meta_only | analyzed | reviewed
rating: 4  # 可选，1-5 评分
repo: "https://github.com/author/repo"  # 可选，关联代码仓库
supplements: ["twitter:https://...", "blog:https://..."]  # 可选，补充信息源
source: daily-papers  # 来源 skill（daily-papers / read-paper / survey-topic）
collected_date: "2026-04-07"  # 收集到 library 的日期
---

## 概要总结

（中文 2-3 句话概括核心问题、方法和贡献）

## Abstract

（英文原文）

## 摘要翻译

（中文翻译）
```

## 自动更新检查

每次新对话开始时（用户的第一条消息不是 slash command 时），静默运行 `bash .claude/skills/update/check_update.sh`：
- 如果有更新：简短告知用户（如："ROSE 有 N 个系统文件更新可用（v1.0.1 → v1.0.2），运行 `/update` 查看详情"），然后继续处理用户的请求
- 如果无更新或网络不通：不输出任何内容，直接处理用户请求
- 不要阻断用户的工作流，只展示一行提示即可

## 演进方式

- 添加 skill：在 `.claude/skills/` 下建子目录放 prompt 和脚本，在 `.claude/commands/` 加薄入口，更新此文件
- 更新 skill：编辑 `.claude/skills/{name}/*.md`，立即生效（无需改 commands）
- 数据兼容：新 skill 应兼容旧数据格式
- 功能规划与想法记录：见 `ROADMAP.md`
- **文档同步规则**：每次有较大更新（新增/修改 skill、变更数据结构、调整流程等）时，必须同时更新 `README.md`（英文）、`README-zh.md`（中文）、`CLAUDE.md`、`ROADMAP.md` 等相关文档，确保文档与实际行为一致
- **版本控制**：
  - 本文件头部的「当前版本」为唯一权威版本号
  - 语义化版本：Major（架构变更）/ Minor（功能里程碑）/ Patch（增量改进）
  - ROADMAP 中 v1.0/v1.5/v2.0 为 Minor 里程碑规划，实际交付用三段版本号（如 v1.0.1）
  - 每次 `/session-digest` 或 `/publish` 时，检查 ROADMAP 想法收集，将已完成条目整合到当前 patch 版本段落
