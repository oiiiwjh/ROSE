# ROSE - Research Observation & Study Engine

基于 [Claude Code](https://claude.ai/claude-code) Skills 的个人科研探索系统。通过 slash commands 在终端中完成论文阅读分析、每日推荐、方向调研、论文库管理等工作流，所有产出结构化存储在本地。

## 前置条件

- [Claude Code](https://claude.ai/claude-code) CLI 已安装
- Python 3.10+（仅使用标准库，无需额外依赖）
- 网络可访问 arxiv.org 和 alphaxiv.org

## 快速开始

```bash
# 1. 进入项目目录
cd rose

# 2. 首次使用，运行设置向导
/setup

# 3. 开始使用
/daily-papers              # 获取今日论文推荐
/read-paper 2401.12345     # 深度分析一篇论文
/survey-topic 3D Gaussian Splatting   # 快速掌握一个方向
```

## 功能一览

### `/read-paper` — 论文深度阅读

分析一篇论文并生成结构化报告，支持选择分析深度、关联代码仓库、后续追问和补充信息源。

```bash
# 首次分析（支持 arxiv URL、ID、本地 PDF）
/read-paper 2401.12345
/read-paper https://arxiv.org/abs/2401.12345
/read-paper ./paper.pdf

# 直接指定分析深度
/read-paper 2401.12345 --detailed    # 深度分析（详细拆解方法、公式、实验）
/read-paper 2401.12345 --brief       # 快速概览（800-1200 字核心速览）

# 关联代码仓库一起分析
/read-paper 2401.12345 --repo https://github.com/author/repo

# 自定义分析角度
/read-paper 2401.12345 --prompt 重点分析 loss 函数设计

# 补充信息源（对已有论文追加分析）
/read-paper 2401-12345 --supplement repo:https://github.com/author/repo
/read-paper 2401-12345 --supplement blog:https://example.com/blog-post

# 对已分析过的论文追问
/read-paper 2401-12345 这篇的 attention 机制和标准 transformer 有什么区别？
```

**工作流程**：获取论文 → 选择分析深度（深度/概览）→ 创建临时目录（`library/tmp/`）→ 生成 meta.md + analysis.md → 支持 Q&A 追问与补充信息源 → 结束时询问是否收藏到正式库（`library/papers/`）

**分析模板**：两个独立模板文件位于 `.claude/skills/read-paper/`，可根据需要自定义修改：
- `template-detailed.md` — 深度分析（七大章节，含代码实现分析）
- `template-brief.md` — 快速概览（800-1200 字速览）

### `/daily-papers` — 每日论文推荐

基于你的研究兴趣，从 arxiv 获取最新论文并智能筛选推荐。

```bash
/daily-papers                        # 今日推荐
/daily-papers --date 2026-04-01      # 指定日期
/daily-papers --days 3               # 回溯 3 天
/daily-papers --category cs.CV,cs.AI # 覆盖分类
```

**工作流程**：Python 脚本批量抓取论文列表 → 保存 CSV → 基于 interests.md 筛选排序 → 批量获取精选论文详情 → 生成推荐报告 + paper stubs → 可直接选择某篇进行深度分析或快速概览

### `/survey-topic` — 研究方向快速掌握

给定一个研究方向，通过多轮搜索生成结构化综述。

```bash
/survey-topic 3D Gaussian Splatting
/survey-topic 视觉语言模型中的幻觉问题
```

**产出**：`library/topics/{slug}/overview.md`（综述）+ `paper_list.md`（论文列表）+ 核心论文的 meta stubs

### `/analyze-code` — 代码仓库分析

分析代码仓库结构和关键实现，可选关联论文进行交叉分析。

```bash
/analyze-code /path/to/repo
/analyze-code https://github.com/author/repo --paper 2401-12345
```

### `/manage-library` — 论文库管理

浏览、搜索和管理本地论文库。

```bash
/manage-library                      # 统计信息
/manage-library --search diffusion   # 全文搜索
/manage-library --list recent        # 最近论文
/manage-library --list unread        # 未分析的论文
/manage-library --tag 2401-12345 vae,generation  # 打标签
/manage-library --tmp                # 查看临时论文
/manage-library --promote 2401-12345 # 临时论文转正
/manage-library --clean              # 检查不完整条目
```

### `/session-digest` — 会话总结归档

回顾当前会话的所有活动，生成知识记录和系统变更日志。

```bash
/session-digest                  # 完整流程（采集→归档→优化建议）
/session-digest --skip-optimize  # 跳过 skill 优化建议
```

**产出**：`library/daily/{date}.md`（知识记录）+ `.claude/changelog/{date}.md`（系统变更）

### `/setup` — 首次使用引导

交互式配置研究兴趣、关注作者，生成个性化的 `library/interests.md`。

```bash
/setup
```

### `/publish` — 发布公共版本

从当前仓库提取干净的 public 版本到指定目录，跳过个人数据，生成通用模板和示例内容。

```bash
/publish                          # 默认输出到 ../rose-public/
/publish ~/projects/rose-public/  # 指定输出路径
```

## 数据存储结构

```
library/
├── interests.md                    # 研究兴趣配置（关键词、领域、arxiv 分类）
├── tmp/                            # 临时论文（分析后未收藏的）
│   └── {arxiv_id}-{method_slug}/
│       └── meta.md
├── papers/                         # 正式收藏的论文
│   └── 1706-03762-transformer/     # 示例论文
│       ├── meta.md                 # 元信息（frontmatter + 概要 + abstract + 翻译）
│       ├── analysis.md             # 详细分析报告
│       └── qa.md                   # Q&A 记录（如有）
├── topics/                         # 研究方向综述
│   └── {topic-slug}/
│       ├── overview.md
│       └── paper_list.md
└── daily/                          # 每日记录
    ├── {YYYY-MM-DD}.md             # 论文推荐 + 知识产出
    └── {YYYY-MM-DD}_raw.csv        # 原始论文列表数据
```

### 论文目录命名规则

`{arxiv_id}-{method_slug}`

- arxiv ID 中的 `.` 替换为 `-`
- method_slug 是论文核心方法/模型的简短英文标识
- 示例：`1706-03762-transformer`、`2401-12345-nerf`

### meta.md 格式

每篇论文的 meta.md 包含 YAML frontmatter 和三段正文：

```markdown
---
title: "Paper Title"
authors: ["Author 1", "Author 2"]
date: "2026-04-01"
arxiv_id: "2604.01030"
url: "https://arxiv.org/abs/2604.01030"
tags: [3dgs, feed-forward, differentiable-optimization]
status: meta_only | analyzed | reviewed
---

## 概要总结
（中文 2-3 句话概括核心问题、方法和贡献）

## Abstract
（英文原文）

## 摘要翻译
（中文翻译）
```

## 自定义研究兴趣

编辑 `library/interests.md` 配置你的研究方向：

```markdown
# Research Interests

## Primary Areas
- 你的主要研究方向（中英文均可）

## Keywords
- 用于论文筛选的关键词列表

## Arxiv Categories
- cs.CV
- cs.AI
- （你关注的 arxiv 分类）

## Followed Authors
- **作者名** — 代表作: [论文标题](arxiv_url) (arxiv_id), 机构
```

此配置影响 `/daily-papers` 的筛选排序和 `/survey-topic` 的搜索范围。推荐使用 `/setup` 进行交互式配置。

## 系统架构

```
.claude/
├── commands/           # Slash command 入口（薄包装）
│   ├── read-paper.md
│   ├── daily-papers.md
│   ├── survey-topic.md
│   ├── analyze-code.md
│   ├── manage-library.md
│   ├── session-digest.md
│   ├── setup.md
│   └── publish.md
├── skills/             # Skill 实现（prompt + 脚本）
│   ├── read-paper/
│   │   ├── read-paper.md       # skill prompt
│   │   ├── template-detailed.md # 深度分析模板
│   │   ├── template-brief.md   # 快速概览模板
│   │   └── arxiv_fetch.py      # 论文元信息获取
│   ├── daily-papers/
│   │   ├── daily-papers.md
│   │   └── arxiv_daily.py      # 批量论文列表抓取 + alphaxiv 详情
│   ├── survey-topic/
│   ├── analyze-code/
│   ├── manage-library/
│   ├── session-digest/
│   ├── setup/
│   └── publish/
└── changelog/          # 系统变更日志
```

**设计原则**：

- **commands 是薄入口**：只引用 skills/ 中的 prompt，不含逻辑
- **skills 独立自治**：每个 skill 的 prompt 和脚本放在同一目录
- **Python 脚本仅用标准库**：零外部依赖，随处可运行
- **数据与逻辑分离**：`library/` 存数据，`.claude/` 存逻辑

## 扩展与演进

- **添加新 skill**：在 `.claude/skills/` 下建子目录 → 写 prompt 和脚本 → 在 `.claude/commands/` 加入口 → 更新 CLAUDE.md
- **修改现有 skill**：直接编辑 `.claude/skills/{name}/*.md`，立即生效
- **功能规划**：详见 [ROADMAP.md](./ROADMAP.md)

## 相关文件

| 文件 | 用途 |
|------|------|
| `CLAUDE.md` | Claude Code 项目指令（系统约定和内部规范） |
| `ROADMAP.md` | 功能规划与想法收集 |
| `library/interests.md` | 研究兴趣配置 |

## 参考内容
https://www.alphaxiv.org/skills/alphaxiv-paper-lookup/SKILL.md