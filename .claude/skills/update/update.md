---
description: "检查并更新 ROSE 系统文件。从 GitHub 获取最新的 skills、commands 和文档，不触碰用户数据"
---

# ROSE 系统更新

你是 ROSE 系统的更新助手。检查 GitHub 上游是否有系统文件更新，安全地将更新应用到本地，绝不触碰用户数据（library/）。

**核心原则**：只更新系统文件，绝不覆盖用户数据。

## 输入

用户输入: $ARGUMENTS

可选参数：
- `--check`: 仅检查是否有更新，不执行更新
- 无参数: 完整流程（检查 → 展示 → 确认 → 更新）

---

## 系统文件与用户数据的边界

| 类别 | 路径 | 更新行为 |
|------|------|----------|
| **系统文件** | `.claude/commands/*`, `.claude/skills/*`, `.claude/changelog/*`, `CLAUDE.md`, `README.md`, `ROADMAP.md` | 检查 + 可覆盖 |
| **用户数据** | `library/**`（papers, tmp, daily, topics, interests.md） | **绝不触碰** |
| **用户配置** | `.gitignore`, `LICENSE`, `config.md`, `.claude/settings.local.json`, `.vscode/` | **不覆盖** |

---

## Step 1: 检查更新

运行检查脚本：

```bash
bash .claude/skills/update/check_update.sh
```

解析输出：
- `STATUS:up-to-date` → 告知用户"已是最新版本"，结束
- `STATUS:skip` → 告知用户"网络不可用，跳过更新检查"，结束
- `STATUS:error` → 告知用户错误原因，结束
- `STATUS:updates-available` → 继续 Step 2

如果用户指定了 `--check`，展示结果后结束，不执行更新。

---

## Step 2: 展示变更摘要

### 2.1 展示变更文件列表

从 `check_update.sh` 的 `FILES:` 输出中提取变更文件列表，按类别分组展示：

```
ROSE 有 {N} 个系统文件可更新：

Commands:
  - .claude/commands/xxx.md (新增/修改)

Skills:
  - .claude/skills/xxx/xxx.md (修改)

文档:
  - CLAUDE.md (修改)
  - README.md (修改)

Changelog:
  - .claude/changelog/xxx.md (新增)
```

### 2.2 展示最新 changelog

如果 `.claude/changelog/` 有变更，运行以下命令获取最新 changelog 内容并展示：

```bash
git show origin/main:.claude/changelog/{最新日期文件}
```

这样用户能看到上游做了什么改动。

---

## Step 3: 检查本地冲突

检查用户是否对系统文件有本地改动：

```bash
git diff --name-only -- .claude/commands/ .claude/skills/ .claude/changelog/ CLAUDE.md README.md ROADMAP.md
```

- **如果没有本地改动**：直接进入 Step 4
- **如果有本地改动**：警告用户

```
注意：以下系统文件有本地改动，更新会覆盖这些改动：
  - .claude/skills/read-paper/read-paper.md
  - CLAUDE.md

你可以选择保留本地改动或让上游版本覆盖。
```

---

## Step 4: 确认更新

使用 AskUserQuestion 询问：

**问题**：确认更新操作？

选项：
- **立即更新** — 更新所有系统文件（如有本地改动会被覆盖）
- **查看详细 diff** — 先查看每个文件的具体变更内容，再决定
- **选择性更新** — 只更新部分文件（如果有本地改动的文件想保留）
- **跳过** — 本次不更新

### 如果选择「查看详细 diff」

对每个变更文件运行：

```bash
git diff HEAD..origin/main -- <file>
```

展示后再次询问是否更新。

### 如果选择「选择性更新」

使用 AskUserQuestion（multiSelect）列出所有变更文件，让用户选择要更新的文件。

---

## Step 5: 执行更新

对每个确认更新的文件，执行：

```bash
git checkout origin/main -- <file_path>
```

这会用上游版本精确覆盖本地文件，自动 stage 到暂存区。

如果有新增的文件（上游新增但本地不存在的），同样通过 `git checkout origin/main -- <file>` 获取。

---

## Step 6: 提交更新

```bash
git commit -m "Update ROSE system files to latest version

Updated files:
{变更文件列表}"
```

---

## Step 7: 完成信息

```
ROSE 系统文件已更新！

更新了 {N} 个文件：
  {文件列表}

用户数据（library/）未受影响。

如需查看完整变更历史：
  git log --oneline -5
```
