// ============================================================
// Neo4j图数据库初始化脚本
// 项目：学术研究知识图谱系统
// 版本：v1.0
// 创建日期：2025-12-11
// ============================================================

// 1. 清理旧约束和索引（可选，首次运行不需要）
// ============================================================

// 删除旧约束
// DROP CONSTRAINT entity_uuid IF EXISTS;
// DROP CONSTRAINT episode_uuid IF EXISTS;
// DROP CONSTRAINT community_uuid IF EXISTS;

// 删除旧索引
// DROP INDEX node_group_id IF EXISTS;
// DROP INDEX episode_group_id IF EXISTS;
// DROP INDEX community_group_id IF EXISTS;
// DROP INDEX entity_name_fulltext IF EXISTS;

// 2. 创建约束（确保数据唯一性）
// ============================================================

// 2.1 EntityNode的uuid唯一约束
CREATE CONSTRAINT entity_uuid IF NOT EXISTS
FOR (n:EntityNode) 
REQUIRE n.uuid IS UNIQUE;

// 2.2 EpisodicNode的uuid唯一约束
CREATE CONSTRAINT episode_uuid IF NOT EXISTS
FOR (n:EpisodicNode) 
REQUIRE n.uuid IS UNIQUE;

// 2.3 CommunityNode的uuid唯一约束
CREATE CONSTRAINT community_uuid IF NOT EXISTS
FOR (n:CommunityNode) 
REQUIRE n.uuid IS UNIQUE;

// 3. 创建索引（优化查询性能）
// ============================================================

// 3.1 为group_id创建索引（命名空间查询，最重要！）
CREATE INDEX node_group_id IF NOT EXISTS
FOR (n:EntityNode) 
ON (n.group_id);

CREATE INDEX episode_group_id IF NOT EXISTS
FOR (n:EpisodicNode) 
ON (n.group_id);

CREATE INDEX community_group_id IF NOT EXISTS
FOR (n:CommunityNode) 
ON (n.group_id);

// 3.2 为name创建索引（快速查找）
CREATE INDEX entity_name IF NOT EXISTS
FOR (n:EntityNode) 
ON (n.name);

CREATE INDEX episode_name IF NOT EXISTS
FOR (n:EpisodicNode) 
ON (n.name);

// 3.3 为domain创建索引（领域过滤）
CREATE INDEX entity_domain IF NOT EXISTS
FOR (n:EntityNode) 
ON (n.domain);

// 3.4 为created_at创建索引（时间范围查询）
CREATE INDEX entity_created IF NOT EXISTS
FOR (n:EntityNode) 
ON (n.created_at);

CREATE INDEX episode_created IF NOT EXISTS
FOR (n:EpisodicNode) 
ON (n.created_at);

// 3.5 复合索引（group_id + domain，高频组合查询）
CREATE INDEX entity_group_domain IF NOT EXISTS
FOR (n:EntityNode) 
ON (n.group_id, n.domain);

// 4. 创建全文索引（支持文本搜索）
// ============================================================

// 4.1 实体名称和摘要全文索引
CREATE FULLTEXT INDEX entity_name_fulltext IF NOT EXISTS
FOR (n:EntityNode) 
ON EACH [n.name, n.summary];

// 4.2 Episode内容全文索引
CREATE FULLTEXT INDEX episode_content_fulltext IF NOT EXISTS
FOR (n:EpisodicNode) 
ON EACH [n.content];

// 5. 验证约束和索引
// ============================================================

// 查看所有约束
SHOW CONSTRAINTS;

// 查看所有索引
SHOW INDEXES;

// 6. 创建示例数据（可选，用于测试）
// ============================================================

/*
// 6.1 创建测试用户的命名空间（示例）
CREATE (user:EntityNode {
    uuid: 'user_test_namespace',
    name: 'Test User Namespace',
    group_id: '550e8400-e29b-41d4-a716-446655440000',
    domain: 'System',
    created_at: datetime()
});

// 6.2 创建测试实体节点
CREATE (ai:EntityNode {
    uuid: 'entity_ai_001',
    name: 'Artificial Intelligence',
    group_id: '550e8400-e29b-41d4-a716-446655440000',
    domain: 'AI',
    summary: 'AI是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。',
    entity_type: 'concept',
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (ml:EntityNode {
    uuid: 'entity_ml_001',
    name: 'Machine Learning',
    group_id: '550e8400-e29b-41d4-a716-446655440000',
    domain: 'AI',
    summary: 'Machine Learning是AI的子领域，专注于让计算机系统从数据中学习和改进。',
    entity_type: 'concept',
    created_at: datetime(),
    updated_at: datetime()
});

// 6.3 创建测试关系
CREATE (ai)-[:CONTAINS {
    uuid: 'edge_001',
    relationship_type: 'CONTAINS',
    fact: 'AI包含Machine Learning作为其子领域',
    weight: 0.95,
    created_at: datetime()
}]->(ml);

// 6.4 创建测试Episode
CREATE (ep:EpisodicNode {
    uuid: 'episode_001',
    name: 'user_query_1234567890',
    group_id: '550e8400-e29b-41d4-a716-446655440000',
    content: '用户询问：什么是Machine Learning？',
    source_type: 'message',
    source_description: 'User query in research session',
    created_at: datetime()
});

// 6.5 连接Episode到实体
CREATE (ep)-[:MENTIONS {
    uuid: 'edge_002',
    created_at: datetime()
}]->(ml);
*/

// 7. 常用查询示例
// ============================================================

// 7.1 查询指定用户的所有实体节点
// MATCH (n:EntityNode)
// WHERE n.group_id = '550e8400-e29b-41d4-a716-446655440000'
// RETURN n
// LIMIT 100;

// 7.2 查询指定用户的所有Episode节点
// MATCH (n:EpisodicNode)
// WHERE n.group_id = '550e8400-e29b-41d4-a716-446655440000'
// RETURN n
// ORDER BY n.created_at DESC
// LIMIT 50;

// 7.3 查询指定Domain的实体
// MATCH (n:EntityNode)
// WHERE n.group_id = '550e8400-e29b-41d4-a716-446655440000'
//   AND n.domain = 'AI'
// RETURN n
// LIMIT 100;

// 7.4 查询节点的邻居
// MATCH (source:EntityNode {uuid: 'entity_ai_001'})-[r]-(neighbor)
// WHERE neighbor.group_id = '550e8400-e29b-41d4-a716-446655440000'
// RETURN source, r, neighbor
// LIMIT 50;

// 7.5 统计用户的图谱规模
// MATCH (n)
// WHERE n.group_id = '550e8400-e29b-41d4-a716-446655440000'
// RETURN 
//   labels(n)[0] as node_type,
//   count(n) as count
// ORDER BY count DESC;

// 7.6 查询实体的来源Episodes
// MATCH (entity:EntityNode {uuid: 'entity_ml_001'})
//       <-[:MENTIONS]-(episode:EpisodicNode)
// WHERE episode.group_id = '550e8400-e29b-41d4-a716-446655440000'
// RETURN episode
// ORDER BY episode.created_at DESC
// LIMIT 10;

// 8. 性能优化建议
// ============================================================

/*
性能优化要点：

1. 始终使用group_id过滤
   - 所有查询必须包含 WHERE n.group_id = $user_id
   - 确保命名空间隔离和查询性能

2. 使用LIMIT限制返回数量
   - 避免返回过多节点导致前端渲染卡顿
   - 建议最多返回1000个节点

3. 使用EXPLAIN分析查询计划
   - EXPLAIN MATCH (n) WHERE n.group_id = $user_id RETURN n;
   - 确保索引被正确使用

4. 避免全图遍历
   - 不要使用 MATCH (n) RETURN n; （没有WHERE条件）
   - 始终从特定节点或条件开始查询

5. 定期维护
   - 定期运行 CALL db.stats.clear(); 清理统计信息
   - 监控慢查询日志
*/

// 9. 数据完整性检查
// ============================================================

// 9.1 检查孤立节点（没有任何关系的节点）
// MATCH (n)
// WHERE NOT (n)-[]-()
// RETURN labels(n)[0] as type, count(n) as orphan_count;

// 9.2 检查没有group_id的节点（数据错误）
// MATCH (n)
// WHERE n.group_id IS NULL
// RETURN labels(n), n.uuid, n.name
// LIMIT 10;

// 9.3 检查重复的uuid（应该为0）
// MATCH (n)
// WITH n.uuid as uuid, count(*) as cnt
// WHERE cnt > 1
// RETURN uuid, cnt;

// ============================================================
// 初始化完成
// ============================================================

// 返回摘要信息
CALL db.labels() YIELD label
RETURN 'Neo4j初始化完成！' as status, 
       label, 
       size((label)-->()) as node_count;

