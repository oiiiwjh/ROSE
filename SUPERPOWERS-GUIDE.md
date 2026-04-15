# Superpowers Plugin 使用指南

> 版本: 5.0.7 | 适用于 Claude Code / Copilot CLI / Cursor / Gemini CLI 等平台

Superpowers 是一个面向编码 Agent 的**结构化软件开发工作流插件**。它通过一系列可组合的 "skills" 来引导 Agent 按照严格的工程纪律完成开发任务，核心理念是：**测试先行、系统化调试、证据驱动、杜绝臆测**。

## 核心工作流

典型的完整开发流程：

```
brainstorming → writing-plans → [using-git-worktrees] → subagent-driven-development → requesting-code-review → finishing-a-development-branch
```

每个环节由对应的 skill 驱动，Agent 会自动识别并调用。你也可以在对话中主动触发。

---

## Skills 速查表

### 设计与规划

| Skill | 触发时机 | 作用 |
|-------|---------|------|
| `brainstorming` | 任何创造性工作开始前 | 通过苏格拉底式对话探索需求、生成设计方案、输出 spec 文档 |
| `writing-plans` | 有了 spec 后、写代码前 | 将 spec 拆分为可执行的实现计划，每步 2-5 分钟粒度 |

### 实现与执行

| Skill | 触发时机 | 作用 |
|-------|---------|------|
| `executing-plans` | 有计划后在当前会话执行 | 逐步执行计划，带验证检查点 |
| `subagent-driven-development` | 有计划后用子 Agent 并行执行 | 每个任务派发独立子 Agent，双阶段 review（spec 合规 + 代码质量） |
| `dispatching-parallel-agents` | 面对 2+ 个独立问题 | 并行派发多个 Agent 处理无依赖的子任务 |
| `test-driven-development` | 写任何功能或修 bug 前 | 强制 RED-GREEN-REFACTOR 循环：先写失败测试，再写最小实现 |
| `using-git-worktrees` | 需要隔离开发环境时 | 创建 git worktree 隔离工作区，自动检测并运行项目 setup |

### 质量保障

| Skill | 触发时机 | 作用 |
|-------|---------|------|
| `systematic-debugging` | 遇到 bug 或测试失败 | 四阶段根因分析：调查 → 模式分析 → 假设验证 → 实现修复 |
| `verification-before-completion` | 即将声称工作完成时 | 强制运行验证命令并检查输出，杜绝"应该没问题" |
| `requesting-code-review` | 完成重要功能后 | 派发 code-reviewer 子 Agent 审查代码 |
| `receiving-code-review` | 收到 review 反馈时 | 技术严谨地处理反馈：先验证再实现，该 push back 时 push back |
| `finishing-a-development-branch` | 实现完成、测试通过后 | 提供 4 个选项：合并 / 创建 PR / 保留分支 / 丢弃 |

### 元技能

| Skill | 触发时机 | 作用 |
|-------|---------|------|
| `writing-skills` | 创建或修改 skill 时 | 用 TDD 方法编写 skill：先测试 Agent 无 skill 时的行为，再编写 |
| `using-superpowers` | 每次对话开始 | 自动加载，确保 Agent 在响应前先检查是否有适用的 skill |

---

## 使用场景与示例

### 场景 1: 开发一个新功能

**你说：** "给 ROSE 添加一个 /compare-papers skill，对比两篇论文的方法差异"

**Agent 行为链：**
1. `brainstorming` 自动触发 — 与你对话探索需求（对比哪些维度？输出什么格式？），生成设计 spec
2. `writing-plans` — 将 spec 拆分为实现步骤（创建 skill 目录、写 prompt、写 command wrapper、更新文档）
3. `using-git-worktrees` — 创建隔离的 worktree 分支
4. `subagent-driven-development` — 每个步骤派发子 Agent 执行，完成后自动 review
5. `requesting-code-review` — 全部完成后审查整体实现
6. `finishing-a-development-branch` — 提供合并/PR 选项

**你需要做的：** 在 brainstorming 阶段回答问题、确认设计方案；在 finishing 阶段选择合并方式。

---

### 场景 2: 修复一个 Bug

**你说：** "/daily-papers 推荐结果里出现了重复论文"

**Agent 行为链：**
1. `systematic-debugging` 自动触发 — 不会直接改代码，而是：
   - 复现问题（运行 daily-papers 观察输出）
   - 追踪数据流（CSV → 筛选 → 去重逻辑）
   - 定位根因（去重只比较了 arxiv_id 但忽略了格式差异）
2. `test-driven-development` — 先写一个能复现 bug 的测试（输入含格式不一致的 ID，断言去重后无重复）
3. 修复代码，测试通过
4. `verification-before-completion` — 重新运行完整测试确认修复

**你需要做的：** 提供复现步骤或示例数据（如果有的话）。

---

### 场景 3: 理解并重构一段代码

**你说：** "重构 arxiv_daily.py 的 HTML 解析逻辑，现在太脆弱了"

**Agent 行为链：**
1. `brainstorming` — 探索重构目标（更健壮？更快？更易维护？），生成设计
2. `test-driven-development` — 先为现有行为写测试（确保重构不破坏功能）
3. 重构代码，持续运行测试
4. `verification-before-completion` — 端到端验证

---

### 场景 4: 并行处理多个独立问题

**你说：** "有三个 skill 各自有 bug：read-paper 的 PDF 下载失败、daily-papers 的日期解析错误、manage-library 的搜索不区分大小写"

**Agent 行为链：**
1. `dispatching-parallel-agents` — 识别出三个独立问题，并行派发 3 个 Agent
2. 每个 Agent 各自用 `systematic-debugging` + `test-driven-development` 修复自己的 bug
3. 汇总结果，统一验证

---

### 场景 5: 代码审查与反馈处理

**你做了一个 PR，收到 review 反馈：** "这个函数应该用 async"

**Agent 行为链（`receiving-code-review` 触发）：**
1. 不会立即说"好的马上改" — 先验证：这个函数是否确实需要 async？调用链中有异步操作吗？
2. 如果确实需要 → 实现修改并测试
3. 如果不需要 → 礼貌但坚定地 push back，给出技术理由

---

### 场景 6: 创建新的 Skill

**你说：** "帮我写一个新的 superpowers skill"

**Agent 行为链（`writing-skills` 触发）：**
1. **RED**: 先在没有 skill 的情况下测试 Agent 行为（记录 Agent 自然会犯什么错）
2. **GREEN**: 针对这些错误编写最小 skill，重新测试直到 Agent 行为符合预期
3. **REFACTOR**: 识别 Agent 可能的"变通"借口，在 skill 中显式封堵

---

## 手动触发 Skill

大多数场景下 Superpowers 会自动识别并调用合适的 skill。但你也可以主动引导：

```
# 直接说出意图，Agent 会自动匹配 skill
"帮我设计一个新功能"              → brainstorming
"写个实现计划"                    → writing-plans
"用子 Agent 并行执行这个计划"      → subagent-driven-development
"这个 bug 帮我查一下"             → systematic-debugging
"帮我 review 一下刚写的代码"       → requesting-code-review
"创建一个 worktree 来做这个功能"   → using-git-worktrees
```

---

## 核心哲学

1. **证据先于断言** — 声称"测试通过"前必须实际运行测试并检查输出
2. **根因先于修复** — 永远不修表象，追踪到根本原因再动手
3. **测试先于代码** — 先写失败测试，再写最小实现，最后重构
4. **过程先于直觉** — 遵循结构化流程，不靠猜测和"应该没问题"
5. **隔离保安全** — 用 worktree 隔离开发，用子 Agent 隔离上下文
6. **YAGNI 无情** — 只写测试要求的代码，不写"将来可能用到"的
7. **双阶段审查** — 先检查是否符合 spec，再检查代码质量

---

## 文件产出位置

Superpowers 在工作过程中会生成以下文件：

| 文件 | 路径 | 内容 |
|------|------|------|
| 设计文档 | `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` | brainstorming 产出的设计 spec |
| 实现计划 | `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` | writing-plans 产出的分步计划 |

---

## 与 ROSE 的配合

在 ROSE 项目中，Superpowers 可以辅助以下场景：

- **开发新 Skill**：brainstorming 设计 skill 交互 → writing-plans 拆分步骤 → subagent-driven-development 实现
- **重构现有 Skill**：systematic-debugging 分析问题 → test-driven-development 安全重构
- **修复 Bug**：systematic-debugging 定位 → verification-before-completion 确认修复
- **批量处理**：dispatching-parallel-agents 并行修复多个独立问题

注意：ROSE 的 skill prompts 是指令文档而非代码，Superpowers 中的 TDD 等 skill 更适合用在 Python 脚本（如 `arxiv_fetch.py`、`arxiv_daily.py`、`generate_index.py`）的开发和调试上。
