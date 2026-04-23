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
- `## Followed Blogs` — 固定关注的博客源列表

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

### Step 3: 两阶段筛选

从 CSV 全量论文中分两阶段筛选，确保覆盖面和精度的平衡。

#### 阶段 A：宽松关键词预筛（目标：保留 40-60 篇）

用**宽松的**关键词列表对标题做初筛，目标是**大范围保留**而非精确匹配。关键词应覆盖：
- 用户兴趣方向的核心词和泛化词（如 video、diffusion、3D、generation、world model 等）
- 方法类通用词（如 attention、transformer、flow、reconstruction、editing 等）
- 应用场景词（如 robot、navigation、embodied、interactive、streaming 等）

**关键原则**：宁多勿少。这一步只是粗过滤，把明显无关的论文（如纯医学影像、遥感、NLP 文本分类等）排除。保留 40-60 篇候选进入下一阶段。如果关键词筛选后不足 40 篇，放宽关键词重新筛选。

同时标注关注作者：检查每篇候选论文的作者列表是否包含 `## Followed Authors` 中的作者，如命中则标注 `[关注作者]`。

#### 阶段 B：LLM 语义深度分析（核心判断）

将阶段 A 的 40-60 篇候选论文的**标题 + abstract**（CSV 中的 abstract 字段，如无则仅用标题）整体提交给 Claude 进行语义分析。

**分析输入**：
- 候选论文列表（标题 + abstract）
- `## 研究方向描述`（含不感兴趣的方向）
- `## 代表性高分论文`（兴趣画像）
- `## 兴趣权重`（辅助信号）

**分析维度**（Claude 综合判断，非机械打分）：

1. **直接相关**：论文主题与研究方向描述直接匹配（如视频生成、相机控制、世界模型等）
2. **方法启发**：论文提出的方法/技术可能迁移到用户感兴趣的方向（如 LLM 中的 speculative decoding → 视频生成加速，图像编辑先验 → 视频编辑）
3. **趋势信号**：论文代表某个新兴方向或跨领域融合趋势，即使不在用户明确兴趣范围内也值得关注（如新的表示方法、新的训练范式、新的评估协议）
4. **高分论文脉络**：与代表性高分论文解决类似问题、使用类似方法或属于同一研究脉络
5. **降权但不排除**：对"不感兴趣"的方向做降权，但如果论文与感兴趣方向有交叉，仍保留

**输出分类**：
- **精选 Top Picks**（3-5 篇）：直接相关度最高 + 方法创新性强
- **推荐阅读**（8-12 篇）：中高相关度，或有方法启发价值
- **边缘关注**（5-10 篇）：弱相关但有趋势价值或跨领域启发

**已有论文检查**：在筛选过程中，检查 `library/tmp/` 和 `library/papers/` 目录，对候选论文中已存在于本地的标注状态：
- 已在 `library/papers/` 中的标注 `[已收藏]`
- 已在 `library/tmp/` 中且有 `analysis.md` 的标注 `[已分析]`
- 已在 `library/tmp/` 中仅有 `meta.md` 的标注 `[已记录]`

**输出格式要求**：
1. 精选和推荐论文的推荐理由要说明**为什么这篇论文与用户兴趣相关**，或**什么方法/思路可以迁移到用户的研究方向**
2. 关注作者的论文标注 `[关注作者]`
3. 已有论文附带状态标注

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

> 基于 interests.md 从 {categories} 中筛选，共扫描 {N} 篇论文，预筛 {M} 篇候选

## 精选推荐

### 1. [{论文标题}]({arxiv_url})
**作者**: ... | **分类**: cs.CV
> 推荐理由：...
>
> 摘要：（简要中文翻译）

### 2. ...

## 推荐阅读

### 1. [{论文标题}]({arxiv_url})
**作者**: ... | **分类**: cs.CV
> 推荐理由：...
>
> 摘要：（简要中文翻译）

## 边缘关注

- [{标题}]({url}) — 一句话描述（标注为什么可能有启发价值）
- ...

## 完整候选列表

| # | 标题 | 分类 | 相关度 | 类别 |
|---|------|------|--------|------|
| 1 | ... | ... | ★★★ | 精选 |
| 2 | ... | ... | ★★☆ | 推荐 |
| 3 | ... | ... | ★☆☆ | 边缘 |
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

> 是否将部分论文加入阅读列表？

选项（multiSelect: true）：
- 列出本次保存到 tmp/ 的所有论文（label 为论文简称，description 为一句话概述）
- 最后一个选项固定为 **"跳过"**（description: "不加入阅读列表"）

如果用户选择了论文，再用 AskUserQuestion 询问优先级：
- 🔴 高优先级
- 🟡 中优先级
- ⚪ 低优先级

将选中的论文按优先级追加到 `library/reading_list.md` 表格中（同一优先级内按收集日期升序排列）。

然后使用 AskUserQuestion 询问：

> 是否有想要现在深入阅读的论文？

选项：
- **深度分析某篇**：用户指定论文编号，按 `/read-paper --detailed` 的流程进行深度分析（读取 `template-detailed.md` 模板）
- **快速浏览某篇**：用户指定论文编号，按 `/read-paper --brief` 的流程进行快速概览（读取 `template-brief.md` 模板）
- **暂不深入**：结束本次推荐

如果用户选择深入阅读，对应论文已有 `library/tmp/` 下的 stub，直接在此基础上补充 analysis.md。分析完成后回到此步，继续询问是否还要阅读其他论文。

### Step 6a: 近期论文趋势报告

在推荐输出完成后，基于本次扫描的全部论文（CSV 中所有数据），生成一份简要的趋势分析报告，追加到 `library/daily/{YYYY-MM-DD}.md` 末尾。

**分析流程**：
1. 读取 `library/daily/{YYYY-MM-DD}_raw.csv` 中的全部论文
2. 结合 `library/interests.md` 中的研究方向和关注作者
3. 按主题对论文进行聚类，统计各方向论文数量
4. 识别趋势和新兴方向
5. 分析与用户兴趣的交叉情况

**追加到每日推荐文件的格式**：

```markdown
## 近期趋势报告

### 热点方向
| 方向 | 论文数 | 代表论文 |
|------|--------|----------|
| ... | ... | ... |

### 趋势观察
- ...（2-3 个观察到的趋势或新兴方向，如"本周出现多篇将 X 应用于 Y 的工作"）

### 兴趣交叉分析
- ...（哪些用户感兴趣的方向今天活跃、哪些沉寂）

### 关注作者动态
- ...（如果关注的作者今天有新论文，单独列出；否则注明"今日无关注作者新论文"）
```

### Step 6a-img: 精选论文图片获取（可选）

对精选 Top Picks 论文，尝试从 arxiv PDF 中提取关键图片描述，追加到每日推荐文件中。

**流程**：
1. 对每篇精选论文，使用 `python3 .claude/skills/read-paper/arxiv_fetch.py --download <arxiv_id>` 下载 PDF 到 `library/tmp/{id}-{slug}/source.pdf`（如果 PDF 还不存在）
2. 使用 Read 工具读取 PDF 文件（Claude 支持读取 PDF 并查看图片）
3. 从 PDF 中识别最具代表性的 1-2 张图片（通常是 Figure 1 方法概览图或效果对比图）
4. 用一句话描述每张图的内容，记录页码和图号
5. 在每日推荐文件的对应精选论文条目下追加图片描述：
   ```markdown
   > 📊 **关键图示**：
   > - Fig.1 (p.2): 方法整体架构图 — [描述核心流程]
   > - Fig.5 (p.7): 效果对比 — [描述关键结论]
   > 
   > 📎 PDF: `library/tmp/{id}-{slug}/source.pdf`
   ```

**注意**：
- 这一步是**可选的**，如果 PDF 下载失败或不可用则跳过该论文
- 不需要实际提取图片文件（避免依赖外部库），只需描述图片内容和位置
- 只对精选 Top Picks 执行，不对推荐论文执行（控制 PDF 下载量）

### Step 6b: 博客源检查（如有 Followed Blogs）

如果 `library/interests.md` 中存在 `## Followed Blogs` 段且其中有配置的博客源：

1. **读取博客源列表**：解析 `## Followed Blogs` 中的所有条目
2. **逐源检查新内容**：
   - 对每个博客源，WebFetch 抓取其 `url + check_path` 页面
   - 解析页面中的文章列表，提取文章标题和链接
   - 与 `last_checked` 日期对比，筛选出该日期之后发布的新文章
3. **兴趣筛选**：
   - 对每篇新文章，用 WebFetch 抓取其内容（或摘要）
   - 根据 `## 研究方向描述` 语义判断是否与用户兴趣相关
   - 仅保留相关的新文章
4. **追加到每日推荐**：
   - 在 `library/daily/{YYYY-MM-DD}.md` 的推荐列表末尾增加博客推荐段：
     ```markdown
     ## 博客推荐

     ### [{文章标题}]({文章URL})
     **来源**: {站点名} | **发布日期**: {date}
     > 推荐理由：{一句话说明为什么与用户兴趣相关}
     >
     > 摘要：（简要中文概括核心内容）
     ```
   - 每篇新文章标注 `[Blog: {站点名}]`
5. **创建 blog stub**：
   - 对通过筛选的博客文章，在 `library/tmp/` 中创建 `{YYYYMMDD}-{slug}/meta.md` stub
   - meta.md 格式同 read-paper 的 blog 分支（content_type: blog, source_site 等）
   - status: meta_only
6. **更新 last_checked**：
   - 将所有已检查的博客源的 `last_checked` 更新为当天日期

如果没有 Followed Blogs 或列表为空，跳过此步骤。
