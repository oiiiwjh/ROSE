# ROSE Roadmap

> 科研探索系统的功能规划与演进路线。随时在「想法收集」中添加新灵感。

## v1.0.0 — 基础分析与存储 ✅

核心的论文阅读、推荐、调研、管理功能。

- [x] `/read-paper` 单篇论文深度分析（支持 Q&A 追问）
- [x] `/daily-papers` 每日论文推荐（兴趣筛选、批量抓取）
- [x] `/survey-topic` 研究方向快速综述
- [x] `/analyze-code` 代码仓库分析与论文交叉引用
- [x] `/manage-library` 本地论文库管理（统计、搜索、列表、标签）
- [x] `/session-digest` 会话总结归档
- [x] `/setup` 首次使用引导
- [x] `library/` 本地存储体系（papers/tmp/topics/daily）
- [x] meta.md 三段式格式（概要总结 + Abstract + 摘要翻译）
- [x] tmp → papers 收藏确认机制

---

## v1.0.1 — 增量改进 ✅

在 v1.0.0 基础上的体验优化和功能增强。

- [x] 分析深度选择（深度分析 / 快速概览），模板外置为 `template-detailed.md` / `template-brief.md`
- [x] `--detailed` / `--brief` / `--supplement` / `--repo` / `--prompt` 参数支持
- [x] 行为增强 interests：分析/收藏时自动更新关键词权重（`## Keyword Weights`）
- [x] 论文评分（1-5）+ 评分 ≥4 自动关注作者（`## Followed Authors`）
- [x] `/manage-library --authors` 作者管理 + `--rate` 评分修改
- [x] `/daily-papers` 关注作者加权 + `[关注作者]` 标注
- [x] `/publish` 公共版本发布与增量更新
- [x] `/update` 系统文件远程更新检查
- [x] `/read-paper` 本地库优先搜索与完整性检查（Step 0）
- [x] 版本控制机制（CLAUDE.md 为版本权威来源）

---

## v1.0.2 — 信息源与语义匹配 ✅

在 v1.0.1 基础上的信息获取和匹配能力增强。

- [x] `sources.md` 信息源记录（WebSearch 结果按类别自动归档）
- [x] `interests.md` 从关键词匹配重构为语义描述 + 模糊匹配
- [x] `survey-topic` 种子论文模式（`--papers` 参数，定向搜索，深度对比表）
- [x] `/read-paper` Step 10 自动记录到每日日志
- [x] `/update` 数据格式迁移机制（schema_version）
- [x] 双语 README（EN + ZH）
- [x] `/publish` 增量更新自动化（远程同步 + commit + push）

---

## v1.0.3 — 交互增强与索引升级 ✅

在 v1.0.2 基础上的交互体验和数据管理增强。

- [x] `/daily-papers` 推荐论文交互式选择（精选自动保存 + 推荐分批 AskUserQuestion 多选）
- [x] `/daily-papers` 已有论文去重检查（创建 stub 前检查 tmp/papers 目录），状态标注（[已收藏]/[已分析]/[已记录]）
- [x] `/daily-papers` 推荐论文描述升级为 2-3 句详细描述
- [x] `library/README.md` 索引增强：新增发表日期、收集日期、来源 skill、一句话概述列
- [x] `generate_index.py` 新增 `extract_summary()` 从概要总结提取首句，`collected_date` 支持文件 mtime 回退
- [x] meta.md 规范新增 `source` 和 `collected_date` 字段
- [x] `/survey-topic --idea` 研究 idea 验证与规划（可行性分析、竞争论文对比、研究计划生成）
- [x] `/read-paper` AlphaXiv markdown 本地缓存（`alphaxiv-overview.md` / `alphaxiv-abs.md`）
- [x] `/read-paper` QA 分主题详细记录（`qa/` 子目录，frontmatter description 轻量扫描，`qa.md` 精简摘要）

---

## v1.0.4 — 库存关联与交叉引用 ✅

在 v1.0.3 基础上的论文间关联能力增强。

- [x] `/read-paper` Step 6b 库存论文关联分析：分析完成后自动扫描本地论文库，按 tags 重叠、共同作者、方法引用、Topics 归属四个维度检测关联，强关联论文额外对比方法异同

---

## v1.0.5 — Blog 支持与内容类型扩展 ✅

在 v1.0.4 基础上扩展支持博客、项目页面等非论文内容。

- [x] `/read-paper` 扩展支持 URL 输入（Blog 分支：WebFetch 抓取、元信息提取、关联论文检测）
- [x] `content_type` 字段：paper | blog | project-page | thread | newsletter
- [x] `library/blogs/` 收藏目录（blog 收藏至此，论文仍收至 papers/）
- [x] Blog 分析模板适配（实证与演示 + 关键 Insight 段）
- [x] `library/interests.md` 新增 `## Followed Blogs` 固定博客源配置
- [x] `/daily-papers` 增加博客源检查与推荐
- [x] `generate_index.py` 扫描范围增加 `library/blogs/`
- [x] `/manage-library` 搜索/统计/评分范围增加 blogs
- [x] Library 索引新增「阅读状态」列（待阅读/已分析/计划阅读/已精读）
- [x] `/read-paper` 分析后询问是否加入阅读列表（Step 8c）
- [x] `read-paper` Step 0 搜索范围补充 blogs/，URL 自动判断规则收紧

---

## v1.0.6 — Arxiv ID 验证与数据一致性 ✅

在 v1.0.5 基础上增强数据一致性保障。

- [x] `/read-paper` Step 0b-1 Arxiv ID 有效性验证：本地论文自动验证 ID 是否仍指向同一篇论文
- [x] 标题不匹配时自动触发修正流程（搜索正确 ID → 确认 → 更新 meta/目录名/sources/analysis/daily）
- [x] Step 1 的 `arxiv_fetch.py` 调用增加交叉验证逻辑

---

## v1.5 — 体验打磨与智能推荐 🔜

> 里程碑目标：完成后升级为 v1.1.0

### 体验打磨

#### 1. 分析模板迭代（优先级：高）

**目标**：根据实际输出效果调整模板粒度和侧重点。

**方案**：
- 在实际使用中收集不满意的分析输出，针对性调整模板结构
- 每个 skill 目录下可加 `examples/` 放示例输入输出，作为 few-shot 参考
- 每个 skill 目录下可加 `templates/` 支持用户自定义分析模板

**涉及文件**：`read-paper` skill 下的模板文件

#### 2. PDF 本地读取（优先级：高）

**目标**：加入 PDF 下载 + 本地读取能力，减少对外部服务依赖。

**方案**：
- 在 `arxiv_fetch.py` 中新增 `--download` 参数，下载 PDF 到论文目录（`source.pdf`）
- `/read-paper` 流程中，当 AlphaXiv 返回 404 时自动下载 PDF 并直接读取
- 本地 PDF 路径的论文直接读取，不再依赖外部服务

**涉及文件**：`arxiv_fetch.py`、`read-paper` skill

#### 3. Explore-Exploit 平衡（优先级：中）

**目标**：每日推荐中平衡"兴趣相关"和"跨领域探索"。

**方案**：
- `/daily-papers` 筛选时，在精选推荐中固定留出 1 个"探索槽位"
- 探索槽位选择标准：与用户主要领域不直接重叠，但在 arxiv 当日高影响力的论文
- 用户的态度评分也会影响探索比例——如果用户经常给探索推荐高分，逐渐增加探索槽位

**涉及文件**：`daily-papers` skill

#### 4. survey-topic 外部搜索优化（优先级：中）

**目标**：降低 survey-topic 的 token 消耗，提升搜索覆盖率。

**方案**：
- 接入外部 AI 搜索平台（如 NotebookLM、Perplexity）做初步文献搜索
- 先搜索获取候选列表，再对关键论文精读，避免大量 WebSearch 轮次

**涉及文件**：`survey-topic` skill

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

#### 引用量与作者画像
- 接入 Semantic Scholar API 或 [CitationClaw](https://github.com/VisionXLab/CitationClaw) 获取引用量、作者 h-index
- `/daily-papers` 结合引用量信号做更好的排序
- 作者推荐从单纯名字升级为兴趣 + 论文质量 + 引用量综合画像
- 关注作者有新论文时主动通知
- 基于"你关注的作者引用了谁"做二度推荐

#### 社交媒体内容整理
- 支持用户添加关注的 X/小红书博主，推送科研相关内容
- 提取其中提到的论文、观点、讨论，与已有论文库交叉引用
- 参考：[yuanbo-skills/no-more-fomo](https://github.com/freemty/yuanbo-skills/tree/main/no-more-fomo)、[follow-builders](https://github.com/zarazhangrui/follow-builders)

#### 知识复习（艾宾浩斯遗忘曲线）
- 记录每篇论文的阅读时间点和复习时间点
- 按遗忘曲线（1天/3天/7天/14天/30天）生成复习提问
- 新会话开始时自动检查是否有待复习论文
- **前置条件**：需要积累一定量的已分析论文（建议 20+ 篇后开启）

#### Notion 集成
- 通过 Notion API（MCP）将 meta.md + analysis.md 同步到 Notion 数据库
- 支持选择性同步（仅收藏的、评分 ≥ N 的）
- 配合订阅推送，实现分析结果自动同步
- 作为导出渠道，与核心分析功能解耦

#### 订阅与推送
- Followed Blogs 自动检查成熟后独立为订阅 skill
- 支持本地推送/邮件订阅
- 统一管理博客源、作者、社交媒体等订阅渠道

### 输出与展示

#### `/present` — 论文分享页面生成
- 将论文分析结果整合为 HTML 网页，方便组会分享
- 支持多种内容转换：单篇论文 / 多篇论文 / topics 综述 / 研究规划
- 参考：[frontend-slides](https://github.com/zarazhangrui/frontend-slides)

#### 图像生成辅助
- 生成论文方法示意图、架构图等可视化内容
- 参考：[awesome-nanobanana-pro](https://github.com/ZeroLu/awesome-nanobanana-pro)

### 结构演进

#### shared/ 共用工具目录
- 新增 `.claude/skills/shared/` 目录放跨 skill 共用的工具
- `arxiv_fetch.py` 被 read-paper 和 survey-topic 都引用，应迁入 shared/
- 共用的模板片段、常量定义等

#### Skill 分类与组织
- 将 skills 按功能域分类（核心分析 / 数据管理 / 系统维护 / 输出展示）
- 考虑子目录组织或 metadata 标注方案

#### Plugins 化
- 将 ROSE 的 skills 抽象为通用的 Claude Code plugin 形态
- 支持其他用户一键安装使用

---

## 想法收集

> 随时记录新灵感。格式：`- [日期] 想法描述`
> 每次 `/session-digest` 或 `/publish` 时整理：已完成标 `[已整合 → vX.X.X]`，已纳入规划标 `[已规划 → vX.X]`。

### 已整合

- ~~[2026-04-02] 根据行为自动增强 interests 权重~~ [已整合 → v1.0.1]
- ~~[2026-04-02] 维护作者/机构关注列表，推荐时加权~~ [已整合 → v1.0.1]
- ~~[2026-04-02] 论文态度评分影响推荐~~ [已整合 → v1.0.1]
- ~~[2026-04-03] WebSearch 多源结果记录：将搜索中获取的 arxiv/github/reddit/x 等信息分类存储到论文目录~~ [已整合 → v1.0.2]
- ~~[2026-04-03] interests.md 从关键词匹配改为语义描述+模糊匹配~~ [已整合 → v1.0.2]

### 已规划

- ~~[2026-04-02] 知识复习功能（艾宾浩斯遗忘曲线）~~ [已规划 → v2.0]
- ~~[2026-04-02] 每日推荐中平衡 explore 和 exploit~~ [已规划 → v1.5]
- ~~[2026-04-03] 分析模板根据实际输出效果迭代，支持 examples/ 和自定义 templates/~~ [已规划 → v1.5]
- ~~[2026-04-03] PDF 下载+本地读取，减少对外部服务依赖~~ [已规划 → v1.5]
- ~~[2026-04-03] 论文间关联图谱（引用关系、同作者、同方向）~~ [已规划 → v2.0]
- ~~[2026-04-03] /compare-papers skill：对比两篇论文的方法差异~~ [已规划 → v2.0]
- ~~[2026-04-03] daily-papers 结合 Semantic Scholar API 补充引用量排序~~ [已规划 → v2.0]
- ~~[2026-04-03] survey-topic 与 library 已有论文自动关联~~ [已规划 → v2.0]
- ~~[2026-04-03] shared/ 目录放跨 skill 共用工具（如 arxiv_fetch.py）~~ [已规划 → v2.0]
- ~~[2026-04-03] survey-topic 后续接入外部 AI 搜索平台降低 token 消耗~~ [已规划 → v1.5]
- ~~[2026-04-02] 作者推荐结合兴趣+论文质量+引用量（综合画像）~~ [已规划 → v2.0]
- ~~[2026-04-03] 添加X/xhs等社交媒体信息源 + 用户自定义关注博主~~ [已规划 → v2.0]
- ~~[2026-04-03] CitationClaw/Semantic Scholar 引用量集成~~ [已规划 → v2.0]
- ~~[2026-04-03] 论文分析结果转HTML网页用于组会分享（/present skill）~~ [已规划 → v2.0]
- ~~[2026-04-03] 图像生成辅助（方法示意图、架构图）~~ [已规划 → v2.0]
- ~~[2026-04-03] skill 分类与组织（子目录或 metadata 方案）~~ [已规划 → v2.0]

### 已整合（v1.0.3）

- ~~[2026-04-07] daily-papers 推荐论文交互式选择（精选自动保存 + 推荐分批选择）~~ [已整合 → v1.0.3]
- ~~[2026-04-07] daily-papers 已有论文去重检查与状态标注（[已收藏]/[已分析]/[已记录]）~~ [已整合 → v1.0.3]
- ~~[2026-04-07] library/README.md 索引增强（发表日期、收集日期、来源、概述列）~~ [已整合 → v1.0.3]
- ~~[2026-04-07] meta.md 新增 source 和 collected_date 字段~~ [已整合 → v1.0.3]

### 已整合（v1.0.3 续）

- ~~[2026-04-09] survey-topic --idea 模式：研究 idea 验证与规划（可行性分析、竞争论文对比、研究计划生成）~~ [已整合 → v1.0.3]
- ~~[2026-04-10] read-paper AlphaXiv markdown 本地缓存（alphaxiv-overview.md / alphaxiv-abs.md）~~ [已整合 → v1.0.3]
- ~~[2026-04-10] read-paper QA 分主题详细记录（qa/ 子目录 + frontmatter description 轻量扫描）~~ [已整合 → v1.0.3]

### 已整合（v1.0.4）

- ~~[2026-04-13] read-paper 库存论文关联分析：分析后自动扫描本地库，按 tags/作者/方法/Topics 四维度检测关联~~ [已整合 → v1.0.4]

### 已整合（v1.0.5）

- ~~[2026-04-21] Blog 支持：扩展 read-paper 支持博客/项目页面等非论文内容，新增 library/blogs/ 目录、Followed Blogs 订阅、daily-papers 博客源检查~~ [已整合 → v1.0.5]

### 待整理

（暂无）

### 已规划（新增）
- ~~[2026-04-10] update-note skill：将论文格式化提交到 Notion 数据库并 push 远程备份~~ [已规划 → v2.0]
- ~~[2026-04-21] 订阅与推送功能：Followed Blogs 自动检查成熟后独立为订阅 skill，支持本地推送/邮件订阅~~ [已规划 → v2.0]
- ~~[2026-04-21] Notion MCP 集成优先级提升：配合订阅推送，实现论文分析结果同步到 Notion~~ [已规划 → v2.0]
