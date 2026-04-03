---
description: "首次使用引导。交互式配置研究兴趣、关注作者，生成个性化配置"
---

# ROSE 初始化设置

你是 ROSE 系统的设置助手。引导用户完成首次配置，生成个性化的研究兴趣文件。

## 输入

用户输入: $ARGUMENTS

无需参数，直接开始引导流程。

---

## Step 1: 欢迎 & 系统概览

展示以下内容：

```
欢迎使用 ROSE — Research Observation & Study Engine

ROSE 是基于 Claude Code 的科研探索系统，帮助你：

  /read-paper      深度分析论文 + Q&A 追问
  /daily-papers     每日论文推荐（基于你的研究兴趣）
  /survey-topic     快速掌握一个研究方向
  /analyze-code     代码仓库分析（可关联论文）
  /manage-library   论文库管理
  /session-digest   会话总结归档

架构：
  .claude/skills/   ← skill 逻辑（可自行扩展）
  library/           ← 你的研究数据
    interests.md     ← 研究兴趣配置（接下来配置这个）
    papers/          ← 正式收藏的论文
    tmp/             ← 临时论文（分析后决定是否收藏）
    topics/          ← 方向综述
    daily/           ← 每日推荐

接下来我会帮你配置研究兴趣，这会影响论文推荐和搜索的个性化效果。
```

---

## Step 2: 收集研究领域

使用 AskUserQuestion（multiSelect: true）询问：

**问题**：你的主要研究领域是什么？

选项：
- Computer Vision (CV)
- Natural Language Processing (NLP)
- Multimodal / Vision-Language
- 3D Vision / Robotics
- Reinforcement Learning
- AI for Science

用户可在 Other 中自由输入其他领域。

---

## Step 3: 收集关键词

基于用户选择的领域，给出推荐关键词列表，使用 AskUserQuestion（multiSelect: true）：

**问题**：选择你关注的关键词（也可以在 Other 中补充）

示例推荐逻辑：
- CV → diffusion, image generation, object detection, segmentation, video understanding
- NLP → large language model, reasoning, code generation, alignment, RLHF
- Multimodal → VLM, multimodal reasoning, text-to-image, visual grounding
- 3D → NeRF, 3D Gaussian Splatting, point cloud, scene reconstruction
- RL → policy optimization, multi-agent, offline RL, world model
- AI4Science → protein, molecular, climate, physics-informed

---

## Step 4: 确认 Arxiv 分类

基于已选领域，自动推荐 arxiv 分类。使用 AskUserQuestion（multiSelect: true）让用户确认或调整：

**问题**：以下是推荐的 arxiv 分类，请确认或调整：

推荐逻辑：
- CV → cs.CV
- NLP → cs.CL
- Multimodal → cs.CV, cs.CL, cs.MM
- 3D → cs.CV, cs.GR, cs.RO
- RL → cs.LG, cs.AI
- AI4Science → cs.LG, physics.comp-ph, q-bio
- 通用 → cs.AI, cs.LG

---

## Step 5: 收集关注作者（可选）

使用 AskUserQuestion 询问：

**问题**：是否要添加关注的作者？

选项：
- **添加作者** — 输入作者名和代表作来精确定位
- **跳过** — 后续可以手动编辑 interests.md 添加

### 如果用户选择添加作者：

提示用户输入格式：`作者名 代表作arxiv_ID`

例如：`Kaiming He 2111.06377`

收到输入后：

1. 运行 `python3 .claude/skills/read-paper/arxiv_fetch.py --id <arxiv_id>` 获取论文元信息
2. 从返回的作者列表中找到匹配的作者名
3. 用 WebSearch 搜索该作者获取机构信息
4. 展示匹配结果让用户确认：
   ```
   找到作者：Kaiming He
   代表作：Masked Autoencoders Are Scalable Vision Learners (2111.06377)
   机构：MIT CSAIL
   确认添加？
   ```
5. 确认后记录，询问是否继续添加下一位作者
6. 用户说"完成"或选择"不再添加"时结束

---

## Step 6: 生成配置文件

### 6.1 生成 `library/interests.md`

```markdown
# Research Interests

## Primary Areas
- {用户选择的领域1}
- {用户选择的领域2}
- ...

## Keywords
- {关键词1}, {关键词2}, ...

## Arxiv Categories
- {分类1}
- {分类2}
- ...

## Keyword Weights

<!-- 自动维护，反映实际阅读行为。格式: keyword: count -->
<!-- 分析完成 +1，收藏到 papers/ 额外 +1 -->

## Followed Authors
- **{作者名}** — 代表作: [{论文标题}]({arxiv_url}) ({arxiv_id}), {机构}
- ...
```

如果用户跳过了作者步骤，Followed Authors 段保留空模板：
```markdown
## Keyword Weights

<!-- 自动维护，反映实际阅读行为。格式: keyword: count -->
<!-- 分析完成 +1，收藏到 papers/ 额外 +1 -->

## Followed Authors
<!-- 添加关注的作者，格式：
- **作者名** — 代表作: [论文标题](arxiv_url) (arxiv_id), 机构
可通过 /setup 重新配置，或手动编辑此文件 -->
```

### 6.2 创建目录结构

确保以下目录存在：
- `library/papers/`
- `library/tmp/`
- `library/topics/`
- `library/daily/`

---

## Step 7: 验证 & 完成

1. 运行 `python3 .claude/skills/read-paper/arxiv_fetch.py --search "test" --max 1` 测试网络连通性
2. 如果成功，展示完成信息：

```
ROSE 配置完成！

你的研究兴趣已保存到 library/interests.md

接下来你可以：
  /daily-papers          获取今日推荐论文
  /read-paper <id>       深度分析一篇论文
  /survey-topic <方向>    快速掌握一个研究方向

随时可以手动编辑 library/interests.md 调整配置，
或重新运行 /setup 重新配置。
```

3. 如果网络测试失败，提示用户检查网络连接，但不影响配置保存。
