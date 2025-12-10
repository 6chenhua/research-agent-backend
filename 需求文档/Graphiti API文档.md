# 📚 Graphiti 知识图谱 API 文档
## 🎯 1. 核心概念 (Core Concepts)
Graphiti 库通过以下核心机制来构建和管理图谱环境：

| 概念 | 描述 | 关键机制 |
| :--- | :--- | :--- |
| **Episode** | 图谱中的一个核心数据单元，代表单一数据摄入或事件。 | [cite_start]通过 `graphiti.add-episode` 或 `add-episode-bulk` 添加。所有边默认类型都是 `MENTIONS` [cite: 3, 11]。 |
| **Namespacing** | [cite_start]允许在同一个 Graphiti 实例内创建隔离的图环境，使多个独立的知识图谱无干扰共存 [cite: 26, 27, 28]。 | [cite_start]通过传递 `group_id` 参数 (`str`) 实现 [cite: 29]。 |
| **Community** | [cite_start]代表一组相关的实体节点，每个社区包含一个摘要 [cite: 21, 22]。 | [cite_start]使用 `build_commuities()` 生成 [cite: 23][cite_start]。可通过 `update-communties=True` 更新 [cite: 24]。 |
| **自定义类型** | [cite_start]允许利用 Pydantic 自定义实体类型和关系类型 [cite: 14]。 | [cite_start]支持模式演进，可随时添加新属性 [cite: 18]。 |


---

## 📥 2. 数据摄入 (Data Ingestion)
### 2.1 添加 Episode (`graphiti.add-episode`)
用于单一数据摄入。

| 参数 | 类型 | 描述 | 来源 |
| :--- | :--- | :--- | :--- |
| `Name` | `str` | [cite_start]Episode 的名称 [cite: 4, 5]。 |  |
| `episode-body` | `str` / `dict` | [cite_start]实际数据部分，`dict` 格式为 `{role/name}:{message}` [cite: 6, 7]。 |  |
| `source` | `Episode.text` / `Episode.Json` / `Episode.Message` | [cite_start]Episode 的类型 [cite: 8]。 |  |
| `source_description` | `str` | [cite_start]对数据来源的描述 [cite: 9]。 |  |
| `reference-time` | `datetime` | [cite_start]参考时间 [cite: 10]。 |  |
| `group_id` | `str` | [cite_start]指定图命名空间 [cite: 30]。 |  |
| `update-communties` | `bool` | [cite_start]设为 `True` 可在添加时更新社区 [cite: 24]。 |  |
| `excluded-entity-typs` | `List[Str]` | [cite_start]避免提取相应的实体类型 [cite: 19, 20]。 |  |


### 2.2 批量导入 (`add-episode-bulk`)
[cite_start]适用于数据初始导入，即填充空图谱 [cite: 12]。

| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| `bulk-episodes` | `List[RawEpisode]` | [cite_start]批量导入的数据列表 [cite: 12]。 |


### 2.3 添加事实三元组 (`graphiti.add_triplet`)
手动向图谱添加由两个节点和一条边组成的事实三元组。

+ **机制**: `await graphiti.add_triplet(source_node, edge, target_node)`。
+ **去重**: Graphiti 会对传入的节点和边进行去重处理；无重复项时添加为新的。
+ **手动构造 Node/Edge 实例**：需确保已存在的节点使用现有 `uuid`，新节点创建新 `uuid`。

---

## ⚙️ 3. 数据操作：节点与边 (CRUD)
Graphiti 使用 8 个核心类来操作数据:

| 核心类 | 类型 | CRUD 支持 |
| :--- | :--- | :--- |
| `Node`, `Edge` | 抽象基类 | 无 |
| `EpisodicNode`, `EntityNode` | 继承自 `Node` | 完全支持 CRUD。 |
| `EpisodicEdge`, `EntityEdge` | 继承自 `Edge` | 完全支持 CRUD。 |
| `CommunityNode`, `CommunityEdge` | 核心类 | - |


### 3.1 创建与更新 (`save` 方法)
| 方法 | 描述 | 关键点 |
| :--- | :--- | :--- |
| `async def save(self, driver: AsyncDriver)` | 执行 **查找或创建 (find or create)** 操作，根据对象的 `uuid` 来添加或更新数据。 | **必须** 提供 `AsyncDriver` 驱动。使用 Neo4j 的 `MERGE` 语句实现。 |


### 3.2 读取 (`get_by_uuid` 方法)
| 方法 | 描述 | 关键点 |
| :--- | :--- | :--- |
| `async def get_by_uuid(cls, driver: AsyncDriver, uuid: str)` | 通过对象的 `uuid` 获取节点或边。 | **类方法**，必须使用类名而非实例调用。 |


### 3.3 删除 (`delete` 方法)
| 方法 | 描述 | 关键点 |
| :--- | :--- | :--- |
| `async def delete(self, driver: AsyncDriver)` | 执行节点和边的 **硬删除 (hard deleting)**。 | **必须** 提供 `AsyncDriver` 驱动。使用 Neo4j 的 `DETACH DELETE` 语句删除节点和关系。 |


---

## 🔎 4. 图谱搜索 (Searching the Graph)
### 4.1 搜索方法
| 方法 | 描述 | 原理 | 适用场景 |
| :--- | :--- | :--- | :--- |
| **Hybrid search** | [cite_start]`await graphiti.search(query)` [cite: 37] | [cite_start]检索结合语义相似度 (`semantic similarity`) 和 BM25 [cite: 38][cite_start]，使用 Reciprocal Rank Fusion (RRF) 重排 [cite: 39]。 | [cite_start]适合广泛探索 [cite: 36]。 |
| **Node distance Reranking** | [cite_start]`await graphiti.search(query,focal_node_uuid)` [cite: 42] | [cite_start]检索结合语义相似度和 BM25 [cite: 43][cite_start]，使用 `node_distance` 重排 [cite: 44]。 | [cite_start]适合针对特定实体信息的精准查询 [cite: 40]。 |


### 4.2 高级配置
+ [cite_start]**可配置策略**: 通过 `Graphiti._search()` 调用，并传入 `SearchConfig` 的额外配置参数 [cite: 45]。
+ [cite_start]**预设配置**: 在 `search_config-recipes.py` 中有 15 种预设配置方案 [cite: 46, 47]。
+ [cite_start]**命名空间查询**: 在执行查询时，可通过向 `Graphiti.search` 或 `Graphiti._search` 传入 `group.id` 实现仅在指定命名空间中查询 [cite: 32]。

### 4.3 支持的重排序方法
| 重排方法 | 描述 |
| :--- | :--- |
| **RRF** | [cite_start]Reciprocal Rank Fusion，更精准的检索 [cite: 49]。 |
| **MMR** | [cite_start]Maximal Marginal Relevance，搜索结果全面且多样 [cite: 50]。 |
| **Cross-Encoder** | [cite_start]交叉编码器，可同时编码查询内容和结果 [cite: 51][cite_start]，包括 `OpenAIRerankerClient` (默认) [cite: 52][cite_start]、`GeminiRerankerClient` [cite: 53][cite_start]、`BGERerankerClient` [cite: 54]。 |


