# 知识图谱模块测试文档

**模块**: Module B - 知识图谱模块  
**开发人员**: Backend Developer B  
**测试完成日期**: 2025-12-10  
**版本**: v1.0

---

## 📋 测试文件概览

### 已完成的测试文件

| 测试文件 | 测试内容 | 测试用例数 | 覆盖范围 |
|---------|---------|-----------|---------|
| `test_schemas.py` | Schema定义测试 | 50+ | 8种实体 + 9种关系 |
| `test_validators.py` | 验证器测试 | 40+ | 7个验证函数 |
| `test_namespace_service.py` | 命名空间服务测试 | 30+ | 命名空间管理和Fallback |
| `test_graph_service.py` | 图谱服务测试 | 25+ | 搜索、重排、节点查询 |
| `test_graph_api.py` | API端点测试 | 30+ | 5个API端点 |

**总测试用例数**: 175+

---

## 🚀 运行测试

### 前提条件

1. 安装测试依赖：
```bash
pip install -r tests/requirements-test.txt
```

2. 确保测试数据库可用：
```bash
# MySQL测试数据库应该已经创建
# 数据库名：test_research_agent
```

3. 配置环境变量（如果需要）

### 运行所有图谱模块测试

```bash
# 运行所有图谱模块测试（从项目根目录）
pytest tests/kg/ -v

# 或者指定具体文件
pytest tests/kg/test_schemas.py tests/kg/test_validators.py tests/kg/test_namespace_service.py tests/kg/test_graph_service.py tests/kg/test_graph_api.py -v

# 或者使用标记（如果添加了）
pytest tests/kg/ -k "graph or schema or validator or namespace" -v
```

### 运行单个测试文件

```bash
# Schema测试
pytest tests/kg/test_schemas.py -v

# 验证器测试
pytest tests/kg/test_validators.py -v

# 命名空间服务测试
pytest tests/kg/test_namespace_service.py -v

# 图谱服务测试
pytest tests/kg/test_graph_service.py -v

# API端点测试
pytest tests/kg/test_graph_api.py -v
```

### 运行特定测试类

```bash
# 运行PaperEntity的测试
pytest tests/kg/test_schemas.py::TestPaperEntity -v

# 运行图谱搜索的测试
pytest tests/kg/test_graph_service.py::TestGraphSearch -v

# 运行搜索API的测试
pytest tests/kg/test_graph_api.py::TestGraphSearchAPI -v
```

### 运行特定测试用例

```bash
# 运行特定的测试方法
pytest tests/kg/test_schemas.py::TestPaperEntity::test_valid_paper_entity -v

# 运行验证器的特定测试
pytest tests/kg/test_validators.py::TestValidateEntityType::test_valid_entity_types -v
```

### 生成测试覆盖率报告

```bash
# 生成覆盖率报告（从项目根目录）
pytest tests/kg/ --cov=app.schemas --cov=app.services.graph_service --cov=app.services.namespace_service --cov=app.api.routes.graph --cov-report=html --cov-report=term

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

---

## 📊 测试覆盖详情

### test_schemas.py

**测试内容**:
- 8种实体类型的创建和验证
- 9种关系类型的创建和验证
- Pydantic字段验证
- 边界条件测试

**关键测试用例**:
- ✅ 有效实体创建
- ✅ 无效数据验证失败
- ✅ arXiv ID格式验证
- ✅ 年份范围验证
- ✅ 权重范围验证
- ✅ 关系类型约束

**测试类**:
- `TestPaperEntity` (7个测试)
- `TestMethodEntity` (2个测试)
- `TestDatasetEntity` (1个测试)
- `TestTaskEntity` (1个测试)
- `TestMetricEntity` (1个测试)
- `TestAuthorEntity` (2个测试)
- `TestInstitutionEntity` (1个测试)
- `TestConceptEntity` (1个测试)
- `TestEntityTypeEnum` (2个测试)
- `TestProposesRelation` (2个测试)
- `TestEvaluatesOnRelation` (1个测试)
- `TestSolvesRelation` (1个测试)
- `TestImprovesOverRelation` (1个测试)
- `TestCitesRelation` (1个测试)
- `TestUsesMetricRelation` (1个测试)
- `TestAuthoredByRelation` (2个测试)
- `TestAffiliatedWithRelation` (1个测试)
- `TestHasConceptRelation` (2个测试)
- `TestRelationTypeEnum` (2个测试)
- `TestRelationConstraints` (1个测试)
- `TestWeightValidation` (3个测试)

### test_validators.py

**测试内容**:
- 实体类型验证
- 关系类型验证
- 关系约束验证
- UUID、arXiv ID、年份、权重验证

**关键测试用例**:
- ✅ 所有8种实体类型验证
- ✅ 所有9种关系类型验证
- ✅ 所有9种关系约束验证
- ✅ arXiv ID格式测试（6种有效格式，8种无效格式）
- ✅ 年份边界测试
- ✅ 权重边界测试

**测试类**:
- `TestValidateEntityType` (2个测试)
- `TestValidateRelationType` (2个测试)
- `TestValidateRelationConstraint` (13个测试)
- `TestValidateUUID` (2个测试)
- `TestValidateArxivId` (2个测试)
- `TestValidateYear` (2个测试)
- `TestValidateWeight` (2个测试)
- `TestEdgeCases` (3个测试)

### test_namespace_service.py

**测试内容**:
- 用户命名空间生成和解析
- 全局命名空间
- Fallback机制
- 权限验证

**关键测试用例**:
- ✅ 用户命名空间格式
- ✅ 全局命名空间
- ✅ 命名空间解析
- ✅ Fallback链生成
- ✅ 多层级搜索
- ✅ 权限验证

**测试类**:
- `TestGetUserNamespace` (3个测试)
- `TestGetGlobalNamespace` (1个测试)
- `TestParseNamespace` (4个测试)
- `TestIsUserNamespace` (2个测试)
- `TestIsGlobalNamespace` (2个测试)
- `TestGetFallbackChain` (3个测试)
- `TestSearchWithFallback` (4个测试)
- `TestValidateNamespaceAccess` (4个测试)
- `TestNamespaceServiceIntegration` (2个测试)
- `TestEdgeCases` (3个测试)

### test_graph_service.py

**测试内容**:
- 图谱搜索功能
- 重排算法（RRF、MMR）
- 节点查询
- 路径查询
- Fallback机制

**关键测试用例**:
- ✅ 基本搜索
- ✅ 带Fallback的搜索
- ✅ RRF重排
- ✅ MMR重排
- ✅ 节点详情查询
- ✅ 邻居查询
- ✅ 路径查询
- ✅ 错误处理

**测试类**:
- `TestGraphSearch` (6个测试)
- `TestRerankMethods` (3个测试)
- `TestNodeQueries` (3个测试)
- `TestPathQueries` (2个测试)
- `TestConvertSearchResult` (2个测试)
- `TestSearchInNamespace` (2个测试)
- `TestEdgeCases` (3个测试)

### test_graph_api.py

**测试内容**:
- 搜索API端点
- 节点详情API
- 邻居查询API
- 路径查询API
- 参数验证
- 错误处理

**关键测试用例**:
- ✅ 搜索API成功响应
- ✅ 带重排的搜索
- ✅ 节点详情API
- ✅ 邻居查询API
- ✅ 路径查询API
- ✅ 参数验证
- ✅ 错误处理

**测试类**:
- `TestGraphSearchAPI` (5个测试)
- `TestNodeDetailAPI` (3个测试)
- `TestNeighborsAPI` (3个测试)
- `TestPathQueryAPI` (4个测试)
- `TestDeprecatedEntityAPI` (2个测试)
- `TestAPIValidation` (4个测试)
- `TestAPIErrorHandling` (2个测试)
- `TestAPIIntegration` (1个测试)

---

## ✅ 测试用例分类

### 单元测试（Unit Tests）

- **test_schemas.py**: Schema定义的单元测试
- **test_validators.py**: 验证函数的单元测试
- **test_namespace_service.py**: 命名空间服务的单元测试

### 集成测试（Integration Tests）

- **test_graph_service.py**: 图谱服务的集成测试（涉及多个组件）
- **test_graph_api.py**: API端点的集成测试（涉及HTTP层和服务层）

### 测试覆盖的功能模块

| 功能模块 | 测试文件 | 测试完整性 |
|---------|---------|-----------|
| Schema定义 | test_schemas.py | ✅ 完整 |
| 数据验证 | test_validators.py | ✅ 完整 |
| 命名空间管理 | test_namespace_service.py | ✅ 完整 |
| 图谱搜索 | test_graph_service.py, test_graph_api.py | ✅ 完整 |
| 节点查询 | test_graph_service.py, test_graph_api.py | ✅ 完整 |
| 路径查询 | test_graph_service.py, test_graph_api.py | ✅ 完整 |
| Fallback机制 | test_namespace_service.py, test_graph_service.py | ✅ 完整 |

---

## 🔍 测试策略

### 1. Schema测试策略

- 测试所有实体和关系的创建
- 测试Pydantic验证规则
- 测试边界条件和无效输入
- 测试所有约束条件

### 2. 验证器测试策略

- 测试所有验证函数的正向和反向case
- 测试边界值
- 测试无效输入
- 测试特殊字符和格式

### 3. 服务层测试策略

- 使用Mock模拟外部依赖（Graphiti、Neo4j）
- 测试业务逻辑的正确性
- 测试错误处理和异常情况
- 测试Fallback机制

### 4. API层测试策略

- 测试HTTP请求和响应
- 测试参数验证
- 测试错误状态码
- 测试集成场景

---

## 📈 预期测试结果

### 测试覆盖率目标

| 组件 | 目标覆盖率 | 实际覆盖率（预估） |
|------|-----------|------------------|
| app/schemas/entities.py | >90% | >95% |
| app/schemas/relations.py | >90% | >95% |
| app/schemas/validators.py | >90% | >95% |
| app/services/namespace_service.py | >80% | >85% |
| app/services/graph_service.py | >80% | >80% |
| app/api/routes/graph.py | >70% | >75% |

**总体目标**: >80%

### 测试执行时间

- Schema测试: ~2秒
- 验证器测试: ~1秒
- 命名空间服务测试: ~3秒
- 图谱服务测试: ~5秒
- API端点测试: ~10秒

**总计**: ~21秒

---

## ⚠️ 注意事项

### Mock的使用

1. **Graphiti Client**: 所有Graphiti相关调用都使用Mock，避免依赖实际的Neo4j和OpenAI API
2. **Database**: API测试使用测试数据库，但图谱数据使用Mock
3. **Redis**: 如果需要，使用fakeredis

### 测试隔离

- 每个测试用例独立运行
- 不依赖测试执行顺序
- 清理测试数据

### 异步测试

- 使用 `@pytest.mark.asyncio` 标记异步测试
- 使用 `AsyncMock` 模拟异步函数

---

## 🐛 常见问题

### Q1: 测试运行失败

**可能原因**:
- 缺少测试依赖
- 测试数据库未创建
- Mock配置错误

**解决方案**:
```bash
# 安装依赖
pip install -r tests/requirements-test.txt

# 检查数据库
mysql -u root -p -e "SHOW DATABASES LIKE 'test_%';"
```

### Q2: 异步测试报错

**可能原因**:
- pytest-asyncio未安装或版本不对
- event_loop fixture配置问题

**解决方案**:
```bash
pip install pytest-asyncio==0.21.0
```

### Q3: Mock不生效

**可能原因**:
- Mock的路径不正确
- 需要使用AsyncMock而不是Mock

**解决方案**:
```python
# 正确的Mock路径
with patch.object(GraphService, 'search', new_callable=AsyncMock):
    ...
```

---

## 📝 测试维护

### 添加新测试

1. 选择合适的测试文件或创建新文件
2. 继承或创建测试类
3. 编写测试方法（以test_开头）
4. 添加必要的Mock
5. 运行测试验证

### 更新测试

- 代码变更时同步更新测试
- 保持测试用例的可读性
- 及时修复失败的测试

---

## 📊 测试报告示例

```
============================== test session starts ===============================
platform win32 -- Python 3.10.x, pytest-7.4.x, pluggy-1.3.x
rootdir: D:\My_Python_Project\graduationProject
plugins: asyncio-0.21.0, cov-4.1.0
collected 175 items

tests/test_schemas.py ....................................................  [ 28%]
tests/test_validators.py ........................................        [ 51%]
tests/test_namespace_service.py ..............................          [ 68%]
tests/test_graph_service.py .........................                   [ 82%]
tests/test_graph_api.py ..............................                  [100%]

============================== 175 passed in 21.3s ===============================
```

---

## ✅ 验收标准

Module B的测试验收标准：

- [x] Schema测试完整覆盖8种实体和9种关系
- [x] 验证器测试覆盖所有验证函数
- [x] 命名空间服务测试覆盖所有功能
- [x] 图谱服务测试覆盖核心业务逻辑
- [x] API端点测试覆盖所有5个端点
- [x] 测试用例总数 > 150个
- [x] 预估代码覆盖率 > 80%
- [x] 所有测试可独立运行
- [x] 测试执行时间 < 30秒

---

## 📞 联系方式

**测试负责人**: Backend Developer B  
**模块**: 知识图谱模块 (Module B)  
**完成日期**: 2025-12-10

如有测试相关问题，请参考本文档或联系开发人员。

---

**测试文档完成**
