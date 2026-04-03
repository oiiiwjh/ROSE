# ROSE Roadmap

> 科研探索系统的功能规划与演进路线。随时在「想法收集」中添加新灵感。

## v1.0 — 基础分析与存储 ✅

核心的论文阅读、推荐、调研、管理功能。

- [x] `/read-paper` 单篇论文深度分析（支持 --repo、--prompt、Q&A 追问）
- [x] `/daily-papers` 每日论文推荐（兴趣筛选、批量抓取）
- [x] `/survey-topic` 研究方向快速综述
- [x] `/analyze-code` 代码仓库分析与论文交叉引用
- [x] `/manage-library` 本地论文库管理（统计、搜索、列表、标签）
- [x] `/session-digest` 会话总结归档
- [x] `library/` 本地存储体系（papers/tmp/topics/daily）
- [x] meta.md 三段式格式（概要总结 + Abstract + 摘要翻译）
- [x] tmp → papers 收藏确认机制

---

## v1.5 — 智能推荐与反馈闭环 🔜

让系统根据用户行为变得越来越"懂你"。

### 1. 行为增强 interests（优先级：高）

**目标**：分析/深读论文后自动更新 `interests.md` 中关键词的权重。

**方案**：
- 在 `/session-digest` 中统计本次会话分析的论文标签
- 在 `interests.md` 新增 `## Keyword Weights` 段，格式如 `diffusion: 12`（累计计数）
- `/daily-papers` 筛选时读取权重进行加权排序
- 收藏到 papers/ 的论文贡献更高权重（+2），仅分析未收藏的贡献较低（+1）

**涉及文件**：`interests.md`、`session-digest` skill、`daily-papers` skill

### 2. 论文态度评分 + 作者/机构关注（优先级：高）

**目标**：看完论文后给评分，同时更新作者/机构关注度。

**方案**：
- 在 `/read-paper` 的收藏确认步骤中，增加 1-5 评分（AskUserQuestion）
- 评分写入 `meta.md` frontmatter（`rating: 4`）
- 在 `/manage-library` 中新增操作：
  - `--authors` — 查看关注的作者/机构列表及统计
  - `--rate <paper_id> <score>` — 补充/修改论文评分
- 在 `interests.md` 新增 `## Followed Authors` 和 `## Followed Institutions` 段
- 评分 ≥4 的论文作者自动加入关注列表（频次累计）

**关于作者智能推荐的建议**：
> 直接通过引用量/h-index 推荐作者确实不好做（需要 Semantic Scholar API 且数据不完全可靠）。建议分两步走：
> 1. **近期**（v1.5）：基于用户行为的被动积累——深读并高评分的论文作者自动进入关注列表，频次越高排名越靠前。不需要外部数据。
> 2. **远期**（v2.0）：引入 Semantic Scholar API（`api.semanticscholar.org`，免费且有作者信息），当关注列表中的作者发新论文时主动推送。也可以基于"你关注的作者引用了谁"做二度推荐。

**涉及文件**：`read-paper` skill、`manage-library` skill、`interests.md`

### 3. Explore-Exploit 平衡（优先级：中）

**目标**：每日推荐中平衡"兴趣相关"和"跨领域探索"。

**方案**：
- `/daily-papers` 筛选时，在精选推荐中固定留出 1 个"探索槽位"
- 探索槽位选择标准：与用户主要领域不直接重叠，但在 arxiv 当日高影响力（多个分类交叉、评论数多）的论文
- 在推荐输出中用特殊标记（如 `🔭 探索推荐`）与常规推荐区分
- 用户的态度评分也会影响探索比例——如果用户经常给探索推荐高分，逐渐增加探索槽位

**涉及文件**：`daily-papers` skill

---

## v2.0 — 外部集成与高级功能 📋

### 知识复习（艾宾浩斯遗忘曲线）
- 记录每篇论文的阅读时间点和复习时间点
- 按遗忘曲线（1天/3天/7天/14天/30天）生成复习提问
- 新会话开始时自动检查是否有待复习论文
- **前置条件**：需要积累一定量的已分析论文（建议 20+ 篇后开启）

### Notion 集成
- 通过 Notion API 将 meta.md + analysis.md 同步到 Notion 数据库
- 支持选择性同步（仅收藏的、评分 ≥ N 的）
- 作为导出渠道，与核心分析功能解耦

### 作者智能推荐
- 接入 Semantic Scholar API 获取作者引用量、h-index、最新论文
- 基于用户关注作者的合作网络做二度推荐
- 关注作者有新论文时主动通知

### Twitter/XHS 等 Media 内容整理
- 爬取/订阅科研相关 Twitter 账号、小红书技术博主
- 提取其中提到的论文、观点、讨论
- 与已有论文库交叉引用

### 整理成 Plugins
- 将 ROSE 的 skills 抽象为通用的 Claude Code plugin 形态
- 支持其他用户一键安装使用

---

## 想法收集

> 在这里随时记录新灵感，后续整理到对应版本中。格式：`- [日期] 想法描述`

- [2026-04-02] 根据行为自动增强 interests 权重
- [2026-04-02] 维护作者/机构关注列表，推荐时加权
- [2026-04-02] 论文态度评分影响推荐
- [2026-04-02] 知识复习功能（艾宾浩斯遗忘曲线）
- [2026-04-02] 每日推荐中平衡 explore 和 exploit
- [2026-04-02] 作者推荐不应只给名字，应结合兴趣+论文质量+引用量

