---
description: "发布公共版本。从当前仓库提取干净的 public 版本到指定目录"
---

# ROSE 公共版本发布

你是 ROSE 系统的发布助手。从当前私人仓库中提取干净的公共版本，跳过个人数据，生成通用模板和示例内容。

**核心原则**：当前仓库（rose/）不做任何修改，所有操作在目标目录中进行。

## Step 0: 准备目标目录

GitHub 仓库地址：`https://github.com/oiiiwjh/ROSE`

在开始发布前，确保目标目录与远程仓库同步：

1. **目标目录不存在**：从 GitHub clone 仓库到目标路径
   ```bash
   git clone https://github.com/oiiiwjh/ROSE.git {target_path}
   ```
2. **目标目录已存在且有 git 历史**：拉取最新远程更新
   ```bash
   cd {target_path} && git pull --rebase origin main
   ```
3. **目标目录已存在但无 git 历史**：先 `git init`，添加 remote，再 pull

这样确保增量更新始终基于最新的远程状态进行。

## 输入解析

用户输入: $ARGUMENTS

格式: `[target_path] [--dry-run]`

- `target_path`（可选）：输出目录路径，默认为当前仓库的同级目录 `../rose-public/`
- `--dry-run`（可选）：仅展示将执行的操作列表，不实际创建/修改任何文件
- 如果目标目录已存在且非空（且非 git 仓库），询问用户是否覆盖

### Dry-run 模式

如果指定了 `--dry-run`，按以下格式展示操作预览后结束，不执行任何文件操作：

```
[Dry Run] ROSE 公共版本发布预览

目标目录: {target_path}

将复制的文件:
  .claude/commands/*.md (8 files)
  .claude/skills/read-paper/  (skill + arxiv_fetch.py + templates)
  .claude/skills/daily-papers/ (skill + arxiv_daily.py)
  .claude/skills/survey-topic/
  .claude/skills/analyze-code/
  .claude/skills/manage-library/
  .claude/skills/session-digest/
  .claude/skills/setup/
  .claude/skills/publish/
  .claude/changelog/*
  README.md, README-zh.md, CLAUDE.md, ROADMAP.md, config.md

将跳过的文件:
  .claude/settings.local.json
  brainstorm.md, add.md, temp_skills/
  library/papers/*, library/tmp/*, library/daily/*, library/topics/*
  library/interests.md (替换为通用模板)

将生成的新文件:
  library/interests.md (通用模板，含 3 位示例作者)
  library/papers/1706-03762-transformer/meta.md (示例论文)
  library/papers/1706-03762-transformer/analysis.md (示例分析)
  .gitignore (增强版)
  LICENSE (MIT)

将微调的文档:
  README.md (EN) / README-zh.md (ZH) — 快速开始改为 /setup，示例改为 transformer
  CLAUDE.md — Skills 表添加 /setup 和 /publish

将执行: git init + 首次 commit
```

---

## Step 1: 确认发布配置

使用 AskUserQuestion 确认：

**问题**：确认发布配置？

选项：
- **使用默认配置** — 输出到 `{target_path}`，包含示例论文（Attention Is All You Need），MIT LICENSE
- **自定义配置** — 调整输出路径、示例论文、LICENSE 类型等

如果选择自定义，逐项询问：
1. 输出路径
2. 是否包含示例论文（默认 yes）
3. LICENSE 类型（MIT / Apache 2.0 / 无）

---

## Step 2: 复制通用文件

从当前仓库复制以下文件到目标目录（保持目录结构）：

### 2.1 Skills 和 Commands（原样复制）

```
.claude/commands/*.md          — 所有 command 入口
.claude/skills/*/              — 所有 skill 目录（自动扫描，无需硬编码列表）
```

**复制方式**：
- Commands: `cp .claude/commands/*.md {target}/.claude/commands/`
- Skills: 遍历 `.claude/skills/` 下所有子目录，使用 `cp -r` 递归复制每个 skill 目录，确保包含所有子文件（.md、.py 等）。不硬编码 skill 名称，新增 skill 自动包含。

### 2.2 文档文件（复制后需微调）

```
README*.md                     — 自动扫描所有语言版本（README.md, README-zh.md, ...）
CLAUDE.md
ROADMAP.md
config.md
```

**复制方式**：使用 glob `README*.md` 自动检测所有语言版本，新增语言无需手动更新列表。

### 2.3 Changelog（原样复制）


```
.claude/changelog/*            — 系统功能变更日志
```

### 2.4 不复制的文件

```
.claude/settings.local.json    — 含个人硬编码路径
.vscode/                       — 编辑器配置（用户自定义）
brainstorm.md                  — 个人笔记
add.md                         — 个人笔记
temp_skills/                   — 参考收集
library/papers/*               — 个人论文数据
library/tmp/*                  — 个人临时数据
library/daily/*                — 个人每日记录
library/topics/*               — 个人方向综述
library/interests.md           — 个人研究兴趣（替换为通用模板）
```

---

## Step 3: 创建空目录结构

在目标目录中创建：

```bash
mkdir -p library/papers/
mkdir -p library/tmp/
mkdir -p library/topics/
mkdir -p library/daily/
```

每个空目录放一个 `.gitkeep` 文件以确保 git 跟踪。

---

## Step 4: 生成示例论文（Attention Is All You Need）

如果用户选择包含示例论文：

### 4.1 获取论文元信息

运行 `python3 .claude/skills/read-paper/arxiv_fetch.py --id 1706.03762` 获取元信息。

### 4.2 创建示例目录

在目标目录的 `library/papers/1706-03762-transformer/` 下创建文件。

### 4.3 生成 meta.md

按标准 meta.md 格式生成，包含：
- frontmatter（title, authors, date, arxiv_id, url, tags, status: analyzed）
- 概要总结（中文）
- Abstract（英文原文）
- 摘要翻译（中文）

### 4.4 生成 analysis.md

获取论文详细信息（优先使用 AlphaXiv：`curl -s "https://alphaxiv.org/overview/1706.03762.md"`），按 `template-detailed.md` 的结构生成完整分析。

这是公开发布的示例，分析质量要高，展示系统的分析能力。

---

## Step 5: 生成通用 interests.md

在目标目录的 `library/interests.md` 创建通用模板：

```markdown
---
schema_version: 2
---

# Research Interests

## Primary Areas
<!-- 通过 /setup 配置，或手动编辑 -->
<!-- 示例:
- Computer Vision (CV)
- Natural Language Processing (NLP)
- Multimodal / Vision-Language
-->

## 研究方向描述

<!-- 用自然语言描述研究兴趣，供论文筛选时做语义匹配 -->
<!-- 通过 /setup 配置，或手动编辑 -->
<!-- 示例:
### Computer Vision
关注 diffusion model 在图像/视频生成方面的进展，对目标检测不太感兴趣。
-->

## 代表性高分论文

<!-- 评分 ≥4 的论文描述自动追加，作为兴趣画像的一部分 -->
<!-- 格式: - [{arxiv_id}] 一句话描述论文核心贡献和你感兴趣的点 -->

## Followed Authors

<!-- 手动添加或评分 ≥4 自动加入 -->
<!-- 格式: 作者名: {count, last_paper, note} -->

<!-- 示例（可删除）: -->
Kaiming He: {count: 1, last_paper: "2111.06377", note: "MAE — 自监督视觉表示学习"}
Saining Xie: {count: 1, last_paper: "2201.03545", note: "ConvNeXt — 现代卷积网络设计"}

## Arxiv Categories
<!-- 用于 /daily-papers 抓取范围 -->
- cs.CV
- cs.CL
- cs.AI
- cs.LG

## 兴趣权重

<!-- 自动维护，反映实际阅读行为 -->
<!-- 分析完成时，从论文 tags 中提取主题词 +1；收藏额外 +1 -->
<!-- 用于对描述匹配的候选论文做二次排序，不作为筛选条件 -->
```

---

## Step 6: 生成 .gitignore

在目标目录创建增强版 .gitignore：

```
# PDFs (可能过大)
*.pdf

# Python
__pycache__/
*.pyc

# OS
.DS_Store

# Config with secrets
config.md

# Personal settings
.claude/settings.local.json

# Temp files
temp_skills/
```

---

## Step 7: 生成 LICENSE

根据用户选择的类型生成。默认 MIT：

```
MIT License

Copyright (c) {current_year} {用户名或占位符}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

使用 AskUserQuestion 询问 LICENSE 中的版权持有人名称。

---

## Step 8: 微调文档

源文件中的大部分内容（快速开始用 /setup、skills 表含 /setup 和 /publish、架构图、Contributing 段等）已经是最新的，复制过来直接可用。

仅需在目标目录中做以下调整：

### 8.1 README.md / README-zh.md — 替换个人数据示例

对英文 `README.md` 和中文 `README-zh.md` 同步执行：

将「数据存储结构」中的个人论文目录替换为示例论文：

```
├── papers/
│   └── 1706-03762-transformer/       # 示例论文
│       ├── meta.md
│       └── analysis.md
```

移除 `tmp/` 下的个人论文条目，保留空目录说明。

### 8.2 CLAUDE.md — 无需额外调整

源文件已包含所有更新，原样复制即可。

---

## Step 9: 初始化 Git

在目标目录中：

```bash
cd {target_path}
git init
git add -A
git commit -m "Initial release: ROSE — Research Operating System for Erudition

A Claude Code skill-based research exploration system for paper reading,
daily recommendations, topic surveys, code analysis, and library management."
```

---

## Step 10: 验证与完成

### 10.1 验证文件完整性

检查以下关键文件是否存在：
- `.claude/commands/` 下的 command 文件数量与源仓库一致
- `.claude/skills/` 下的 skill 目录数量与源仓库一致
- `library/interests.md`
- `library/papers/1706-03762-transformer/meta.md`（如有示例）
- `library/papers/1706-03762-transformer/analysis.md`（如有示例）
- `README.md`、`README-zh.md`、`CLAUDE.md`、`ROADMAP.md`
- `.gitignore`、`LICENSE`

### 10.2 验证网络连通性

运行 `python3 {target_path}/.claude/skills/read-paper/arxiv_fetch.py --search "test" --max 1` 测试。

### 10.3 展示完成信息

```
ROSE 公共版本已生成！

输出目录: {target_path}
Git 状态: 已初始化，首次提交完成

包含内容:
  8 个 slash commands（read-paper, daily-papers, survey-topic, analyze-code,
                       manage-library, session-digest, setup, publish）
  示例论文: Attention Is All You Need (1706.03762)
  通用 interests.md 模板（含 3 位示例作者）
  MIT LICENSE

接下来你可以：
  cd {target_path}
  git remote add origin <your-repo-url>
  git push -u origin main

原始仓库未做任何修改。
```

---

## 发布前检查

每次发布前，自动执行以下检查：

1. **版本一致性**：读取 CLAUDE.md 的「当前版本」，确保 ROADMAP 中有对应版本段落
2. **ROADMAP 想法整理**：检查 ROADMAP「想法收集 → 待整理」中的条目，执行以下整理：
   - 已完成的条目：移至「已整合」，标注 `[已整合 → vX.X.X]`
   - 可归入现有版本规划的条目：整合到对应版本段落的描述中，移至「已规划」，标注 `[已规划 → vX.X]`
   - 涉及外部参考链接的条目：将参考链接保留在版本规划的对应条目中，方便后续查阅
   - 无法归类的条目：保留在「待整理」中
   - 整理后「待整理」如果为空，写 `（暂无）`
3. **changelog 完整性**：确保当天的 changelog 已记录本次发布包含的变更

---

## 增量更新说明

如果目标目录已存在且有 git 历史：

0. **先同步远程**：`git pull --rebase origin main`（确保基于最新远程状态）
1. **不覆盖用户数据**：跳过 `library/interests.md`、`library/papers/`、`library/daily/` 等
2. **更新 skills 和 commands**：覆盖 `.claude/commands/` 和 `.claude/skills/` 中的文件
3. **更新 changelog**：覆盖 `.claude/changelog/` 中的文件
4. **更新文档**：覆盖 README.md、README-zh.md、CLAUDE.md、ROADMAP.md
5. **保留 LICENSE 和 .gitignore**：不覆盖（用户可能已修改）
6. **自动 commit + push**（用户确认后执行）：
   - 展示 `git diff --stat` 让用户 review 变更
   - 使用 AskUserQuestion 询问是否自动 commit 并 push
   - 如果确认：`git add -A && git commit -m "sync: update skills, docs and changelog" && git push origin main`
   - 如果拒绝：仅提示用户手动操作
