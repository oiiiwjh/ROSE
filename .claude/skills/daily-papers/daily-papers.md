---
description: "每日论文爬取与推荐。基于研究兴趣筛选 arxiv 最新论文"
---

# 每日论文推荐

你是科研论文推荐助手。请基于用户的研究兴趣，从 arxiv 获取近期论文并生成个性化推荐。

## 输入解析

用户输入: $ARGUMENTS

可选参数:
- `--date YYYY-MM-DD`: 指定日期（默认今天）
- `--category cs.CV,cs.AI,...`: 覆盖默认分类
- `--days N`: 回溯天数（默认 2）

## 执行步骤

### Step 1: 读取用户兴趣

读取 `library/interests.md`，获取:
- 主要研究领域
- 关键词列表
- Arxiv 分类列表

### Step 2: 批量获取论文列表（一次性完成）

运行 Python 脚本一次性抓取所有论文并保存到本地 CSV：

```bash
python3 .claude/skills/daily-papers/arxiv_daily.py list \
  --categories <categories> --days <days> \
  -o library/daily/{YYYY-MM-DD}_raw.csv
```

- categories 来自 interests.md 或用户参数
- 脚本通过 HTML 页面抓取，一次请求获取所有论文（标题、作者、分类）
- 如果 HTML 抓取失败，自动 fallback 到 arxiv API
- 结果保存为 CSV，包含 arxiv_id, title, authors, primary_category, url 等字段

### Step 3: 智能筛选与排序

读取 CSV 文件，结合用户的研究兴趣和行为数据进行筛选排序：

**信号源**（从 `library/interests.md` 读取）：
1. **基础关键词匹配**: `## Keywords` 中的关键词与论文标题匹配
2. **关键词权重加权**: `## Keyword Weights` 中的权重反映实际阅读行为——权重高的关键词命中时，relevance score 按比例提升（如 `3dgs: 5` 比 `nerf: 2` 贡献更高分数）
3. **关注作者加权**: `## Followed Authors` 中的作者出现在论文作者列表时，relevance score 额外加分
4. **分类筛选**: 优先展示与用户主要领域高度相关的论文

**输出**：
1. **精选 Top Picks**: 选出 3-5 篇最值得关注的论文
2. **推荐阅读**: 再选 5-10 篇次要推荐
3. 关注作者的论文在输出中标注 `[关注作者]`

### Step 3.5: 批量获取精选论文详情（一次性完成）

对精选 Top Picks 的论文，运行脚本一次性获取 AlphaXiv 分析报告：

```bash
python3 .claude/skills/daily-papers/arxiv_daily.py detail \
  --ids <id1>,<id2>,<id3>,... \
  -o library/daily/{YYYY-MM-DD}_details.json
```

- 脚本内部批量请求 alphaxiv，自带 rate limiting
- 结果保存为 JSON，用于生成推荐理由和中文摘要
- 如果某篇论文 alphaxiv 无数据，基于标题和已有信息生成推荐

### Step 4: 生成每日推荐文件

将结果保存到 `library/daily/{YYYY-MM-DD}.md`，格式:

```markdown
# Daily Papers - {YYYY-MM-DD}

> 基于 interests.md 从 {categories} 中筛选，共扫描 {N} 篇论文

## 精选推荐

### 1. [{论文标题}]({arxiv_url})
**作者**: ... | **分类**: cs.CV
> 推荐理由：...
>
> 摘要：（简要中文翻译）

### 2. ...

## 值得关注

- [{标题}]({url}) — 一句话描述
- ...

## 完整列表

| # | 标题 | 分类 | 相关度 |
|---|------|------|--------|
| 1 | ... | ... | ★★★ |
```

### Step 5: 创建 paper stubs

为精选推荐的论文自动创建 `library/tmp/{id}-{method_slug}/meta.md` stub（status: meta_only），方便后续用 `/read-paper` 深入阅读。其中 `{method_slug}` 从论文标题/摘要中提炼出核心方法的简短英文标识（规则同 read-paper skill）。

meta.md 正文必须包含三段（格式同 CLAUDE.md 中的 meta.md 规范）：
1. **概要总结** — 中文 2-3 句话概括核心问题、方法和贡献
2. **Abstract** — 英文原文
3. **摘要翻译** — Abstract 的中文翻译

如果 Step 3.5 的 alphaxiv detail 返回了该论文的摘要，直接使用；否则从 CSV 中已有信息或标题推断生成概要总结即可（Abstract 和翻译可标注"待补充"）。

### Step 6: 输出摘要与后续操作

向用户展示今日精选推荐的简要列表，并告知完整推荐已保存到哪个文件。

展示完成后，使用 AskUserQuestion 询问：

> 是否有想要深入阅读的论文？

选项：
- **深度分析某篇**：用户指定论文编号，按 `/read-paper --detailed` 的流程进行深度分析（读取 `template-detailed.md` 模板）
- **快速浏览某篇**：用户指定论文编号，按 `/read-paper --brief` 的流程进行快速概览（读取 `template-brief.md` 模板）
- **暂不深入**：结束本次推荐

如果用户选择深入阅读，对应论文已有 `library/tmp/` 下的 stub，直接在此基础上补充 analysis.md。分析完成后回到此步，继续询问是否还要阅读其他论文。
