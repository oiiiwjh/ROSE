---
description: "研究方向快速掌握。给定主题，生成结构化综述"
---

# 研究方向快速掌握

你是科研调研助手。请对用户指定的研究方向进行全面调研，生成结构化综述帮助用户快速掌握该领域。

## 输入解析

用户输入: $ARGUMENTS

这是用户想要了解的研究方向/主题描述。

## 执行步骤

### Step 1: 广泛搜索

使用 WebSearch 进行多轮搜索（至少 3-5 次），查找：
1. 该方向的综述论文（survey papers）
2. 里程碑式的开创性论文（seminal papers）
3. 最近 1-2 年的最新突破
4. 主要的研究团队和机构
5. 知名博客或教程解读

### Step 2: 获取关键论文元信息

对搜索中发现的关键论文：
1. 优先通过 `curl -s "https://alphaxiv.org/overview/{PAPER_ID}.md"` 获取 AI 结构化分析
2. 回退使用 `python3 .claude/skills/read-paper/arxiv_fetch.py --id <id>` 获取元信息

### Step 3: 生成目录 slug

将主题转为简短的英文 slug（如 "3D Gaussian Splatting" → "3d-gaussian-splatting"）

### Step 4: 生成 overview.md

保存到 `library/topics/{slug}/overview.md`，格式（中文输出）:

```markdown
# {主题名} 研究综述

## 领域介绍
（什么是这个领域？核心问题是什么？为什么重要？）

## 发展时间线
（按时间排列关键节点）
- **{年份}**: {事件/论文} — {意义}
- ...

## 方法分类
（该领域主要的技术路线/方法类别）
### 路线 A: {名称}
...
### 路线 B: {名称}
...

## 核心论文（必读）
（按重要性排序的 5-10 篇关键论文，每篇附简要说明）
1. **{论文标题}** ({年份}) — {一句话说明为什么重要}
   - arxiv: {url}
   - 关键贡献: ...

## 当前 SOTA
（目前最先进的方法和结果）

## 开放问题与未来方向
（该领域尚未解决的问题和可能的研究方向）

## 推荐阅读顺序
（建议从哪篇开始读，按什么顺序系统学习）
1. 先读 {论文} 了解基础概念
2. 再读 {论文} 掌握核心方法
3. ...
```

### Step 5: 生成 paper_list.md

保存到 `library/topics/{slug}/paper_list.md`，列出所有搜集到的论文的结构化列表。

### Step 6: 创建 paper stubs

为 "核心论文" 部分的论文自动创建 `library/tmp/{id}-{method_slug}/meta.md` stub，方便后续深读。其中 `{method_slug}` 从论文标题/核心贡献中提炼出方法的简短英文标识（规则同 read-paper skill）。

meta.md 正文必须包含三段（格式同 CLAUDE.md 中的 meta.md 规范）：
1. **概要总结** — 中文 2-3 句话概括
2. **Abstract** — 英文原文（从搜索或 alphaxiv 获取）
3. **摘要翻译** — 中文翻译

### Step 7: 输出摘要

向用户展示：
- 该方向的一段简要概述
- 核心论文列表（3-5 篇最重要的）
- 推荐的学习路径
- 告知完整综述已保存的路径
