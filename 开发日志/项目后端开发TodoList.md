# 📋 项目后端开发 Todo List

本文档提供了完整的、分阶段的后端开发任务清单。每个阶段都是独立可交付的，建议按顺序开发。

---

## 🎯 开发原则

1. **迭代开发** - 每个阶段完成后都可以运行和测试
2. **测试驱动** - 每个功能都需要编写单元测试
3. **文档同步** - 更新API文档和使用说明
4. **代码审查** - 提交前自我审查代码质量

---

## 📦 阶段0：环境准备与基础设施（1-2天）

### ✅ 0.1 项目配置
- [ ] 创建`.env.example`文件，包含所有必需的环境变量
- [ ] 更新`requirements.txt`，添加缺失的依赖：
  - [ ] `arxiv`（arXiv API客户端）
  - [ ] `aiohttp`（异步HTTP客户端）
  - [ ] `PyMuPDF`或`pdfplumber`（PDF解析）
  - [ ] `sentence-transformers`（向量化）
  - [ ] `celery[redis]`（异步任务）
  - [ ] `sqlalchemy`（数据库ORM）
  - [ ] `alembic`（数据库迁移）
  - [ ] `python-multipart`（文件上传）
  - [ ] `langchain`（LLM编排，可选）
- [ ] 创建`docker-compose.yml`，包含：
  - [ ] FastAPI应用容器
  - [ ] Neo4j容器
  - [ ] Redis容器（Celery）
  - [ ] PostgreSQL容器（关系数据）

### ✅ 0.2 核心模块完善
- [ ] 完善`app/core/config.py`，添加新的配置项：
  ```python
  ARXIV_MAX_RESULTS: int = 10
  S2_API_KEY: Optional[str] = None
  OPENAI_API_KEY: str
  EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
  DATABASE_URL: str
  REDIS_URL: str = "redis://localhost:6379"
  ```
- [ ] 创建`app/core/logging.py`（统一日志配置）
- [ ] 创建`app/core/errors.py`（自定义异常类）
- [ ] 创建`app/core/constants.py`（常量定义）

### ✅ 0.3 数据库初始化
- [ ] 创建`scripts/init_db.py`（初始化关系数据库）
- [ ] 设计数据库Schema：
  - [ ] `users`表（用户信息）
  - [ ] `chat_history`表（聊天历史）
  - [ ] `paper_metadata`表（论文元数据缓存）
  - [ ] `user_reading_history`表（用户阅读历史）
  - [ ] `user_interests`表（用户兴趣标签）

### ✅ 0.4 测试框架
- [ ] 配置`pytest`
- [ ] 创建测试fixtures（mock Graphiti client、mock LLM等）
- [ ] 创建`tests/conftest.py`

**交付物**：
- ✅ 环境配置文件
- ✅ Docker容器可正常启动
- ✅ 数据库初始化完成
- ✅ 测试框架可运行

---

## 📦 阶段1：实体Schema与Graphiti增强（3-4天）

### ✅ 1.1 实体Schema定义
- [ ] 创建`app/schemas/entities.py`：
  - [ ] `PaperEntity`（论文）
  - [ ] `MethodEntity`（方法）
  - [ ] `TaskEntity`（任务）
  - [ ] `DatasetEntity`（数据集）
  - [ ] `MetricEntity`（指标）
  - [ ] `AuthorEntity`（作者）
  - [ ] `InstitutionEntity`（机构）
  - [ ] `ConceptEntity`（概念）

### ✅ 1.2 关系Schema定义
- [ ] 创建`app/schemas/relations.py`：
  - [ ] 定义关系类型枚举（PROPOSES、EVALUATES_ON、SOLVES等）
  - [ ] 定义关系属性Schema

### ✅ 1.3 Schema验证器
- [ ] 创建`app/schemas/validators.py`：
  - [ ] 实体类型验证
  - [ ] 关系类型验证
  - [ ] Schema演进工具

### ✅ 1.4 Graphiti Client增强
- [ ] 完善`app/core/graphiti_client.py`：
  - [ ] 添加`add_episode_with_schema`方法（支持自定义Schema）
  - [ ] 添加`add_triplet`方法（手动添加三元组）
  - [ ] 添加`get_node_neighbors`方法（获取邻居节点）
  - [ ] 添加`search_with_config`方法（高级搜索配置）
  - [ ] 添加`build_communities`方法（社区检测）
  - [ ] 添加错误处理和重试机制

### ✅ 1.5 测试
- [ ] 创建`tests/test_schemas.py`（测试Schema定义）
- [ ] 创建`tests/test_graphiti_client.py`（测试Graphiti操作）

**交付物**：
- ✅ 完整的实体和关系Schema
- ✅ 增强的Graphiti客户端
- ✅ Schema验证通过测试

---

## 📦 阶段2：Namespace管理与双图谱架构（2-3天）

### ✅ 2.1 Namespace服务
- [ ] 创建`app/services/namespace_service.py`：
  - [ ] `get_user_namespace(user_id)` - 获取用户命名空间
  - [ ] `get_global_namespace()` - 获取全局命名空间
  - [ ] `search_with_fallback(query, user_id)` - 多层级搜索
  - [ ] `merge_results(user_results, global_results)` - 结果聚合

### ✅ 2.2 图谱服务增强
- [ ] 完善`app/services/graph_service.py`：
  - [ ] 集成namespace_service
  - [ ] 添加`search_user_graph(query, user_id)`
  - [ ] 添加`search_global_graph(query)`
  - [ ] 添加`search_with_reranking(query, focal_node_uuid)`
  - [ ] 添加`get_node_by_uuid(uuid)`
  - [ ] 添加`get_neighbors(node_uuid, hops=1)`
  - [ ] 添加`find_path(source_uuid, target_uuid)`

### ✅ 2.3 图谱模型完善
- [ ] 完善`app/models/graph_models.py`：
  - [ ] `GraphSearchRequest`（搜索请求）
  - [ ] `GraphSearchResponse`（搜索响应）
  - [ ] `NodeResponse`（节点响应）
  - [ ] `PathResponse`（路径响应）
  - [ ] `NeighborsResponse`（邻居响应）

### ✅ 2.4 图谱API增强
- [ ] 完善`app/api/routes/graph.py`：
  - [ ] `POST /graph/search` - 混合搜索
  - [ ] `GET /graph/node/{uuid}` - 获取节点
  - [ ] `GET /graph/node/{uuid}/neighbors` - 获取邻居
  - [ ] `POST /graph/path` - 查找路径
  - [ ] `POST /graph/search/user` - 用户图谱搜索
  - [ ] `POST /graph/search/global` - 全局图谱搜索

### ✅ 2.5 测试
- [ ] 创建`tests/test_namespace.py`
- [ ] 创建`tests/test_graph_service.py`

**交付物**：
- ✅ 双图谱架构运行正常
- ✅ Namespace隔离验证
- ✅ 图谱搜索API完整

---

## 📦 阶段3：PDF解析与图谱摄入Pipeline（4-5天）

### ✅ 3.1 PDF解析器完善
- [ ] 完善`app/services/pdf_parser.py`：
  - [ ] `extract_text(pdf_bytes)` - 提取文本
  - [ ] `extract_sections(pdf_bytes)` - 提取章节
  - [ ] `extract_metadata(pdf_bytes)` - 提取元数据（标题、作者等）
  - [ ] `extract_references(pdf_bytes)` - 提取参考文献
  - [ ] 支持多种PDF格式（学术论文特化）

### ✅ 3.2 文本分块器
- [ ] 完善`app/utils/text_splitter.py`：
  - [ ] `split_by_section(text)` - 按章节分块
  - [ ] `split_by_paragraph(text, max_tokens)` - 按段落分块
  - [ ] `smart_split(text)` - 智能分块（保留语义完整性）

### ✅ 3.3 实体抽取
- [ ] 创建`app/services/entity_extraction_service.py`：
  - [ ] `extract_entities_from_text(text)` - LLM抽取实体
  - [ ] `extract_relations_from_text(text)` - LLM抽取关系
  - [ ] `normalize_entity(entity)` - 实体归一化
  - [ ] `deduplicate_entities(entities)` - 实体去重
  - [ ] 使用自定义Schema提示LLM

### ✅ 3.4 图谱摄入服务
- [ ] 完善`app/services/ingest_service.py`：
  - [ ] `ingest_pdf(file, user_id, to_global=True)` - PDF摄入主流程
  - [ ] `build_episodes(sections)` - 构建Episode列表
  - [ ] `add_episodes_to_graph(episodes, group_id)` - 批量添加Episode
  - [ ] `add_entities_to_graph(entities, group_id)` - 添加实体
  - [ ] `add_relations_to_graph(relations, group_id)` - 添加关系
  - [ ] `generate_paper_summary(paper_text)` - 生成论文摘要

### ✅ 3.5 论文模型完善
- [ ] 完善`app/models/paper_models.py`：
  - [ ] `PaperMetadata`（论文元数据）
  - [ ] `PaperSection`（论文章节）
  - [ ] `PaperUploadRequest`（上传请求）
  - [ ] `PaperUploadResponse`（上传响应）
  - [ ] `PaperSummary`（论文摘要）

### ✅ 3.6 论文API完善
- [ ] 完善`app/api/routes/papers.py`：
  - [ ] `POST /papers/upload` - 上传PDF
  - [ ] `GET /papers/{paper_id}` - 获取论文详情
  - [ ] `GET /papers/{paper_id}/summary` - 获取论文摘要
  - [ ] `GET /papers/{paper_id}/entities` - 获取论文相关实体
  - [ ] `GET /papers/{paper_id}/relations` - 获取论文相关关系
  - [ ] `POST /papers/search` - 搜索论文

### ✅ 3.7 异步任务
- [ ] 完善`app/tasks/ingest_tasks.py`：
  - [ ] `ingest_pdf_task(file_path, user_id)` - 异步摄入任务
  - [ ] `process_batch_papers(paper_list)` - 批量处理任务

### ✅ 3.8 测试
- [ ] 创建`tests/test_pdf_parser.py`
- [ ] 创建`tests/test_ingest_service.py`
- [ ] 创建`tests/test_entity_extraction.py`
- [ ] 准备测试用PDF文件

**交付物**：
- ✅ 完整的PDF摄入Pipeline
- ✅ 论文上传API可用
- ✅ 实体和关系正确抽取

---

## 📦 阶段4：外部搜索集成（3-4天）

### ✅ 4.1 arXiv集成
- [ ] 创建`app/integrations/arxiv_client.py`：
  - [ ] `search(query, max_results)` - 搜索论文
  - [ ] `download_pdf(arxiv_id)` - 下载PDF
  - [ ] `get_paper_metadata(arxiv_id)` - 获取元数据
  - [ ] 错误处理和速率限制

### ✅ 4.2 Semantic Scholar集成
- [ ] 创建`app/integrations/semantic_scholar_client.py`：
  - [ ] `search(query, max_results)` - 搜索论文
  - [ ] `get_paper_details(paper_id)` - 获取论文详情
  - [ ] `get_citations(paper_id)` - 获取引用信息
  - [ ] `get_references(paper_id)` - 获取参考文献

### ✅ 4.3 外部搜索服务
- [ ] 创建`app/services/external_search_service.py`：
  - [ ] `search(query, source="arxiv")` - 外部搜索
  - [ ] `search_and_ingest(query, user_id)` - 搜索并自动摄入
  - [ ] `download_and_ingest_paper(paper_id, user_id)` - 下载并摄入
  - [ ] `batch_ingest_from_search(query)` - 批量摄入

### ✅ 4.4 搜索服务增强
- [ ] 完善`app/services/search_service.py`：
  - [ ] 集成外部搜索
  - [ ] `search_with_fallback(query, user_id)` - 带fallback的搜索
  - [ ] 搜索结果聚合和排序

### ✅ 4.5 测试
- [ ] 创建`tests/test_arxiv_client.py`
- [ ] 创建`tests/test_semantic_scholar_client.py`
- [ ] 创建`tests/test_external_search.py`

**交付物**：
- ✅ 外部搜索正常工作
- ✅ 自动摄入机制验证
- ✅ API限流和错误处理完善

---

## 📦 阶段5：Community管理（2-3天）

### ✅ 5.1 Community服务
- [ ] 创建`app/services/community_service.py`：
  - [ ] `detect_communities(group_id)` - 社区检测
  - [ ] `get_communities(group_id)` - 获取社区列表
  - [ ] `get_community_details(community_id)` - 获取社区详情
  - [ ] `get_community_nodes(community_id)` - 获取社区节点
  - [ ] `update_communities(group_id)` - 更新社区

### ✅ 5.2 Community模型
- [ ] 创建`app/models/community_models.py`：
  - [ ] `Community`（社区信息）
  - [ ] `CommunityNode`（社区节点）
  - [ ] `CommunityListResponse`（社区列表响应）

### ✅ 5.3 Community API
- [ ] 创建`app/api/routes/communities.py`：
  - [ ] `POST /communities/detect` - 触发社区检测
  - [ ] `GET /communities` - 获取社区列表
  - [ ] `GET /communities/{community_id}` - 获取社区详情
  - [ ] `GET /communities/user/{user_id}` - 获取用户社区

### ✅ 5.4 异步任务
- [ ] 创建`app/tasks/community_tasks.py`：
  - [ ] `detect_communities_task(group_id)` - 异步社区检测
  - [ ] `rebuild_all_communities()` - 重建所有社区

### ✅ 5.5 测试
- [ ] 创建`tests/test_community_service.py`

**交付物**：
- ✅ 社区检测功能
- ✅ Community API完整
- ✅ 异步任务正常运行

---

## 📦 阶段6：用户画像与个性化（3-4天）

### ✅ 6.1 用户服务
- [ ] 创建`app/services/user_profile_service.py`：
  - [ ] `create_user_profile(user_id)` - 创建用户画像
  - [ ] `update_reading_history(user_id, paper_id)` - 更新阅读历史
  - [ ] `get_user_interests(user_id)` - 获取用户兴趣
  - [ ] `analyze_research_direction(user_id)` - 分析研究方向
  - [ ] `build_user_communities(user_id)` - 构建用户社区
  - [ ] `get_user_embedding(user_id)` - 获取用户兴趣向量

### ✅ 6.2 历史服务
- [ ] 创建`app/services/history_service.py`：
  - [ ] `save_chat_message(user_id, message, response)` - 保存聊天
  - [ ] `get_chat_history(user_id, limit)` - 获取聊天历史
  - [ ] `get_reading_history(user_id, limit)` - 获取阅读历史
  - [ ] `clear_history(user_id)` - 清空历史

### ✅ 6.3 用户模型
- [ ] 创建`app/models/user_models.py`：
  - [ ] `UserProfile`（用户画像）
  - [ ] `UserInterest`（用户兴趣）
  - [ ] `ResearchDirection`（研究方向）

### ✅ 6.4 历史模型
- [ ] 创建`app/models/history_models.py`：
  - [ ] `ChatMessage`（聊天消息）
  - [ ] `ChatHistory`（聊天历史）
  - [ ] `ReadingHistory`（阅读历史）

### ✅ 6.5 用户API
- [ ] 创建`app/api/routes/users.py`：
  - [ ] `GET /users/{user_id}/profile` - 获取用户画像
  - [ ] `GET /users/{user_id}/interests` - 获取用户兴趣
  - [ ] `GET /users/{user_id}/direction` - 获取研究方向
  - [ ] `POST /users/{user_id}/reading` - 记录阅读

### ✅ 6.6 历史API
- [ ] 创建`app/api/routes/history.py`：
  - [ ] `GET /history/chat/{user_id}` - 获取聊天历史
  - [ ] `GET /history/reading/{user_id}` - 获取阅读历史
  - [ ] `DELETE /history/{user_id}` - 清空历史

### ✅ 6.7 异步任务
- [ ] 创建`app/tasks/profile_update_tasks.py`：
  - [ ] `update_user_profile_task(user_id)` - 更新用户画像
  - [ ] `analyze_user_direction_task(user_id)` - 分析研究方向

### ✅ 6.8 测试
- [ ] 创建`tests/test_user_profile.py`
- [ ] 创建`tests/test_history.py`

**交付物**：
- ✅ 用户画像系统
- ✅ 历史记录功能
- ✅ 个性化基础设施

---

## 📦 阶段7：Agent工具系统（4-5天）

### ✅ 7.1 Tool基础框架
- [ ] 创建`app/tools/base.py`：
  - [ ] `ToolInput`（工具输入基类）
  - [ ] `ToolOutput`（工具输出基类）
  - [ ] `BaseTool`（工具基类）
  - [ ] `ToolRegistry`（工具注册器）

### ✅ 7.2 图谱查询工具
- [ ] 创建`app/tools/graph_query_tool.py`：
  - [ ] `GraphQueryTool.execute(query, user_id)` - 图谱查询
  - [ ] 支持hybrid search和node distance reranking

### ✅ 7.3 外部搜索工具
- [ ] 创建`app/tools/external_search_tool.py`：
  - [ ] `ExternalSearchTool.execute(query)` - 外部搜索
  - [ ] 自动触发摄入

### ✅ 7.4 PDF解析工具
- [ ] 创建`app/tools/pdf_parse_tool.py`：
  - [ ] `PDFParseTool.execute(pdf_file, user_id)` - PDF解析

### ✅ 7.5 论文对比工具
- [ ] 创建`app/tools/paper_compare_tool.py`：
  - [ ] `PaperCompareTool.execute(paper_ids)` - 论文对比

### ✅ 7.6 社区查询工具
- [ ] 创建`app/tools/community_query_tool.py`：
  - [ ] `CommunityQueryTool.execute(user_id)` - 社区查询

### ✅ 7.7 用户画像工具
- [ ] 创建`app/tools/user_profile_tool.py`：
  - [ ] `UserProfileTool.execute(user_id)` - 用户画像查询

### ✅ 7.8 工具注册器
- [ ] 创建`app/tools/tool_registry.py`：
  - [ ] 注册所有工具
  - [ ] `get_tool(tool_name)`
  - [ ] `list_tools()`

### ✅ 7.9 测试
- [ ] 创建`tests/test_tools.py`

**交付物**：
- ✅ 完整的工具系统
- ✅ 所有工具可独立调用
- ✅ 工具注册器正常工作

---

## 📦 阶段8：Agent核心逻辑（5-6天）

### ✅ 8.1 LLM客户端封装
- [ ] 创建`app/integrations/llm_client.py`：
  - [ ] `LLMClient.chat(messages)` - 基础对话
  - [ ] `LLMClient.chat_with_tools(messages, tools)` - 工具调用
  - [ ] `LLMClient.extract_entities(text)` - 实体抽取
  - [ ] 支持多种LLM（OpenAI、Anthropic、Local）

### ✅ 8.2 Agent服务核心
- [ ] 完善`app/services/agent_service.py`：
  - [ ] `chat(user_id, message)` - 主对话流程
  - [ ] `understand_query(message)` - 理解用户意图
  - [ ] `select_tools(intent)` - 选择工具
  - [ ] `execute_tools(tools, context)` - 执行工具
  - [ ] `aggregate_context(tool_results)` - 聚合上下文
  - [ ] `generate_response(context, query)` - 生成回答
  - [ ] `cite_sources(response, facts)` - 标注引用

### ✅ 8.3 对话上下文管理
- [ ] 创建`app/services/context_service.py`：
  - [ ] `build_context(user_id, query)` - 构建对话上下文
  - [ ] `add_graph_context(context, search_results)` - 添加图谱上下文
  - [ ] `add_history_context(context, history)` - 添加历史上下文
  - [ ] `add_user_profile_context(context, profile)` - 添加画像上下文

### ✅ 8.4 Agent Prompt工程
- [ ] 创建`app/prompts/`目录：
  - [ ] `system_prompt.py` - 系统提示词
  - [ ] `query_understanding_prompt.py` - 意图理解提示
  - [ ] `tool_selection_prompt.py` - 工具选择提示
  - [ ] `response_generation_prompt.py` - 回答生成提示

### ✅ 8.5 聊天模型完善
- [ ] 完善`app/models/chat_models.py`：
  - [ ] `ChatRequest`（聊天请求）
  - [ ] `ChatResponse`（聊天响应）
  - [ ] `ToolCall`（工具调用）
  - [ ] `Citation`（引用）

### ✅ 8.6 聊天API完善
- [ ] 完善`app/api/routes/chat.py`：
  - [ ] `POST /chat` - 主对话接口
  - [ ] `POST /chat/stream` - 流式对话接口
  - [ ] `GET /chat/{session_id}` - 获取会话历史

### ✅ 8.7 测试
- [ ] 创建`tests/test_agent_service.py`
- [ ] 创建`tests/test_context_service.py`
- [ ] 端到端测试：用户提问 → Agent回答

**交付物**：
- ✅ 完整的Agent对话系统
- ✅ 工具调用正常
- ✅ 引用标注清晰

---

## 📦 阶段9：推荐系统（3-4天）

### ✅ 9.1 论文对比服务
- [ ] 创建`app/services/comparison_service.py`：
  - [ ] `compare_papers(paper_ids)` - 对比论文
  - [ ] `find_paper_relations(paper1_id, paper2_id)` - 查找论文关系
  - [ ] `compare_methods(method_ids)` - 对比方法

### ✅ 9.2 推荐服务
- [ ] 创建`app/services/recommendation_service.py`：
  - [ ] `recommend_papers(user_id, n=10)` - 推荐论文
  - [ ] `recommend_research_directions(user_id)` - 推荐研究方向
  - [ ] `recommend_related_papers(paper_id, n=5)` - 推荐相关论文
  - [ ] `trending_topics()` - 热门话题

### ✅ 9.3 推荐模型
- [ ] 创建`app/models/recommendation_models.py`：
  - [ ] `PaperRecommendation`（论文推荐）
  - [ ] `DirectionRecommendation`（方向推荐）
  - [ ] `TrendingTopic`（热门话题）

### ✅ 9.4 推荐API
- [ ] 创建`app/api/routes/recommendations.py`：
  - [ ] `GET /recommendations/papers/{user_id}` - 论文推荐
  - [ ] `GET /recommendations/directions/{user_id}` - 方向推荐
  - [ ] `GET /recommendations/related/{paper_id}` - 相关论文
  - [ ] `GET /recommendations/trending` - 热门话题
  - [ ] `POST /papers/compare` - 论文对比

### ✅ 9.5 测试
- [ ] 创建`tests/test_comparison.py`
- [ ] 创建`tests/test_recommendation.py`

**交付物**：
- ✅ 论文对比功能
- ✅ 推荐系统运行
- ✅ 推荐API完整

---

## 📦 阶段10：可视化支持（2-3天）

### ✅ 10.1 可视化服务
- [ ] 创建`app/services/visualization_service.py`：
  - [ ] `export_graph_data(group_id, format="json")` - 导出图谱数据
  - [ ] `get_community_graph(community_id)` - 获取社区图
  - [ ] `get_paper_relations_graph(paper_id)` - 获取论文关系图
  - [ ] `get_user_knowledge_graph(user_id)` - 获取用户知识图

### ✅ 10.2 可视化API
- [ ] 创建`app/api/routes/visualization.py`：
  - [ ] `GET /visualization/graph/user/{user_id}` - 用户图谱数据
  - [ ] `GET /visualization/graph/global` - 全局图谱数据
  - [ ] `GET /visualization/community/{community_id}` - 社区图数据
  - [ ] `GET /visualization/paper/{paper_id}` - 论文关系图数据

### ✅ 10.3 数据格式
- [ ] 支持多种可视化格式：
  - [ ] JSON（D3.js格式）
  - [ ] Cytoscape格式
  - [ ] GraphML格式

### ✅ 10.4 测试
- [ ] 创建`tests/test_visualization.py`

**交付物**：
- ✅ 可视化数据导出
- ✅ 多种格式支持
- ✅ 可视化API完整

---

## 📦 阶段11：定时任务与维护（2-3天）

### ✅ 11.1 arXiv同步任务
- [ ] 创建`app/tasks/arxiv_sync_tasks.py`：
  - [ ] `sync_latest_papers(categories)` - 同步最新论文
  - [ ] `daily_arxiv_update()` - 每日更新
  - [ ] 配置Celery Beat定时任务

### ✅ 11.2 社区重建任务
- [ ] 完善`app/tasks/community_tasks.py`：
  - [ ] `rebuild_all_communities()` - 重建所有社区
  - [ ] 定时执行（每周）

### ✅ 11.3 维护脚本
- [ ] 创建`scripts/rebuild_communities.py` - 手动重建社区
- [ ] 创建`scripts/migrate_schema.py` - Schema迁移
- [ ] 创建`scripts/backup_graph.py` - 图谱备份

### ✅ 11.4 监控和日志
- [ ] 完善`app/core/logging.py`：
  - [ ] 结构化日志
  - [ ] 性能监控
  - [ ] 错误追踪

### ✅ 11.5 测试
- [ ] 创建`tests/test_tasks.py`

**交付物**：
- ✅ 定时任务运行正常
- ✅ 维护脚本可用
- ✅ 监控和日志完善

---

## 📦 阶段12：工具类与辅助功能（2天）

### ✅ 12.1 Embedding工具
- [ ] 创建`app/utils/embedding_utils.py`：
  - [ ] `generate_embedding(text)` - 生成向量
  - [ ] `compute_similarity(emb1, emb2)` - 计算相似度
  - [ ] `batch_embeddings(texts)` - 批量向量化

### ✅ 12.2 图谱工具
- [ ] 创建`app/utils/graph_utils.py`：
  - [ ] `merge_duplicate_nodes(node_list)` - 节点去重
  - [ ] `normalize_entity_name(name)` - 实体名称归一化
  - [ ] `validate_graph_structure(graph)` - 图结构验证

### ✅ 12.3 文件工具
- [ ] 创建`app/utils/file_utils.py`：
  - [ ] `save_upload_file(file)` - 保存上传文件
  - [ ] `cleanup_temp_files()` - 清理临时文件
  - [ ] `get_file_hash(file)` - 文件hash

### ✅ 12.4 时间工具
- [ ] 创建`app/utils/time_utils.py`：
  - [ ] `parse_paper_date(date_str)` - 解析论文日期
  - [ ] `format_datetime(dt)` - 格式化时间
  - [ ] `get_time_range(period)` - 获取时间范围

### ✅ 12.5 测试
- [ ] 创建`tests/test_utils.py`

**交付物**：
- ✅ 工具函数完善
- ✅ 代码复用性提升

---

## 📦 阶段13：集成测试与优化（3-4天）

### ✅ 13.1 端到端测试
- [ ] 测试完整用户流程：
  - [ ] 用户提问 → 图谱搜索 → 外部搜索 → 回答
  - [ ] 上传PDF → 解析 → 摄入 → 查询
  - [ ] 用户画像 → 推荐 → 对比

### ✅ 13.2 性能测试
- [ ] 图谱搜索性能
- [ ] PDF摄入速度
- [ ] 并发请求处理
- [ ] 数据库查询优化

### ✅ 13.3 压力测试
- [ ] 大规模图谱测试（10k+ 节点）
- [ ] 多用户并发测试
- [ ] 长时间运行稳定性

### ✅ 13.4 Bug修复
- [ ] 修复测试中发现的bug
- [ ] 完善错误处理
- [ ] 优化异常捕获

### ✅ 13.5 代码优化
- [ ] 代码重构
- [ ] 性能优化
- [ ] 内存优化

**交付物**：
- ✅ 系统稳定运行
- ✅ 性能达标
- ✅ 主要bug修复

---

## 📦 阶段14：文档与部署（2-3天）

### ✅ 14.1 API文档
- [ ] 完善OpenAPI文档
- [ ] 编写API使用示例
- [ ] 创建Postman collection

### ✅ 14.2 开发文档
- [ ] 编写`README.md`
- [ ] 编写`CONTRIBUTING.md`
- [ ] 编写架构说明文档
- [ ] 编写部署指南

### ✅ 14.3 用户文档
- [ ] 编写用户使用指南
- [ ] 编写常见问题FAQ
- [ ] 编写功能演示视频

### ✅ 14.4 Docker部署
- [ ] 优化Dockerfile
- [ ] 优化docker-compose.yml
- [ ] 编写部署脚本

### ✅ 14.5 CI/CD
- [ ] 配置GitHub Actions
- [ ] 自动化测试
- [ ] 自动化部署

**交付物**：
- ✅ 完整的文档
- ✅ 部署方案
- ✅ CI/CD流程

---

## 🎉 最终检查清单

在完成所有阶段后，确认以下内容：

### 功能完整性
- [ ] ✅ A1. 学术问答
- [ ] ✅ A2. 论文查询与阅读辅助
- [ ] ✅ A3. 用户个性化科研记忆
- [ ] ✅ A4. 论文上传解析
- [ ] ✅ A5. 外部论文搜索
- [ ] ✅ A6. 图谱可视化（数据支持）
- [ ] ✅ A7. 聊天与任务历史

### 系统质量
- [ ] ✅ 所有单元测试通过
- [ ] ✅ 集成测试通过
- [ ] ✅ API文档完整
- [ ] ✅ 性能指标达标
- [ ] ✅ 错误处理完善
- [ ] ✅ 日志记录完整

### 部署准备
- [ ] ✅ Docker镜像构建成功
- [ ] ✅ 环境变量配置清晰
- [ ] ✅ 数据库迁移脚本准备
- [ ] ✅ 部署文档完整

---

## 📊 预估时间线

| 阶段 | 名称 | 预估时间 | 累计时间 |
|-----|------|---------|---------|
| 0 | 环境准备 | 1-2天 | 2天 |
| 1 | Schema定义 | 3-4天 | 6天 |
| 2 | 双图谱架构 | 2-3天 | 9天 |
| 3 | PDF摄入Pipeline | 4-5天 | 14天 |
| 4 | 外部搜索集成 | 3-4天 | 18天 |
| 5 | Community管理 | 2-3天 | 21天 |
| 6 | 用户画像 | 3-4天 | 25天 |
| 7 | Agent工具系统 | 4-5天 | 30天 |
| 8 | Agent核心逻辑 | 5-6天 | 36天 |
| 9 | 推荐系统 | 3-4天 | 40天 |
| 10 | 可视化支持 | 2-3天 | 43天 |
| 11 | 定时任务 | 2-3天 | 46天 |
| 12 | 工具类 | 2天 | 48天 |
| 13 | 集成测试 | 3-4天 | 52天 |
| 14 | 文档与部署 | 2-3天 | 55天 |

**总预估时间：50-55天（约2个月）**

---

## 🚀 快速启动建议

如果时间紧迫，可以采用以下MVP（最小可行产品）策略：

### MVP核心功能（前5周）
1. 阶段0-1：环境和Schema（1周）
2. 阶段2-3：双图谱 + PDF摄入（2周）
3. 阶段7-8：Agent系统（2周）

**MVP交付物**：
- 用户可以上传PDF
- Agent可以回答问题
- 图谱正常工作

### 增强功能（后3周）
4. 阶段4-5：外部搜索 + Community（1.5周）
5. 阶段6：用户画像（1周）
6. 阶段9-10：推荐和可视化（1.5周）

---

## 📝 开发建议

1. **每天提交代码** - 保持小步快跑
2. **先写测试** - TDD能提高代码质量
3. **及时文档** - 边开发边写文档
4. **代码审查** - 定期review代码
5. **性能监控** - 关注关键指标
6. **用户反馈** - 尽早获取反馈

祝开发顺利！🎉

