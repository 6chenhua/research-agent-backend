"""
测试Schema验证器
包括实体类型、关系类型、关系约束等验证函数
"""
import pytest

from app.schemas.validators import (
    validate_entity_type,
    validate_relation_type,
    validate_relation_constraint,
    validate_uuid,
    validate_arxiv_id,
    validate_year,
    validate_weight
)


class TestValidateEntityType:
    """测试实体类型验证"""
    
    def test_valid_entity_types(self):
        """测试有效的实体类型"""
        valid_types = [
            "Paper", "Method", "Dataset", "Task",
            "Metric", "Author", "Institution", "Concept"
        ]
        for entity_type in valid_types:
            assert validate_entity_type(entity_type) is True
    
    def test_invalid_entity_type(self):
        """测试无效的实体类型"""
        assert validate_entity_type("InvalidType") is False
        assert validate_entity_type("paper") is False  # 大小写敏感
        assert validate_entity_type("") is False
        assert validate_entity_type("PAPER") is False


class TestValidateRelationType:
    """测试关系类型验证"""
    
    def test_valid_relation_types(self):
        """测试有效的关系类型"""
        valid_types = [
            "PROPOSES", "EVALUATES_ON", "SOLVES", "IMPROVES_OVER",
            "CITES", "USES_METRIC", "AUTHORED_BY", "AFFILIATED_WITH",
            "HAS_CONCEPT"
        ]
        for rel_type in valid_types:
            assert validate_relation_type(rel_type) is True
    
    def test_invalid_relation_type(self):
        """测试无效的关系类型"""
        assert validate_relation_type("INVALID_RELATION") is False
        assert validate_relation_type("proposes") is False  # 大小写敏感
        assert validate_relation_type("") is False


class TestValidateRelationConstraint:
    """测试关系约束验证"""
    
    def test_valid_proposes_constraint(self):
        """测试有效的PROPOSES约束"""
        is_valid, error = validate_relation_constraint(
            "PROPOSES", "Paper", "Method"
        )
        assert is_valid is True
        assert error is None
    
    def test_invalid_proposes_constraint(self):
        """测试无效的PROPOSES约束"""
        is_valid, error = validate_relation_constraint(
            "PROPOSES", "Paper", "Dataset"
        )
        assert is_valid is False
        assert "PROPOSES requires source=Paper, target=Method" in error
    
    def test_valid_evaluates_on_constraint(self):
        """测试有效的EVALUATES_ON约束"""
        is_valid, error = validate_relation_constraint(
            "EVALUATES_ON", "Paper", "Dataset"
        )
        assert is_valid is True
        assert error is None
    
    def test_valid_solves_constraint(self):
        """测试有效的SOLVES约束"""
        is_valid, error = validate_relation_constraint(
            "SOLVES", "Method", "Task"
        )
        assert is_valid is True
        assert error is None
    
    def test_valid_improves_over_constraint(self):
        """测试有效的IMPROVES_OVER约束"""
        is_valid, error = validate_relation_constraint(
            "IMPROVES_OVER", "Method", "Method"
        )
        assert is_valid is True
        assert error is None
    
    def test_valid_cites_constraint(self):
        """测试有效的CITES约束"""
        is_valid, error = validate_relation_constraint(
            "CITES", "Paper", "Paper"
        )
        assert is_valid is True
        assert error is None
    
    def test_valid_uses_metric_constraint(self):
        """测试有效的USES_METRIC约束"""
        is_valid, error = validate_relation_constraint(
            "USES_METRIC", "Paper", "Metric"
        )
        assert is_valid is True
        assert error is None
    
    def test_valid_authored_by_constraint(self):
        """测试有效的AUTHORED_BY约束"""
        is_valid, error = validate_relation_constraint(
            "AUTHORED_BY", "Paper", "Author"
        )
        assert is_valid is True
        assert error is None
    
    def test_valid_affiliated_with_constraint(self):
        """测试有效的AFFILIATED_WITH约束"""
        is_valid, error = validate_relation_constraint(
            "AFFILIATED_WITH", "Author", "Institution"
        )
        assert is_valid is True
        assert error is None
    
    def test_valid_has_concept_constraint(self):
        """测试有效的HAS_CONCEPT约束"""
        is_valid, error = validate_relation_constraint(
            "HAS_CONCEPT", "Paper", "Concept"
        )
        assert is_valid is True
        assert error is None
    
    def test_unknown_relation_type(self):
        """测试未知的关系类型"""
        is_valid, error = validate_relation_constraint(
            "UNKNOWN_RELATION", "Paper", "Method"
        )
        assert is_valid is False
        assert "Unknown relation type" in error
    
    def test_wrong_source_type(self):
        """测试错误的源实体类型"""
        is_valid, error = validate_relation_constraint(
            "PROPOSES", "Method", "Method"  # 应该是Paper -> Method
        )
        assert is_valid is False
        assert "source=Paper" in error
    
    def test_wrong_target_type(self):
        """测试错误的目标实体类型"""
        is_valid, error = validate_relation_constraint(
            "PROPOSES", "Paper", "Paper"  # 应该是Paper -> Method
        )
        assert is_valid is False
        assert "target=Method" in error


class TestValidateUUID:
    """测试UUID验证"""
    
    def test_valid_uuids(self):
        """测试有效的UUID"""
        valid_uuids = [
            "paper_001",
            "method_transformer",
            "abc-123-def-456",
            "node_12345678",
        ]
        for uuid in valid_uuids:
            assert validate_uuid(uuid) is True
    
    def test_invalid_uuids(self):
        """测试无效的UUID"""
        assert validate_uuid("") is False
        assert validate_uuid(None) is False
        assert validate_uuid("a" * 101) is False  # 太长


class TestValidateArxivId:
    """测试arXiv ID验证"""
    
    def test_valid_arxiv_ids(self):
        """测试有效的arXiv ID"""
        valid_ids = [
            "1706.03762",
            "1706.03762v2",
            "2103.14030",
            "2103.14030v1",
            "1234.12345",
            "1234.12345v99",
        ]
        for arxiv_id in valid_ids:
            assert validate_arxiv_id(arxiv_id) is True
    
    def test_invalid_arxiv_ids(self):
        """测试无效的arXiv ID"""
        invalid_ids = [
            "",
            None,
            "invalid",
            "123.456",  # 太短
            "12345.12345",  # YYMM部分太长
            "1234.123",  # NNNNN部分太短
            "abcd.12345",  # 非数字
            "1234.12345v",  # v后面没有数字
        ]
        for arxiv_id in invalid_ids:
            assert validate_arxiv_id(arxiv_id) is False


class TestValidateYear:
    """测试年份验证"""
    
    def test_valid_years(self):
        """测试有效的年份"""
        valid_years = [1900, 1950, 2000, 2023, 2024, 2100]
        for year in valid_years:
            assert validate_year(year) is True
    
    def test_invalid_years(self):
        """测试无效的年份"""
        invalid_years = [1899, 1800, 2101, 3000, 0, -1]
        for year in invalid_years:
            assert validate_year(year) is False


class TestValidateWeight:
    """测试权重验证"""
    
    def test_valid_weights(self):
        """测试有效的权重"""
        valid_weights = [0.0, 0.1, 0.5, 0.9, 1.0]
        for weight in valid_weights:
            assert validate_weight(weight) is True
    
    def test_invalid_weights(self):
        """测试无效的权重"""
        invalid_weights = [-0.1, -1.0, 1.1, 2.0, 100.0]
        for weight in invalid_weights:
            assert validate_weight(weight) is False


class TestEdgeCases:
    """测试边界情况"""
    
    def test_none_inputs(self):
        """测试None输入"""
        assert validate_uuid(None) is False
        assert validate_arxiv_id(None) is False
    
    def test_empty_string_inputs(self):
        """测试空字符串输入"""
        assert validate_entity_type("") is False
        assert validate_relation_type("") is False
        assert validate_uuid("") is False
        assert validate_arxiv_id("") is False
    
    def test_boundary_values(self):
        """测试边界值"""
        # 年份边界
        assert validate_year(1900) is True
        assert validate_year(1899) is False
        assert validate_year(2100) is True
        assert validate_year(2101) is False
        
        # 权重边界
        assert validate_weight(0.0) is True
        assert validate_weight(1.0) is True
        assert validate_weight(-0.000001) is False
        assert validate_weight(1.000001) is False

