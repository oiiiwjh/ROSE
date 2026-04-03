# ROSE 数据迁移注册表

> 记录每个 schema 版本跳转所需的用户数据迁移操作。
> `/update` 在 Step 5.5 中读取此文件，按顺序执行需要的迁移。

**当前最新 schema_version: 2**

---

## schema v1 → v2 (ROSE v1.0.2)

**触发条件**：`library/interests.md` 无 frontmatter 或 `schema_version` 缺失/为 1

### interests.md 迁移步骤

1. **`## Primary Areas` + `## Keywords` → `## 研究方向描述`**
   - 读取 `## Primary Areas` 下的条目作为子标题
   - 读取 `## Keywords` 下的关键词列表
   - 按 Primary Areas 分组，将每组对应的关键词扩展为一段自然语言描述
   - 示例转换：
     ```
     # 旧格式
     ## Primary Areas
     - 图像生成与编辑 (Image Generation & Editing)

     ## Keywords
     - diffusion, image editing, text-to-image

     # 新格式
     ## 研究方向描述
     ### 图像生成与编辑
     关注 diffusion model 在图像生成、图像编辑、text-to-image 方面的进展。
     ```
   - 如果 Keywords 中有无法归入任何 Primary Area 的关键词，单独创建一个 `### 其他关注` 子标题

2. **新增 `## 代表性高分论文`**
   - 添加空段落（含注释说明格式）
   - 如果 `library/papers/` 中有 `rating >= 4` 的论文，自动填充
   ```markdown
   ## 代表性高分论文
   <!-- 评分 ≥4 的论文自动追加。格式: - [{arxiv_id}] 一句话描述 -->
   ```

3. **`## Keyword Weights` → `## 兴趣权重`**
   - 仅改段落标题，保留所有已有数据
   - 如果无此段落，创建空段落

4. **`## Followed Authors` 格式补充**
   - 保留已有数据
   - 如果无此段落，创建空段落并添加格式注释
   ```markdown
   ## Followed Authors
   <!-- 评分 ≥4 的论文作者自动加入。格式: 作者名: {count, last_paper, note} -->
   ```

5. **`## Arxiv Categories` — 保持不变**

6. **添加 frontmatter**
   ```yaml
   ---
   schema_version: 2
   ---
   ```

### 迁移特性
- **非破坏性**：保留所有原有数据，只重新组织格式
- **可回退**：迁移前的内容可通过 `git diff` 查看
- **需确认**：迁移前展示变更预览，用户确认后执行
