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
- `## 研究方向描述` — 自然语言描述的研究兴趣（含感兴趣和不感兴趣的方向）
- `## 代表性高分论文` — 用户评价高的论文描述，作为兴趣画像的补充
- `## Followed Authors` — 关注的作者列表
- `## Arxiv Categories` — 分类列表
- `## 兴趣权重` — 阅读行为积累的主题词权重（辅助排序用）

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

### Step 3: 语义筛选与排序

读取 CSV 文件，结合用户的研究兴趣进行**语义匹配**筛选排序（非关键词硬匹配）：

**匹配策略**（按优先级排列）：
1. **语义相关性判断**：将每篇论文的标题与 `## 研究方向描述` 中的自然语言段落做语义匹配。由 Claude 直接判断相关度（高/中/低/不相关），而非字符串匹配。重点理解描述中的细微语义（如"对 video+3DGS 感兴趣但对纯静态 3DGS 不感兴趣"）
2. **高分论文类比**：将候选论文与 `## 代表性高分论文` 中的描述做相似性比较——如果候选论文与某篇高分论文解决类似问题、使用类似方法或属于同一研究脉络，提升排名
3. **排除条件降权**：研究方向描述中标注"不感兴趣"的方向做**降权**（非硬过滤），避免误杀与感兴趣方向交叉的边界论文
4. **关注作者加权**：`## Followed Authors` 中的作者出现在论文作者列表时，额外加分
5. **兴趣权重微调**：`## 兴趣权重` 中的主题词权重作为辅助信号，对语义匹配的候选做二次排序微调

**已有论文检查**：在筛选过程中，检查 `library/tmp/` 和 `library/papers/` 目录，对候选论文中已存在于本地的标注状态：
- 已在 `library/papers/` 中的标注 `[已收藏]`
- 已在 `library/tmp/` 中且有 `analysis.md` 的标注 `[已分析]`
- 已在 `library/tmp/` 中仅有 `meta.md` 的标注 `[已记录]`

**输出**：
1. **精选 Top Picks**: 选出 3-5 篇最值得关注的论文
2. **推荐阅读**: 再选 5-10 篇次要推荐
3. 关注作者的论文在输出中标注 `[关注作者]`
4. 已有论文附带上述状态标注

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

### Step 5: 创建 paper stubs（精选自动 + 推荐交互选择）

`{method_slug}` 从论文标题/摘要中提炼出核心方法的简短英文标识（规则同 read-paper skill）。

meta.md 正文必须包含三段（格式同 CLAUDE.md 中的 meta.md 规范）：
1. **概要总结** — 中文 2-3 句话概括核心问题、方法和贡献
2. **Abstract** — 英文原文
3. **摘要翻译** — Abstract 的中文翻译

如果 Step 3.5 的 alphaxiv detail 返回了该论文的摘要，直接使用；否则从 CSV 中已有信息或标题推断生成概要总结即可（Abstract 和翻译可标注"待补充"）。

#### 阶段 A：精选论文自动保存

为精选 Top Picks（3-5 篇）自动创建 `library/tmp/{id}-{method_slug}/meta.md` stub（status: meta_only）。无需用户确认。

**去重**：创建前检查 `library/tmp/` 和 `library/papers/` 是否已有同名目录。如果已存在，跳过创建，不覆盖已有内容。

#### 阶段 B：推荐论文交互选择

将"推荐阅读"中的论文分批展示，每批最多 4 篇，让用户选择性保存：

1. 每批使用 `AskUserQuestion`（`multiSelect: true`），格式：
   - 每个选项的 **label** 为论文核心方法/关键词简称（如 "DeltaWorld"、"SphericalSteering"）
   - 每个选项的 **description** 为 2-3 句中文详细描述，包括：论文解决什么问题、提出了什么方法、关键技术亮点或实验结论（如"针对扩散模型推理时行为引导的表示坍缩问题，提出用超球面测地线旋转替代激活加法，保范旋转避免特征退化，配合 vMF 置信度门控实现自适应干预强度"）
   - 最后一个选项固定为 **"跳过 / 结束选择"**（description: "不再选择更多推荐论文"）
2. 用户可多选感兴趣的论文，也可选"跳过"进入下一批或结束
3. 如果用户选择了"跳过 / 结束选择"，停止后续批次，不再询问
4. 仅为用户选中的论文创建 `library/tmp/{id}-{slug}/meta.md` stub

### Step 5b: 更新 Library 索引

创建 paper stubs 后，运行索引生成脚本刷新 `library/README.md`：

```bash
python3 .claude/skills/manage-library/generate_index.py
```

### Step 6: 输出摘要与后续操作

向用户展示今日精选推荐的简要列表，并告知完整推荐已保存到哪个文件。列出所有已保存到 `library/tmp/` 的论文（精选 + 用户选中的推荐论文）。

展示完成后，使用 AskUserQuestion 询问：

> 是否有想要深入阅读的论文？

选项：
- **深度分析某篇**：用户指定论文编号，按 `/read-paper --detailed` 的流程进行深度分析（读取 `template-detailed.md` 模板）
- **快速浏览某篇**：用户指定论文编号，按 `/read-paper --brief` 的流程进行快速概览（读取 `template-brief.md` 模板）
- **暂不深入**：结束本次推荐

如果用户选择深入阅读，对应论文已有 `library/tmp/` 下的 stub，直接在此基础上补充 analysis.md。分析完成后回到此步，继续询问是否还要阅读其他论文。
