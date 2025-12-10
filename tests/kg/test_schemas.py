"""
测试知识图谱Schema定义
包括实体Schema和关系Schema的验证测试
"""
import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.entities import (
    PaperEntity, MethodEntity, DatasetEntity, TaskEntity,
    MetricEntity, AuthorEntity, InstitutionEntity, ConceptEntity,
    EntityType, ENTITY_TYPE_MAP
)
from app.schemas.relations import (
    ProposesRelation, EvaluatesOnRelation, SolvesRelation,
    ImprovesOverRelation, CitesRelation, UsesMetricRelation,
    AuthoredByRelation, AffiliatedWithRelation, HasConceptRelation,
    RelationType, RELATION_TYPE_MAP, RELATION_CONSTRAINTS
)


class TestPaperEntity:
    """测试PaperEntity"""
    
    def test_valid_paper_entity(self):
        """测试创建有效的论文实体"""
        paper = PaperEntity(
            name="Attention Is All You Need",
            title="Attention Is All You Need",
            arxiv_id="1706.03762",
            year=2017,
            venue="NeurIPS",
            authors=["Vaswani", "Shazeer"]
        )
        assert paper.name == "Attention Is All You Need"
        assert paper.title == "Attention Is All You Need"
        assert paper.arxiv_id == "1706.03762"
        assert paper.year == 2017
        assert len(paper.authors) == 2
    
    def test_paper_with_empty_title_fails(self):
        """测试空标题应该失败"""
        with pytest.raises(ValidationError) as exc_info:
            PaperEntity(
                name="Test",
                title="",
                year=2017
            )
        assert "title" in str(exc_info.value)
    
    def test_paper_with_invalid_arxiv_id(self):
        """测试无效的arXiv ID"""
        with pytest.raises(ValidationError):
            PaperEntity(
                name="Test Paper",
                title="Test Paper",
                arxiv_id="invalid_format"
            )
    
    def test_paper_with_invalid_year(self):
        """测试无效的年份"""
        with pytest.raises(ValidationError):
            PaperEntity(
                name="Test Paper",
                title="Test Paper",
                year=1899  # 太早
            )
        
        with pytest.raises(ValidationError):
            PaperEntity(
                name="Test Paper",
                title="Test Paper",
                year=2101  # 太晚
            )
    
    def test_paper_with_valid_arxiv_id_formats(self):
        """测试各种有效的arXiv ID格式"""
        valid_ids = ["1706.03762", "1706.03762v2", "2103.14030"]
        for arxiv_id in valid_ids:
            paper = PaperEntity(
                name="Test",
                title="Test",
                arxiv_id=arxiv_id
            )
            assert paper.arxiv_id == arxiv_id
    
    def test_paper_with_negative_citation_count(self):
        """测试负数引用数应该失败"""
        with pytest.raises(ValidationError):
            PaperEntity(
                name="Test",
                title="Test",
                citation_count=-1
            )


class TestMethodEntity:
    """测试MethodEntity"""
    
    def test_valid_method_entity(self):
        """测试创建有效的方法实体"""
        method = MethodEntity(
            name="Transformer",
            description="Self-attention architecture",
            category="Deep Learning"
        )
        assert method.name == "Transformer"
        assert method.description == "Self-attention architecture"
        assert method.category == "Deep Learning"
    
    def test_method_with_minimal_fields(self):
        """测试只有必填字段的方法实体"""
        method = MethodEntity(name="BERT")
        assert method.name == "BERT"
        assert method.description == ""


class TestDatasetEntity:
    """测试DatasetEntity"""
    
    def test_valid_dataset_entity(self):
        """测试创建有效的数据集实体"""
        dataset = DatasetEntity(
            name="ImageNet",
            description="Large scale image dataset",
            domain="Computer Vision",
            size="1.2M images"
        )
        assert dataset.name == "ImageNet"
        assert dataset.domain == "Computer Vision"


class TestTaskEntity:
    """测试TaskEntity"""
    
    def test_valid_task_entity(self):
        """测试创建有效的任务实体"""
        task = TaskEntity(
            name="Machine Translation",
            description="Translate text between languages",
            domain="NLP"
        )
        assert task.name == "Machine Translation"
        assert task.domain == "NLP"


class TestMetricEntity:
    """测试MetricEntity"""
    
    def test_valid_metric_entity(self):
        """测试创建有效的指标实体"""
        metric = MetricEntity(
            name="BLEU",
            value=0.85,
            unit="score",
            description="Bilingual Evaluation Understudy"
        )
        assert metric.name == "BLEU"
        assert metric.value == 0.85


class TestAuthorEntity:
    """测试AuthorEntity"""
    
    def test_valid_author_entity(self):
        """测试创建有效的作者实体"""
        author = AuthorEntity(
            name="Geoffrey Hinton",
            affiliation="University of Toronto",
            h_index=180,
            paper_count=250
        )
        assert author.name == "Geoffrey Hinton"
        assert author.h_index == 180
    
    def test_author_with_negative_h_index(self):
        """测试负数h-index应该失败"""
        with pytest.raises(ValidationError):
            AuthorEntity(
                name="Test Author",
                h_index=-1
            )


class TestInstitutionEntity:
    """测试InstitutionEntity"""
    
    def test_valid_institution_entity(self):
        """测试创建有效的机构实体"""
        institution = InstitutionEntity(
            name="MIT",
            country="USA",
            city="Cambridge",
            type="University"
        )
        assert institution.name == "MIT"
        assert institution.country == "USA"


class TestConceptEntity:
    """测试ConceptEntity"""
    
    def test_valid_concept_entity(self):
        """测试创建有效的概念实体"""
        concept = ConceptEntity(
            name="Attention Mechanism",
            description="Focus on relevant parts of input",
            domain="Deep Learning",
            aliases=["Self-Attention", "Attention"]
        )
        assert concept.name == "Attention Mechanism"
        assert len(concept.aliases) == 2


class TestEntityTypeEnum:
    """测试EntityType枚举"""
    
    def test_all_entity_types_exist(self):
        """测试所有实体类型都存在"""
        expected_types = [
            "Paper", "Method", "Dataset", "Task",
            "Metric", "Author", "Institution", "Concept"
        ]
        for entity_type in expected_types:
            assert hasattr(EntityType, entity_type.upper())
    
    def test_entity_type_map_completeness(self):
        """测试实体类型映射完整性"""
        assert len(ENTITY_TYPE_MAP) == 8
        for entity_type, entity_class in ENTITY_TYPE_MAP.items():
            assert entity_type in EntityType


class TestProposesRelation:
    """测试PROPOSES关系"""
    
    def test_valid_proposes_relation(self):
        """测试创建有效的PROPOSES关系"""
        relation = ProposesRelation(
            source_uuid="paper_001",
            target_uuid="method_001",
            is_primary=True,
            description="Paper proposes Transformer"
        )
        assert relation.relation_type == RelationType.PROPOSES
        assert relation.source_uuid == "paper_001"
        assert relation.target_uuid == "method_001"
        assert relation.is_primary is True
    
    def test_proposes_default_weight(self):
        """测试默认权重"""
        relation = ProposesRelation(
            source_uuid="paper_001",
            target_uuid="method_001"
        )
        assert relation.weight == 1.0


class TestEvaluatesOnRelation:
    """测试EVALUATES_ON关系"""
    
    def test_valid_evaluates_on_relation(self):
        """测试创建有效的EVALUATES_ON关系"""
        relation = EvaluatesOnRelation(
            source_uuid="paper_001",
            target_uuid="dataset_001",
            metric_value=93.2,
            metric_name="F1 Score"
        )
        assert relation.relation_type == RelationType.EVALUATES_ON
        assert relation.metric_value == 93.2


class TestSolvesRelation:
    """测试SOLVES关系"""
    
    def test_valid_solves_relation(self):
        """测试创建有效的SOLVES关系"""
        relation = SolvesRelation(
            source_uuid="method_001",
            target_uuid="task_001",
            effectiveness="State-of-the-art"
        )
        assert relation.relation_type == RelationType.SOLVES


class TestImprovesOverRelation:
    """测试IMPROVES_OVER关系"""
    
    def test_valid_improves_over_relation(self):
        """测试创建有效的IMPROVES_OVER关系"""
        relation = ImprovesOverRelation(
            source_uuid="method_002",
            target_uuid="method_001",
            improvement_percentage=15.3,
            improvement_description="Better performance"
        )
        assert relation.relation_type == RelationType.IMPROVES_OVER
        assert relation.improvement_percentage == 15.3


class TestCitesRelation:
    """测试CITES关系"""
    
    def test_valid_cites_relation(self):
        """测试创建有效的CITES关系"""
        relation = CitesRelation(
            source_uuid="paper_002",
            target_uuid="paper_001",
            citation_context="Building upon...",
            section="Introduction"
        )
        assert relation.relation_type == RelationType.CITES


class TestUsesMetricRelation:
    """测试USES_METRIC关系"""
    
    def test_valid_uses_metric_relation(self):
        """测试创建有效的USES_METRIC关系"""
        relation = UsesMetricRelation(
            source_uuid="paper_001",
            target_uuid="metric_001",
            reported_value=96.4
        )
        assert relation.relation_type == RelationType.USES_METRIC


class TestAuthoredByRelation:
    """测试AUTHORED_BY关系"""
    
    def test_valid_authored_by_relation(self):
        """测试创建有效的AUTHORED_BY关系"""
        relation = AuthoredByRelation(
            source_uuid="paper_001",
            target_uuid="author_001",
            author_position=1,
            contribution="First author"
        )
        assert relation.relation_type == RelationType.AUTHORED_BY
        assert relation.author_position == 1
    
    def test_authored_by_with_zero_position_fails(self):
        """测试作者位置为0应该失败"""
        with pytest.raises(ValidationError):
            AuthoredByRelation(
                source_uuid="paper_001",
                target_uuid="author_001",
                author_position=0
            )


class TestAffiliatedWithRelation:
    """测试AFFILIATED_WITH关系"""
    
    def test_valid_affiliated_with_relation(self):
        """测试创建有效的AFFILIATED_WITH关系"""
        relation = AffiliatedWithRelation(
            source_uuid="author_001",
            target_uuid="inst_001",
            position="Professor",
            start_date="1987"
        )
        assert relation.relation_type == RelationType.AFFILIATED_WITH


class TestHasConceptRelation:
    """测试HAS_CONCEPT关系"""
    
    def test_valid_has_concept_relation(self):
        """测试创建有效的HAS_CONCEPT关系"""
        relation = HasConceptRelation(
            source_uuid="paper_001",
            target_uuid="concept_001",
            relevance=0.98,
            mention_count=47
        )
        assert relation.relation_type == RelationType.HAS_CONCEPT
        assert relation.relevance == 0.98
    
    def test_has_concept_with_invalid_relevance(self):
        """测试无效的相关度"""
        with pytest.raises(ValidationError):
            HasConceptRelation(
                source_uuid="paper_001",
                target_uuid="concept_001",
                relevance=1.5  # 超过1.0
            )


class TestRelationTypeEnum:
    """测试RelationType枚举"""
    
    def test_all_relation_types_exist(self):
        """测试所有关系类型都存在"""
        expected_types = [
            "PROPOSES", "EVALUATES_ON", "SOLVES", "IMPROVES_OVER",
            "CITES", "USES_METRIC", "AUTHORED_BY", "AFFILIATED_WITH",
            "HAS_CONCEPT"
        ]
        for rel_type in expected_types:
            assert hasattr(RelationType, rel_type)
    
    def test_relation_type_map_completeness(self):
        """测试关系类型映射完整性"""
        assert len(RELATION_TYPE_MAP) == 9


class TestRelationConstraints:
    """测试关系约束"""
    
    def test_all_relation_constraints_defined(self):
        """测试所有关系都有约束定义"""
        assert len(RELATION_CONSTRAINTS) == 9
        
        expected_constraints = {
            RelationType.PROPOSES: ("Paper", "Method"),
            RelationType.EVALUATES_ON: ("Paper", "Dataset"),
            RelationType.SOLVES: ("Method", "Task"),
            RelationType.IMPROVES_OVER: ("Method", "Method"),
            RelationType.CITES: ("Paper", "Paper"),
            RelationType.USES_METRIC: ("Paper", "Metric"),
            RelationType.AUTHORED_BY: ("Paper", "Author"),
            RelationType.AFFILIATED_WITH: ("Author", "Institution"),
            RelationType.HAS_CONCEPT: ("Paper", "Concept"),
        }
        
        for rel_type, constraint in expected_constraints.items():
            assert RELATION_CONSTRAINTS[rel_type] == constraint


class TestWeightValidation:
    """测试权重字段验证"""
    
    def test_weight_in_valid_range(self):
        """测试有效范围内的权重"""
        for weight in [0.0, 0.5, 1.0]:
            relation = ProposesRelation(
                source_uuid="p1",
                target_uuid="m1",
                weight=weight
            )
            assert relation.weight == weight
    
    def test_weight_below_zero_fails(self):
        """测试负数权重应该失败"""
        with pytest.raises(ValidationError):
            ProposesRelation(
                source_uuid="p1",
                target_uuid="m1",
                weight=-0.1
            )
    
    def test_weight_above_one_fails(self):
        """测试大于1的权重应该失败"""
        with pytest.raises(ValidationError):
            ProposesRelation(
                source_uuid="p1",
                target_uuid="m1",
                weight=1.1
            )

