下面是我整理的：



\# \*\*① 完整的 Functional Requirements（功能需求清单）\*\*



\# \*\*② 一个贯穿全系统的用户使用全流程示例（End-to-End Use Case）\*\*

\# ============================================



\# 📌 \*\*① 完整 Functional Requirements（系统功能需求）\*\*



\# ============================================



功能需求分为 \*\*用户功能需求（User-facing）\*\* 和 \*\*系统功能需求（Backend / AI / Graph）\*\* 两大类。



---



\# 🎯 \*\*A. 用户功能需求（User-Facing Features）\*\*



用户直接体验到的能力。



---



\## \*\*A1. 学术问答（Core）\*\*



用户可以向系统提问，系统需：



\* 利用图谱提供高质量学术答案

\* 结合用户个人图谱提供个性化回答

\* 自动引用来源（论文、facts、episodes）

\* 当图谱缺失信息时 → 自动进行外部搜索（arXiv/Scholar/网络）



\*\*范围包括：\*\*



\* 提问某一方法/模型/任务

\* 调研某一领域

\* 对比两篇论文

\* 询问论文之间关系



---



\## \*\*A2. 论文查询与阅读辅助\*\*



用户可以：



\* 搜索论文（title / keyword）

\* 查看论文结构化信息（方法、任务、数据集、结果）

\* 查看作者、引用、所属社区

\* 查看论文之间的关系

\* 生成该论文的：



&nbsp; \* 总结

&nbsp; \* 创新点

&nbsp; \* 缺点

&nbsp; \* 方法流程图（自然语言）

&nbsp; \* 实验结论

\* 比较两篇或多篇论文



---



\## \*\*A3. 用户个性化科研记忆（Graphiti Memory）\*\*



系统自动为用户构建「个人科研知识图谱」，包括：



\* 用户阅读过哪些论文

\* 用户对哪类问题感兴趣

\* 用户的研究方向画像

\* 用户经常查询的方法/任务

\* 用户论文自动聚类 → 形成个人研究社区（主题）

\* 为用户提供个性化的建议：



&nbsp; \* 研究方向推荐

&nbsp; \* 值得关注的论文

&nbsp; \* 社区趋势变化



---



\## \*\*A4. 论文上传解析\*\*



用户可上传论文（PDF/HTML/URL），系统需自动：



\* 解析 PDF（文本、结构）

\* 拆分为 Episode（段落）

\* 抽取 Paper / Method / Dataset / Task 等实体

\* 抽取事实关系（PROPOSES、EVALUATES\_ON、SOLVES 等）

\* 自动构建用户个性图谱

\* 输出摘要、创新点、流程图等



---



\## \*\*A5. 外部论文搜索（Fallback）\*\*



当图谱中无法找到足够信息：



\* 系统自动调用 arXiv API / Semantic Scholar

\* 下载论文

\* 构建图谱

\* 再回答用户



这是本系统的关键能力：\*\*随着用户使用，图谱不断自动扩展。\*\*



---



\## \*\*A6. 图谱可视化\*\*



用户可以查看：



\* 实体节点关系图（Paper、Method、Dataset、Task…）

\* 社区聚类图（研究主题）

\* 用户个人知识图谱



---



\## \*\*A7. 聊天与任务历史\*\*



用户可：



\* 查看历史对话

\* 查看系统之前为用户解析过的论文

\* 继续上一次研究话题

\* 重新询问之前的论文



---



\## \*\*A8. 科研辅助工具（可选阶段）\*\*



\* 生成研究提案

\* 写 related work

\* 自动生成论文笔记

\* 自动写 Code Snippet（根据论文方法）

\* 模拟面试 / Oral Presentation



---



\# 🎯 \*\*B. 系统功能需求（Backend + AI + Graphiti）\*\*



系统为了实现用户功能而必须具备的能力。



---



\## \*\*B1. 图谱检索 Pipeline（Graph Retrieval Orchestrator）\*\*



\* 优先使用用户图谱

\* 若不够 → 使用公共科研图谱

\* 再不够 → 自动触发外部检索

\* 聚合多个来源的证据



支持：



\* 向量检索

\* 图遍历（neighbors, multi-hop）

\* 结构检索（按关系、按 schema）



---



\## \*\*B2. 图谱构建 Pipeline（Graphiti Ingestion Pipeline）\*\*



论文 → Episode → Entity → Fact → Community



Pipeline 包括：



1\. PDF → 文本解析

2\. Section/Paragraph 分块

3\. 构建 Episode 节点

4\. LLM 解析实体（Paper / Method / Task / Dataset …）

5\. LLM 抽取 Facts

6\. 去重、归一化

7\. 写入 Graphiti（用户图谱 or 公共图谱）

8\. 自动 Community Detection



---



\## \*\*B3. 实体 Schema 管理与类型归一化\*\*



系统必须维护科研图谱 Schema：



\* Paper

\* Author

\* Institution

\* Method

\* Task

\* Dataset

\* Metric

\* Result

\* Concept

\* Community



并能：



\* 合并重复实体

\* 使用 embedding 归一化

\* 自动识别实体类型



---



\## \*\*B4. 事实管理（Fact Lifecycle）\*\*



Graphiti 的双时间线：



\* tvalid / tinvalid（事实真实有效性）

\* t'created / t'expired（存储时间）



系统需支持：



\* 新事实加入

\* 旧事实失效（例如论文被撤稿）

\* 事实去重

\* 事实更新



---



\## \*\*B5. LLM Agent 功能\*\*



Agent 必须：



\* 理解用户 query

\* 调用工具（graph\_query、external\_search、pdf\_parse 等）

\* 综合图谱结果

\* 生成用户可读的答案



---



\## \*\*B6. 用户画像与个性化模型\*\*



系统维护：



\* 用户兴趣 embedding

\* 用户研究社区

\* 用户最近阅读历史

\* 个性化推荐



---



\## \*\*B7. 前端服务\*\*



\* 聊天 UI

\* 论文阅读器

\* 图谱可视化（Force graph / Sankey / Tree）

\* 用户个人中心



---



\## \*\*B8. 定时任务\*\*



\* 每日更新 arXiv 数据

\* 重建社区聚类

\* 清理失效事实

\* Graphiti 快照备份



---



\# ============================================



\# 📌 \*\*② 全系统贯穿示例（End-to-End Use Case）\*\*



\# ============================================



以用户“小李”（研究方向：视觉 Transformer）为例。



我们用一个真实的场景贯穿所有功能。



---



\# 🎬 \*\*Step 1：用户提问\*\*



小李在 Chat 页面输入：



> \*“最近视觉 Transformer 有哪些新的改进？能帮我总结一下吗？”\*



---



\# 🎬 \*\*Step 2：检索管线启动\*\*



Agent 判断需要：



\* 检索「Vision Transformer」相关节点

\* 检索 2022–2024 论文

\* 找到相关 communities



Agent 调用：



```

graph\_query("vision transformer", scope="auto")

```



系统从 \*\*用户图谱 + 公共图谱\*\* 各找到若干论文。



---



\# 🎬 \*\*Step 3：图谱相关论文不足 → 启动外部搜索\*\*



系统发现：



\* 用户图谱：包含 2 篇 ViT 相关论文

\* 公共图谱：19 篇

\* 但系统判定 coverage < threshold（例如 0.4）



于是自动触发：



```

external\_search("Vision Transformer improvements 2023–2024")

```



抓取 arXiv 最新 10 篇新论文。



---



\# 🎬 \*\*Step 4：自动构建图谱\*\*



系统自动解析其中一篇，例如：



\*\*“Swin Transformer V3”\*\*



执行 pipeline：



\* 下载 PDF

\* PDF → 文本

\* 文本 → Episode

\* Episode → Entities（Method=SwinV3, Dataset=ImageNet, Task=Classification）

\* 抽取 Facts：



&nbsp; \* Paper → PROPOSES → Method:SwinV3

&nbsp; \* SwinV3 → IMPROVES\_OVER → SwinV2

&nbsp; \* Evaluation → DATASET:ImageNet

\* 写入全局图谱

\* 也写入用户图谱



图谱自动更新。



---



\# 🎬 \*\*Step 5：社区更新\*\*



新论文加入后，Graphiti 自动触发：



```

Community detection for: Vision Transformers

```



更新 “Vision Transformer Research Community”



---



\# 🎬 \*\*Step 6：Agent 整合图谱回答用户问题\*\*



LLM 根据图谱生成综合回答：



> 近两年视觉 Transformer 的主要改进包括：

>

> 1. \*\*结构优化\*\*：Swin Transformer V3 引入了 \*\*token-mixing normalization\*\*，减少训练不稳定性……

> 2. \*\*训练加速\*\*：Dynamic ViT 系列通过……

> 3. \*\*应用扩展\*\*：MedViT 将 ViT 应用于医学影像……

>

> 我认为你特别关注 \*\*模型结构创新\*\*，这里给你重点方向。

> 另外，你个人图谱已自动增加 3 篇论文。



（引用来源全部来自 fact + episode）



---



\# 🎬 \*\*Step 7：用户上传论文 PDF\*\*



小李上传：



> \*“ConvNeXt V2: Co-designing and scaling ConvNets with Masked Autoencoders”\*



系统自动构图：



\* Paper

\* Author

\* Method（ConvNeXt V2）

\* Task

\* Dataset

\* Fact（IMPROVES\_OVER）



加入小李的个人图谱。



---



\# 🎬 \*\*Step 8：用户问：\*\*



> “请你对比 Vision Transformer 和 ConvNeXt V2 的优缺点。”



Agent 执行：



\* graph\_query(vit, neighbors=2)

\* graph\_query(convnextv2, neighbors=2)

\* 搜索事实关系：性能指标、训练成本、趋势



生成对比：



| 对比项  | ViT               | ConvNeXt V2 |

| ---- | ----------------- | ----------- |

| 架构   | Transformer       | Modern CNN  |

| 优势   | 大模型可扩展性强          | 高效 + 性能稳定   |

| 训练成本 | 更高                | 更实用         |

| 最新进展 | Swin V3, DeiT III | ConvNeXt V2 |



---



\# 🎬 \*\*Step 9：系统更新个性化科研画像\*\*



系统记录：



\* 用户关注 Vision Transformer

\* 用户最近学习 ConvNeXt

\* 用户对比 CNN vs Transformer



更新用户画像：



> “你当前主要研究方向是：模型结构设计（Transformer vs ConvNet）”



并提供：



> “建议：你可能会对 Meta 的 Mamba 架构论文感兴趣，要我帮你总结吗？”



---



\# ============================================



\# 📌 \*\*总结：本例贯穿了所有系统功能\*\*



\# ============================================



| 模块                        | 在示例中体现         |

| ------------------------- | -------------- |

| 学术问答                      | Step 1, Step 6 |

| 图谱检索                      | Step 2         |

| 外部搜索                      | Step 3         |

| 图谱构建                      | Step 4         |

| 论文解析                      | Step 7         |

| Entity + Fact + Community | Step 4, 5      |

| 个性化图谱                     | Step 6, Step 9 |

| 论文对比                      | Step 8         |

| 用户画像                      | Step 9         |



