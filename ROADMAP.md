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

> 随时记录新灵感。格式：`- [日期] 想法描述`
> 每次 `/session-digest` 或 `/publish` 时整理：已完成标 `[已整合 → vX.X.X]`，已纳入规划标 `[已规划 → vX.X]`。

### 已整合

- ~~[2026-04-02] 根据行为自动增强 interests 权重~~ [已整合 → v1.0.1]
- ~~[2026-04-02] 维护作者/机构关注列表，推荐时加权~~ [已整合 → v1.0.1]
- ~~[2026-04-02] 论文态度评分影响推荐~~ [已整合 → v1.0.1]

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

### 待整理

- [2026-04-03] survey-topic 后续接入外部 AI 搜索平台（如 NotebookLM）降低 token 消耗，先搜索再精读
- [2026-04-02] 作者推荐不应只给名字，应结合兴趣+论文质量+引用量
- [2026-04-03] 爬取或涉及到论文相关信息搜集，可以后续添加X/xhs等难直接爬取到平台
- [2026-04-03] 支持用户添加自己喜欢的X博主等，可以参考 https://github.com/freemty/yuanbo-skills/tree/main/no-more-fomo 中推送关注消息的功能，以及https://github.com/zarazhangrui/follow-builders
- [2026-04-03] https://github.com/VisionXLab/CitationClaw 计划添加引用量
- ~~[2026-04-03] WebSearch 多源结果记录：将搜索中获取的 arxiv/github/reddit/x 等信息分类存储到论文目录~~ [已整合 → v1.0.2]
- ~~[2026-04-03] interests.md 从关键词匹配改为语义描述+模糊匹配~~ [已整合 → v1.0.2]
- skill计划：考虑将论文分析结果整合成html版本的网页，方便组会分享。（考虑多种内容进行转换，例如单篇论文/多篇论文/topics分析/研究规划/研究兴趣等）参考skill：https://github.com/zarazhangrui/frontend-slides
- skill计划：考虑添加图像生成功能，参考https://github.com/ZeroLu/awesome-nanobanana-pro中的skill设计
- skill计划：添加https://github.com/nextlevelbuilder/ui-ux-pro-max-skill 中的用户界面设计功能
- skill分类规划，思考如何对skills进行分类？或者分子目录等
