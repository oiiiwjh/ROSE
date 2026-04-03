# ROSE Roadmap

> 科研探索系统的功能规划与演进路线。随时在「想法收集」中添加新灵感。

## v1.0 — 基础分析与存储 ✅

核心的论文阅读、推荐、调研、管理功能。

- [x] `/read-paper` 单篇论文深度分析（支持 --repo、--prompt、--detailed/--brief、--supplement、Q&A 追问）
- [x] `/daily-papers` 每日论文推荐（兴趣筛选、批量抓取、推荐后可选深度/快速阅读）
- [x] `/survey-topic` 研究方向快速综述
- [x] `/analyze-code` 代码仓库分析与论文交叉引用
- [x] `/manage-library` 本地论文库管理（统计、搜索、列表、标签）
- [x] `/session-digest` 会话总结归档
- [x] `/setup` 首次使用引导
- [x] `/publish` 公共版本发布
- [x] `library/` 本地存储体系（papers/tmp/topics/daily）
- [x] meta.md 三段式格式（概要总结 + Abstract + 摘要翻译）
- [x] tmp → papers 收藏确认机制
- [x] 分析深度选择（深度分析 / 快速概览），模板外置为独立文件

---

## v1.5 — 体验打磨与智能推荐 🔜

### 短期体验打磨

#### 1. 分析模板迭代（优先级：高）

**目标**：根据实际输出效果调整 `template-detailed.md` 和 `template-brief.md` 的粒度和侧重点。

**方案**：
- 在实际使用中收集不满意的分析输出，针对性调整模板结构
- 每个 skill 目录下可加 `examples/` 放示例输入输出，作为 few-shot 参考
- 每个 skill 目录下可加 `templates/` 支持用户自定义分析模板

**涉及文件**：`read-paper` skill 下的模板文件

#### 2. PDF 本地读取（优先级：高）

**目标**：`arxiv_fetch.py` 目前只拿到 abstract，PDF 全文分析依赖 AlphaXiv/WebSearch 补充。加入 PDF 下载 + 本地读取能力。

**方案**：
- 在 `arxiv_fetch.py` 中新增 `--download` 参数，下载 PDF 到论文目录（`source.pdf`）
- `/read-paper` 流程中，当 AlphaXiv 返回 404 时自动下载 PDF 并直接读取
- 本地 PDF 路径的论文直接读取，不再依赖外部服务

**涉及文件**：`arxiv_fetch.py`、`read-paper` skill

#### 3. 行为增强 interests（优先级：高）✅

**目标**：分析/深读论文后自动更新 `interests.md` 中关键词的权重。

**方案**：
- `/read-paper` 分析完成时实时更新关键词权重（+1），收藏时额外 +1
- `/session-digest` 做校验和补漏
- 在 `interests.md` 新增 `## Keyword Weights` 段，格式如 `diffusion: 12`（累计计数）
- `/daily-papers` 筛选时读取权重进行加权排序

**涉及文件**：`interests.md`、`read-paper` skill、`session-digest` skill、`daily-papers` skill

### 智能推荐与反馈闭环

#### 4. 论文态度评分 + 作者/机构关注（优先级：高）✅

**目标**：看完论文后给评分，同时更新作者/机构关注度。

**方案**：
- 在 `/read-paper` 的输出摘要和收藏确认步骤中，增加 1-5 评分（AskUserQuestion）
- 评分写入 `meta.md` frontmatter（`rating: 4`）
- 在 `/manage-library` 中新增操作：
  - `--authors` — 查看关注的作者列表及统计
  - `--rate <paper_id> <score>` — 补充/修改论文评分
- 评分 ≥4 的论文作者自动加入 `interests.md` 的 `## Followed Authors`
- `/daily-papers` 排序时对关注作者论文加权，并标注 `[关注作者]`

**涉及文件**：`read-paper` skill、`manage-library` skill、`daily-papers` skill、`interests.md`

#### 5. Explore-Exploit 平衡（优先级：中）

**目标**：每日推荐中平衡"兴趣相关"和"跨领域探索"。

**方案**：
- `/daily-papers` 筛选时，在精选推荐中固定留出 1 个"探索槽位"
- 探索槽位选择标准：与用户主要领域不直接重叠，但在 arxiv 当日高影响力的论文
- 用户的态度评分也会影响探索比例——如果用户经常给探索推荐高分，逐渐增加探索槽位

**涉及文件**：`daily-papers` skill

---

## v2.0 — 能力扩展与外部集成 📋

### 论文关联与对比

#### 论文间关联图谱
- 构建论文间的引用关系、同作者、同方向关联
- 可视化展示已读论文的知识网络
- 推荐时利用图谱信息（如"你读过的 A 被 B 引用了"）

#### `/compare-papers` — 论文对比分析
- 新增 skill：对比两篇论文的方法差异
- 输入两个论文 ID，生成结构化的方法对比（架构差异、实验对比、各自优劣）
- 可集成到 `/survey-topic` 中，对核心论文自动两两对比

#### survey-topic 关联增强
- `/survey-topic` 生成的 `paper_list` 与 `library/` 中已有论文自动关联
- 标注哪些论文已读/已收藏，避免重复推荐
- 综述中引用已有分析的结论

### 外部数据集成

#### Semantic Scholar API
- 接入 `api.semanticscholar.org` 获取引用量、作者 h-index、最新论文
- `/daily-papers` 结合引用量信号做更好的排序
- 关注作者有新论文时主动通知
- 基于"你关注的作者引用了谁"做二度推荐

#### 知识复习（艾宾浩斯遗忘曲线）
- 记录每篇论文的阅读时间点和复习时间点
- 按遗忘曲线（1天/3天/7天/14天/30天）生成复习提问
- 新会话开始时自动检查是否有待复习论文
- **前置条件**：需要积累一定量的已分析论文（建议 20+ 篇后开启）

#### Notion 集成
- 通过 Notion API 将 meta.md + analysis.md 同步到 Notion 数据库
- 支持选择性同步（仅收藏的、评分 ≥ N 的）
- 作为导出渠道，与核心分析功能解耦

#### Twitter/XHS 等 Media 内容整理
- 爬取/订阅科研相关 Twitter 账号、小红书技术博主
- 提取其中提到的论文、观点、讨论
- 与已有论文库交叉引用

### 结构演进

#### shared/ 共用工具目录
- 新增 `.claude/skills/shared/` 目录放跨 skill 共用的工具
- `arxiv_fetch.py` 被 read-paper 和 survey-topic 都引用，应迁入 shared/
- 共用的模板片段、常量定义等

#### Plugins 化
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
- [2026-04-03] 分析模板根据实际输出效果迭代，支持 examples/ 和自定义 templates/
- [2026-04-03] PDF 下载+本地读取，减少对外部服务依赖
- [2026-04-03] 论文间关联图谱（引用关系、同作者、同方向）
- [2026-04-03] /compare-papers skill：对比两篇论文的方法差异
- [2026-04-03] daily-papers 结合 Semantic Scholar API 补充引用量排序
- [2026-04-03] survey-topic 与 library 已有论文自动关联
- [2026-04-03] shared/ 目录放跨 skill 共用工具（如 arxiv_fetch.py）
- [2026-04-03] 爬取或涉及到论文相关信息搜集，可以后续添加X/xhs等难直接爬取到平台。
- [2026-04-03] 支持用户添加自己喜欢的X博主等，可以参考https://github.com/freemty/yuanbo-skills/tree/main/no-more-fomo中推送关注消息的功能。
- https://github.com/VisionXLab/CitationClaw计划添加引用量
