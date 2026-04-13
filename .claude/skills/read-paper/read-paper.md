---
description: "论文阅读分析与 Q&A。支持 arxiv URL/ID 或本地 PDF，已分析过的论文可直接提问"
---

# 论文阅读分析

你是一个科研论文分析助手。根据论文状态自动选择模式：首次分析或基于已有分析的 Q&A。

**公式格式要求**：所有数学公式必须使用 LaTeX 语法，行内公式用 `$...$`，独立公式用 `$$...$$`，确保在 Markdown 渲染器中可正确显示。

## 输入解析

用户输入: $ARGUMENTS

请解析输入，识别：
1. **论文标识**：arxiv URL、arxiv ID（如 2401.12345）、alphaxiv URL（如 alphaxiv.org/overview/2401.12345）、本地 PDF 路径、或已有论文的关键词
2. **可选参数**：
   - `--repo <url>`: 关联的 GitHub 代码仓库
   - `--prompt <text>`: 自定义分析角度（替代默认模板）
   - `--detailed`: 直接使用深度分析模板（跳过选择）
   - `--brief`: 直接使用简略分析模板（跳过选择）
   - `--supplement <type:source>`: 补充信息源，可多次使用。类型包括：
     - `repo:https://github.com/...` — 代码仓库
     - `twitter:https://x.com/...` — Twitter/X 讨论
     - `blog:https://...` — 博客文章
     - `video:https://...` — 视频讲解
3. **追问内容**：论文标识之后的自然语言问题（如有）
4. **隐式补充**：在 Q&A 模式中，用户可以用自然语言补充信息源（如"补充这个 repo: ..."、"加上这个博客"），等价于 `--supplement`

## 模式判断

### Step 0: 本地库全局搜索（必须先执行）

在访问任何外部服务之前，先在本地 library 中全面搜索论文已有信息：

**搜索范围与优先级**（按顺序搜索，一旦命中即记录）：

1. **`library/papers/`**（已收藏论文）— 用 arxiv ID 前缀匹配目录名（如 `2401-12345*`）
2. **`library/tmp/`**（临时论文）— 同上匹配规则
3. **`library/daily/*.md`**（每日推荐记录）— 在所有日报中搜索该 arxiv ID 或论文标题关键词，提取已有的推荐理由、标签等信息
4. **`library/topics/*/paper_list.md`**（专题论文列表）— 搜索该论文是否已被某个研究专题收录

如果 arxiv ID 未命中，尝试用论文标题关键词在所有 `meta.md` 的 title 字段中模糊匹配。

**搜索方式**：使用 Glob + Grep 工具组合搜索，不要用 Bash 命令。例如：
- `Glob: library/papers/2401-12345*` 和 `Glob: library/tmp/2401-12345*` 匹配目录
- `Grep: pattern="2401.12345" path="library/daily/"` 搜索日报提及
- `Grep: pattern="2401.12345" path="library/topics/"` 搜索专题提及

### Step 0b: 完整性检查

如果在 papers/ 或 tmp/ 中找到了论文目录，检查以下文件的存在情况：

| 文件 | 状态含义 |
|------|---------|
| `meta.md` | 基础元信息（标题、作者、摘要） |
| `analysis.md` | 已完成分析 |
| `qa.md` | 有过 Q&A 记录（精简摘要版） |
| `qa/` | 分主题的详细 Q&A 记录 |
| `source.pdf` | 已下载 PDF |
| `sources.md` | 搜索信息源记录 |
| `notes.md` | 有个人笔记 |
| `alphaxiv-overview.md` | AlphaXiv 结构化分析报告 |
| `alphaxiv-abs.md` | AlphaXiv 论文全文 markdown |

向用户展示搜索结果摘要，例如：
```
📎 本地已有记录：
  - library/papers/2401-12345-nerf/
    ✓ meta.md  ✓ analysis.md  ✓ qa.md  ✓ qa/ (3 topics)  ✗ source.pdf
  - 出现在 daily/2026-04-02.md 推荐列表中（标签: nerf, 3dgs）
```

### Step 0c: 模式路由

根据搜索结果和用户意图，选择模式：

| 本地状态 | 用户输入 | 模式 |
|---------|---------|------|
| 有 analysis.md + 用户带了问题 | 问题/追问 | → **Q&A 模式** |
| 有 analysis.md + 无问题 | 仅论文标识 | → 展示已有分析摘要，询问是否要重新分析、追问、或补充信息 |
| 有 meta.md 但无 analysis.md | 任意 | → **分析模式**（跳过 Step 1-3 的元信息获取，直接从 Step 4 选择分析深度开始） |
| 仅在 daily/topics 中出现 | 任意 | → **分析模式**（从 Step 1 开始，但将 daily/topics 中的已有信息作为初始上下文） |
| 完全未找到 | 任意 | → **分析模式**（从 Step 1 开始，正常流程） |

---

## 分析模式

### Step 1: 获取论文信息

> **注意**：如果 Step 0 已找到本地 meta.md，则跳过本步骤的元信息获取部分，直接复用本地数据。仅在信息不完整时（如缺少 abstract、authors）才补充获取。

**本地优先策略**：
1. 如果本地已有 `meta.md`：读取并检查字段完整性（title、authors、date、arxiv_id、abstract）
2. 如果本地已有 `source.pdf`：直接读取 PDF，不重新下载
3. 如果 daily/ 或 topics/ 中有该论文的推荐信息：提取标签、推荐理由作为分析的初始上下文

**仅当本地信息不足时，按以下优先级获取外部信息：**

**信息获取优先级链**（按顺序尝试，前一步成功则跳过后续）：

1. **AlphaXiv（首选，针对 arxiv 论文）**：
   - 提取论文 ID（从 arxiv URL、alphaxiv URL 或原始 ID 中解析）
   - 获取 AI 结构化分析报告：`curl -s "https://alphaxiv.org/overview/{PAPER_ID}.md"`
   - 如果报告不够详细或需要具体公式/表格，获取论文全文：`curl -s "https://alphaxiv.org/abs/{PAPER_ID}.md"`
   - AlphaXiv 通常能提供最完整的结构化内容，优先使用
   - **保存原始 markdown**：将成功获取的 AlphaXiv 内容保存到论文目录（Step 2 创建目录后执行）：
     - overview 内容 → `{论文目录}/alphaxiv-overview.md`
     - abs 全文内容 → `{论文目录}/alphaxiv-abs.md`
     - 如果论文目录已存在对应文件，覆盖更新

2. **arxiv_fetch.py（AlphaXiv 返回 404 或超时时）**：
   - 运行 `python3 .claude/skills/read-paper/arxiv_fetch.py --id <id>` 获取元信息（标题、作者、摘要）
   - 此步仅获取元信息，不含全文分析

3. **WebSearch（补充上下文）**：
   - 搜索论文标题，获取相关博客、讨论、代码仓库等补充信息
   - 无论前两步是否成功，都建议执行此步以丰富 sources.md

4. **PDF 下载（AlphaXiv 全文不可用时的最终回退）**：
   - 当 AlphaXiv 无法获取论文全文，且分析需要具体公式/表格时，下载 PDF 本地阅读

**PDF 下载（深度分析时自动执行）：**

在创建论文目录后（Step 2），下载 PDF 到论文目录供本地阅读和分析参考：

```bash
python3 .claude/skills/read-paper/arxiv_fetch.py --id <id> --download library/tmp/{dir}/source.pdf
```

下载的 PDF 可直接用 Read 工具读取，补充 AlphaXiv 未覆盖的细节（公式、图表、附录等）。

**本地 PDF：**

- 直接读取 PDF 文件，跳过下载步骤

### Step 1b: 记录信息源（sources.md）

在通过 WebSearch 或其他方式获取到外部信息后，将发现的所有信息源记录到论文目录下的 `sources.md`。

**自动记录**：WebSearch 返回的每个结果自动按类别分类记录，包括 URL 和一句话描述。

**分类规则**：
- **论文相关 (Paper)**：arxiv 页面、AlphaXiv 分析、项目主页、会议页面
- **代码相关 (Code)**：GitHub/GitLab 仓库、代码教程、Colab notebook
- **社区讨论 (Discussion)**：Reddit、Twitter/X、小红书、博客、论坛帖子、视频讲解

**用户确认**：记录完成后，使用 AskUserQuestion 展示发现的信息源列表，询问用户是否需要对某些来源进行深入抓取和分析（multiSelect）。对用户选择的来源执行 WebFetch 获取详细内容，并整合到 analysis.md 中。

**格式**：
```markdown
# Sources

> 最后更新: {YYYY-MM-DD}

## 论文相关 (Paper)
- [显示名](URL) — 一句话描述

## 代码相关 (Code)
- [显示名](URL) — 一句话描述

## 社区讨论 (Discussion)
- [显示名](URL) — 一句话描述
```

如果论文目录下已有 `sources.md`，追加新发现的来源（去重）而非覆盖。

在 Q&A 模式中，如果用户补充新的信息源（`--supplement` 或自然语言），也同步更新 `sources.md`。

### Step 2: 创建论文目录

> **注意**：如果 Step 0 已找到本地目录（papers/ 或 tmp/），跳过此步骤。

- 目录路径: `library/tmp/{arxiv_id}-{method_slug}/`（所有论文先进 tmp）
  - arxiv ID 中的 `.` 替换为 `-`（如 `2401.12345` → `2401-12345`）
  - `{method_slug}` 是论文核心方法/模型的简短英文标识，用小写字母和连字符：
    - 如果论文明确提出了一个方法名/模型名/数据集名/框架名（如 "NeRF"、"CLIP"、"DreamBooth"），直接使用该名称的 slug（如 `nerf`、`clip`、`dreambooth`）
    - 如果没有明确名称，从标题和核心贡献中凝练一个简短描述性 slug（如 `adaptive-token-pruning`、`multi-scale-diffusion`）
    - slug 长度控制在 2-5 个词以内
  - 完整示例: `2401-12345-nerf`、`2503-08017-adaptive-token-pruning`
- 如果是本地 PDF 且无 arxiv ID，使用 `{title_slug}-{method_slug}` 作为目录名

### Step 2b: 更新 Library 索引

创建论文目录后，运行索引生成脚本刷新 `library/README.md`：

```bash
python3 .claude/skills/manage-library/generate_index.py
```

### Step 3: 生成 meta.md

> **注意**：如果本地已有 `meta.md`，检查字段完整性。仅补充缺失字段（如 tags、repo），不覆盖已有内容。如果所有字段完整，跳过此步骤。

使用以下格式创建 `meta.md`（frontmatter + 正文三段）:

```markdown
---
title: "论文标题"
authors: ["作者1", "作者2"]
date: "发表日期"
arxiv_id: "2401.12345"
url: "https://arxiv.org/abs/2401.12345"
tags: [相关标签]
status: analyzed
repo: "https://github.com/author/repo"  # 可选，关联代码仓库
supplements: ["twitter:https://...", "blog:https://..."]  # 可选，补充信息源
---

## 概要总结

（用中文 2-3 句话概括论文的核心问题、方法和贡献，帮助快速判断是否值得深读）

## Abstract

（原文 Abstract，保持英文原文不动）

## 摘要翻译

（Abstract 的中文翻译，忠实原文但表述流畅）
```

### Step 4: 选择分析深度

如果用户已通过 `--detailed` 或 `--brief` 指定，跳过此步。否则，使用 AskUserQuestion 询问用户：

> 选择分析深度？

选项：
- **深度分析**：详细拆解方法、公式、实验，适合需要精读的论文（参考 `template-detailed.md`）
- **快速概览**：核心信息速览，800-1200 字，适合初筛或泛读（参考 `template-brief.md`）

### Step 5: 生成 analysis.md

根据用户选择的分析深度：

1. **如果用户提供了 `--prompt`**：按用户的自定义角度分析
2. **深度分析**：读取 `.claude/skills/read-paper/template-detailed.md` 作为分析模板，严格按照其结构和要求生成 analysis.md
3. **快速概览**：读取 `.claude/skills/read-paper/template-brief.md` 作为分析模板，严格按照其结构和要求生成 analysis.md

**如果有 `--repo`**：在深度分析模板中，务必填充「代码实现分析」章节。在快速概览模板中，追加简要的代码结构说明。

### Step 6: 代码分析（使用深度分析 + `--repo` 时）

如果用户提供了 `--repo`（或通过 `--supplement repo:...` 补充），且选择了深度分析：

1. **获取代码**：
   - 本地路径：直接读取目录结构和关键文件
   - GitHub URL：用 WebSearch 浏览仓库结构、README、核心代码文件

2. **全局扫描**：
   - 识别入口点、目录结构、核心模块、依赖
   - 阅读 README 了解用途和使用方式

3. **逐模块分析**：
   - 每个核心模块的功能和在 pipeline 中的角色
   - 数据流和 tensor shape 变换过程
   - 论文未提及但代码中存在的工程细节

4. **论文-代码对应表**：建立论文章节/公式与代码位置的映射

5. **差异标注**：论文描述 vs 代码实现的差异

### Step 6b: 库存论文关联分析

分析完成后，自动扫描本地论文库，发现当前论文与已有收藏的关联。如果库中论文数量为 0，跳过此步。

**扫描范围**：
1. 使用 Glob 列出 `library/papers/*/meta.md` 和 `library/tmp/*/meta.md` 的所有论文（排除当前论文自身）
2. 读取每篇论文 meta.md 的 frontmatter（仅 tags、authors、title、rating 字段），不读取正文
3. 读取 `library/interests.md` 的 `## Followed Authors` 段
4. 使用 Grep 在 `library/topics/*/paper_list.md` 中搜索当前论文的关键词或 arxiv ID

**关联判定规则**：

- **强关联**（至少满足一项）：
  - tags 交集 ≥ 2 个
  - 有共同作者
  - 当前论文 analysis.md 中明确提及库存论文的方法名或模型名
- **弱关联**（至少满足一项）：
  - tags 交集 = 1 个（且该 tag 不是过于泛化的标签如 `diffusion`、`deep-learning`、`transformer`）
  - 属于同一个 `topics/` 方向
- **作者关联**：当前论文作者出现在 Followed Authors 列表中

**输出格式**：

仅在有关联发现时输出，无关联时静默跳过。按强关联 → 弱关联 → 作者命中 → Topics 归属的顺序展示：

```
📎 与你的论文库的关联：

🔗 强关联（共享核心方法/同一研究组）：
  - [{论文标题}](library/papers/{dir}/) ⭐{rating} — 共同标签: {tag1, tag2} | {一句话说明方法异同}

🔗 弱关联（相关领域/互补方法）：
  - [{论文标题}](library/papers/{dir}/) ⭐{rating} — 共同标签: {tag} | {关联说明}

👤 关注作者命中：
  - {作者名} ({机构}) — 也是 {论文名} 的{角色}

📂 相关 Topics：
  - {topic_slug} — {本文可纳入该方向综述的理由}
```

**强关联论文的深度对比**：对判定为强关联的论文，额外读取其 `analysis.md` 的「核心思想与主要贡献」段（或「概要」段），用 1-2 句话说明两篇论文的方法异同或互补关系。

**性能考虑**：
- 仅读取 meta.md frontmatter（不读取完整 analysis.md），除非判定为强关联
- 如果库存论文数量 > 30，先按 tags 交集预筛选，再读取强关联论文详情

### Step 7: 输出摘要与评分

完成后，向用户展示：
- 论文标题和核心贡献的简要总结
- 创建的文件路径（在 library/tmp/ 中）
- 如果有值得深入讨论的点，主动提出建议

然后使用 AskUserQuestion 询问评分：

> 为这篇论文评分（1-5）？

选项：
- **★★★★★ (5)**：非常有价值，强烈推荐
- **★★★★ (4)**：很好，值得深入
- **★★★ (3)**：一般，有参考价值
- **跳过评分**：暂不评分

如果用户给出评分，写入 meta.md frontmatter：`rating: <score>`

### Step 8: 收藏确认（论文在 tmp 中时）

使用 AskUserQuestion 询问：

> 是否将这篇论文收藏到正式库（library/papers/）？

选项：
- **收藏**：将整个论文目录从 `library/tmp/` 移动到 `library/papers/`
- **暂不收藏**：保留在 `library/tmp/` 中，继续追问或后续通过 `/manage-library` 整理

### Step 8b: 更新 Library 索引

收藏操作完成后（无论是否收藏），运行索引生成脚本刷新 `library/README.md`：

```bash
python3 .claude/skills/manage-library/generate_index.py
```

### Step 9: 更新研究兴趣（interests.md）

分析完成后，自动更新 `library/interests.md`：

1. **兴趣权重**：读取论文 meta.md 的 `tags`，在 `## 兴趣权重` 段中为每个 tag 权重 +1。如果用户选择了收藏，则每个 tag 额外 +1（收藏比仅分析多 +1）。兴趣权重仅作为辅助排序信号，不作为筛选条件。
2. **代表性高分论文**（新增）：如果用户评分 ≥ 4，在 `## 代表性高分论文` 段追加一行，格式：`- [{arxiv_id}] 一句话描述论文核心贡献和用户可能感兴趣的点`。这些描述将被 daily-papers 用于语义类比匹配。
3. **关注作者**：如果用户评分 ≥ 4，将论文的所有作者加入 `## Followed Authors`。如果作者已存在，更新 count +1 和 last_paper；如果不存在，新增条目（count: 1）

### Step 10: 记录到每日日志（daily）

自动将本次分析追加到 `library/daily/{YYYY-MM-DD}.md`（当天日期）：

- 如果文件不存在，创建并添加标题 `# {YYYY-MM-DD} 每日记录`
- 如果文件已存在，追加到文件末尾
- 检查是否已有当前 Session 的 `## Session {HH:MM}` 段，有则追加到该段，无则新建

**追加格式**：
```markdown
### 论文相关
- 分析了 [{论文标题}]({arxiv_url})（{arxiv_id}）
  - 核心发现：{一句话总结核心贡献}
```

如果用户评了分，在行末标注（如 `⭐4`）；如果收藏了，标注"已收藏"。

---

## Q&A 模式

### Step 1: 加载上下文

定位论文目录（可能在 `library/papers/` 或 `library/tmp/` 中），读取以下文件作为回答依据：
- `meta.md` — 元信息和摘要
- `analysis.md` — 详细分析
- `qa.md` — 之前的 Q&A 摘要（如果存在）
- `qa/*.md` — 分主题的详细 Q&A 记录（如果 `qa/` 目录存在）。先扫描各文件的 frontmatter `description` 判断相关性，仅完整读取与当前问题相关的文件（`------` 分隔线以下的内容）；不相关的文件跳过
- `alphaxiv-overview.md` — AlphaXiv 结构化分析报告（如果存在）
- `alphaxiv-abs.md` — AlphaXiv 论文全文 markdown（如果存在）

如果论文目录下有本地 PDF，也读取作为补充上下文。
如果 meta.md 中有 arxiv_id 且已有信息不足以回答问题，优先读取本地 `alphaxiv-abs.md`；若不存在，通过 `curl -s "https://alphaxiv.org/abs/{PAPER_ID}.md"` 获取论文全文并保存为 `alphaxiv-abs.md`。

### Step 2: 处理补充信息源（如有）

如果用户输入包含 `--supplement`、`--repo`，或用自然语言要求补充信息源（如"补充 repo"、"加上这个代码仓库"、"分析一下这个实现"）：

**补充 repo（代码仓库）：**
1. 读取 `template-detailed.md` 中「代码实现分析」章节的要求
2. 执行完整的代码分析流程（同分析模式 Step 6）
3. 将代码分析内容追加到现有 analysis.md
4. 更新 meta.md frontmatter，添加 `repo: <url>`

**补充其他信息源（twitter/blog/video 等）：**
1. 获取补充信息源的内容（WebSearch 或直接访问）
2. 将相关信息整合到 analysis.md 中合适的章节（或新增 `## 补充资料` 章节）
3. 更新 meta.md frontmatter，在 `supplements` 列表中追加

补充完成后，继续回答用户的问题（如有）。

### Step 3: 回答问题

- 基于论文内容，用中文详细回答用户的问题
- 引用论文中的具体章节、公式或实验数据
- 如果问题超出论文范围，可以用 WebSearch 补充查找相关信息

### Step 4: 记录 Q&A

本步分两部分：写入详细主题文件（`qa/` 目录）和更新摘要文件（`qa.md`）。

#### Step 4a: 详细记录 → `qa/` 目录

1. **确保目录存在**：如果论文目录下不存在 `qa/` 子目录，创建它。

2. **主题分类**：根据当前问题的内容，判断它属于哪个主题类别。常见类别包括（但不限于）：
   - `model-architecture` — 模型结构、网络设计、模块组成
   - `training-strategy` — 训练方法、损失函数、优化策略
   - `experimental-results` — 实验结果、消融实验、对比分析
   - `theoretical-basis` — 理论基础、数学推导、证明
   - `implementation-details` — 实现细节、工程技巧、代码相关
   - `related-work` — 相关工作、对比方法、领域背景
   - `data-and-preprocessing` — 数据集、数据处理、评估指标
   - `application-and-extension` — 应用场景、扩展方向、局限性
   
   也可以根据论文特点自定义更具体的主题（如 `vae-equivariance`、`latent-space-manipulation`）。

3. **匹配已有文件（轻量扫描）**：列出 `qa/` 目录下已有的 `.md` 文件，**仅读取每个文件的 frontmatter**（`---` 之间的 `description` 字段）来判断当前问题是否属于某个已有主题。不需要读取文件全文：
   - description 与当前问题高度相关 → **追加到该文件**
   - 与所有已有文件的 description 都不匹配 → **创建新文件**
   - 如果横跨多个主题，选择最核心的那个

4. **文件命名**：`qa/{topic-slug}.md`，slug 为小写英文 + 连字符（2-5 词）

5. **文件格式**：

   每个主题文件采用 frontmatter + 分隔线 + 正文的结构。frontmatter 中的 `description` 用于快速匹配，`------`（6 个连字符）分隔线以下是实际 Q&A 内容。

   **新建主题文件时**：
   ```markdown
   ---
   topic: {topic-slug}
   paper: {arxiv_id}
   description: "{一句话描述该主题覆盖的问题范围，如：模型整体架构设计、各模块组成与连接方式}"
   ---

   # {主题中文名}

   ------

   ## {YYYY-MM-DD HH:MM}

   **Q**: {用户的完整问题}

   **A**: {详细回答，保留完整的推理过程、公式推导、实验数据引用}

   ---
   ```

   **追加到已有文件时**，在文件末尾追加新条目。如果新追加的问题扩展了主题范围，同时更新 frontmatter 中的 `description` 使其覆盖新内容：
   ```markdown
   ## {YYYY-MM-DD HH:MM}

   **Q**: {用户的完整问题}

   **A**: {详细回答}

   ---
   ```

6. **详细版要求**：
   - 保留回答中的所有公式推导，使用 LaTeX 记法（行内 `$...$`，独立 `$$...$$`）
   - 保留具体的数字、实验数据、表格引用
   - 保留对论文具体章节/图表的引用（如"见 Table 3"、"公式 (7)"）
   - 如果回答中涉及对比或列举，保留完整列表

#### Step 4b: 摘要记录 → `qa.md`

将本次 Q&A 的**精简版**追加到 `qa.md`。与详细版的区别：

- **Q**：保留问题原文（如果过长则缩写为一句话）
- **A**：将回答压缩为 2-4 句话的核心结论，省略推导过程和辅助细节。重点保留：最终结论、关键数字、核心洞察
- 末尾标注详细记录所在文件

格式：
```markdown
## {YYYY-MM-DD HH:MM}

**Q**: {问题}

**A**: {2-4 句精简回答}

→ 详见 `qa/{topic-slug}.md`

---
```

如果 `qa.md` 不存在，创建新文件，首行为 `# Q&A: {论文简称}`。

### Step 5: 后续建议

回答后，如果有相关的深入方向，可以建议：
- 相关的后续问题
- 可以对比阅读的其他论文
- 对应的代码实现细节

### Step 6: 评分与收藏（论文在 tmp 中时）

如果当前论文在 `library/tmp/` 中，在每次 Q&A 回答结束后：

**Step 6a: 评分**

使用 AskUserQuestion 询问：

> 为这篇论文评分（1-5）？

选项：
- **★★★★★ (5)**：非常有价值，强烈推荐
- **★★★★ (4)**：很好，值得深入
- **★★★ (3)**：一般，有参考价值
- **跳过评分**：暂不评分

如果用户给出评分，写入 meta.md frontmatter：`rating: <score>`

**Step 6b: 收藏确认**

使用 AskUserQuestion 询问：

> 是否将这篇论文收藏到正式库（library/papers/）？

选项：
- **收藏**：将整个论文目录从 `library/tmp/` 移动到 `library/papers/`
- **暂不收藏**：保留在 `library/tmp/` 中，继续追问或后续通过 `/manage-library` 整理

**Step 6c: 更新研究兴趣（interests.md）**

自动更新 `library/interests.md`：

1. **兴趣权重**：读取论文 meta.md 的 `tags`，在 `## 兴趣权重` 段中为每个 tag 权重 +1。如果用户选择了收藏，则每个 tag 额外 +1
2. **代表性高分论文**：如果用户评分 ≥ 4，在 `## 代表性高分论文` 段追加一行描述
3. **关注作者**：如果用户评分 ≥ 4，将论文的所有作者加入 `## Followed Authors`（更新 count 和 last_paper）

如果论文已在 `library/papers/` 中，跳过此步。
