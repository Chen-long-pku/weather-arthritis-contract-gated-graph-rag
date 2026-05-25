"""
知识图谱查询服务
提供对Neo4j图谱的查询接口
"""

from typing import List, Dict, Optional, Any
from neo4j import GraphDatabase
import logging
import re

logger = logging.getLogger(__name__)

ALLOWED_ENTITY_LABELS = {
    "ChronicDisease",
    "ArthritisType",
    "ClimateFactor",
    "Symptom",
    "Mechanism",
    "Population",
    "StudyType",
    "Study",
}
WRITE_CYPHER_PATTERN = re.compile(
    r"\b(CREATE|MERGE|SET|DELETE|DETACH|REMOVE|DROP|LOAD\s+CSV|FOREACH)\b"
    r"|\bCALL\s+(dbms|apoc\.periodic|apoc\.create|apoc\.merge|apoc\.refactor)\b",
    re.IGNORECASE,
)


def _validate_label(label: str) -> str:
    """限制可拼接进Cypher标签位置的值，避免标签注入。"""
    if label not in ALLOWED_ENTITY_LABELS:
        raise ValueError(f"不支持的实体类型: {label}")
    return label


def _bounded_int(value: int, minimum: int, maximum: int, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(minimum, min(maximum, number))


class GraphQueryService:
    """知识图谱查询服务"""
    
    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        """初始化"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database
        logger.info(f"图谱查询服务初始化完成: {uri}")
    
    def close(self):
        """关闭连接"""
        self.driver.close()
    
    def execute_query(self, cypher: str, parameters: Dict = None) -> List[Dict]:
        """执行Cypher查询"""
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher, parameters or {})
            return [dict(record) for record in result]

    def execute_read_query(self, cypher: str, parameters: Dict = None) -> List[Dict]:
        """执行只读Cypher查询，用于研究者界面的自定义查询入口。"""
        if WRITE_CYPHER_PATTERN.search(cypher):
            raise ValueError("出于数据安全考虑，自定义Cypher仅支持只读查询。")
        return self.execute_query(cypher, parameters)
    
    # ==================== 实体查询 ====================
    
    def search_entity(self, entity_name: str, entity_type: Optional[str] = None) -> List[Dict]:
        """
        搜索实体
        
        Args:
            entity_name: 实体名称（支持模糊匹配）
            entity_type: 实体类型（ChronicDisease/ArthritisType/ClimateFactor/Symptom）
        """
        if entity_type:
            entity_type = _validate_label(entity_type)
            cypher = f"""
            MATCH (e:{entity_type})
            WHERE toLower(coalesce(e.name, '')) CONTAINS toLower($name)
               OR toLower(coalesce(e.canonical_name, '')) CONTAINS toLower($name)
            OPTIONAL MATCH (e)-[:STUDIED_IN]->(s:Study)
            WITH e, count(DISTINCT s) as study_count
            OPTIONAL MATCH (e)-[r]-()
            WITH e, study_count, count(DISTINCT r) as relation_count
            RETURN e.entity_id as entity_id, e.name as name, coalesce(e.type, labels(e)[0]) as type,
                   coalesce(e.canonical_name, toLower(e.name)) as canonical_name,
                   coalesce(e.study_count, study_count) as study_count,
                   coalesce(e.degree, relation_count) as relation_count
            ORDER BY study_count DESC
            LIMIT 10
            """
        else:
            cypher = """
            MATCH (e:Entity)
            WHERE e.name IS NOT NULL
              AND (
                toLower(e.name) CONTAINS toLower($name)
                OR toLower(coalesce(e.canonical_name, '')) CONTAINS toLower($name)
              )
            OPTIONAL MATCH (e)-[:STUDIED_IN]->(s:Study)
            WITH e, count(DISTINCT s) as study_count
            OPTIONAL MATCH (e)-[r]-()
            WITH e, study_count, count(DISTINCT r) as relation_count
            RETURN e.entity_id as entity_id, e.name as name, coalesce(e.type, labels(e)[0]) as type,
                   coalesce(e.canonical_name, toLower(e.name)) as canonical_name,
                   coalesce(e.study_count, study_count) as study_count,
                   coalesce(e.degree, relation_count) as relation_count
            ORDER BY study_count DESC
            LIMIT 10
            """
        
        return self.execute_query(cypher, {"name": entity_name})
    
    def get_entity_details(self, entity_name: str) -> Optional[Dict]:
        """获取实体详细信息"""
        cypher = """
        MATCH (e:Entity)
        WHERE e.name = $name OR e.canonical_name = toLower($name)
        OPTIONAL MATCH (e)-[:STUDIED_IN]->(s:Study)
        WITH e, count(DISTINCT s) as study_count
        OPTIONAL MATCH (e)-[r]-()
        WITH e, study_count, count(DISTINCT r) as relation_count
        RETURN e.entity_id as entity_id, e.name as name, coalesce(e.type, labels(e)[0]) as type,
               coalesce(e.canonical_name, toLower(e.name)) as canonical_name,
               coalesce(e.study_count, study_count) as study_count,
               coalesce(e.degree, relation_count) as relation_count,
               e.description as description
        LIMIT 1
        """
        results = self.execute_query(cypher, {"name": entity_name})
        return results[0] if results else None
    
    # ==================== 关系查询 ====================
    
    def get_entity_relations(self, entity_name: str, direction: str = "both") -> List[Dict]:
        """
        获取实体的关系
        
        Args:
            entity_name: 实体名称
            direction: 方向（outgoing/incoming/both）
        """
        if direction == "outgoing":
            cypher = """
            MATCH (e1:Entity)-[r]->(e2:Entity)
            WHERE (e1.name = $name OR e1.canonical_name = toLower($name))
              AND type(r) <> 'STUDIED_IN'
            RETURN e1.name as source, type(r) as relation, e2.name as target,
                   coalesce(e1.type, labels(e1)[0]) as source_type,
                   coalesce(e2.type, labels(e2)[0]) as target_type,
                   coalesce(r.support_count, 0) as support_count,
                   coalesce(r.evidence_tier, 'unknown') as evidence_tier,
                   coalesce(r.pmids, []) as pmids
            ORDER BY support_count DESC
            LIMIT 20
            """
        elif direction == "incoming":
            cypher = """
            MATCH (e1:Entity)<-[r]-(e2:Entity)
            WHERE (e1.name = $name OR e1.canonical_name = toLower($name))
              AND type(r) <> 'STUDIED_IN'
            RETURN e2.name as source, type(r) as relation, e1.name as target,
                   coalesce(e2.type, labels(e2)[0]) as source_type,
                   coalesce(e1.type, labels(e1)[0]) as target_type,
                   coalesce(r.support_count, 0) as support_count,
                   coalesce(r.evidence_tier, 'unknown') as evidence_tier,
                   coalesce(r.pmids, []) as pmids
            ORDER BY support_count DESC
            LIMIT 20
            """
        else:  # both
            cypher = """
            MATCH (e1:Entity)-[r]-(e2:Entity)
            WHERE (e1.name = $name OR e1.canonical_name = toLower($name))
              AND type(r) <> 'STUDIED_IN'
            RETURN e1.name as entity1, type(r) as relation, e2.name as entity2,
                   coalesce(e1.type, labels(e1)[0]) as type1,
                   coalesce(e2.type, labels(e2)[0]) as type2,
                   coalesce(r.support_count, 0) as support_count,
                   coalesce(r.evidence_tier, 'unknown') as evidence_tier,
                   coalesce(r.pmids, []) as pmids
            ORDER BY support_count DESC
            LIMIT 20
            """
        
        return self.execute_query(cypher, {"name": entity_name})
    
    def find_relation(self, entity1: str, entity2: str) -> List[Dict]:
        """查找两个实体之间的关系"""
        cypher = """
        MATCH (e1:Entity)-[r]-(e2:Entity)
        WHERE (e1.name = $name1 OR e1.canonical_name = toLower($name1))
          AND (e2.name = $name2 OR e2.canonical_name = toLower($name2))
          AND type(r) <> 'STUDIED_IN'
        RETURN e1.name as source, type(r) as relation, e2.name as target,
               coalesce(r.support_count, 0) as support_count,
               coalesce(r.evidence_tier, 'unknown') as evidence_tier,
               coalesce(r.pmids, []) as pmids
        ORDER BY support_count DESC
        """
        return self.execute_query(cypher, {"name1": entity1, "name2": entity2})
    
    # ==================== 路径查询 ====================
    
    def find_shortest_path(self, entity1: str, entity2: str, max_length: int = 3) -> List[Dict]:
        """查找两个实体之间的最短路径"""
        max_length = _bounded_int(max_length, 1, 5, 3)
        cypher = f"""
        MATCH path = shortestPath((e1:Entity)-[*..{max_length}]-(e2:Entity))
        WHERE (e1.name = $name1 OR e1.canonical_name = toLower($name1))
          AND (e2.name = $name2 OR e2.canonical_name = toLower($name2))
        RETURN [node in nodes(path) | node.name] as path,
               [rel in relationships(path) | type(rel)] as relations,
               length(path) as length
        LIMIT 5
        """
        return self.execute_query(cypher, {"name1": entity1, "name2": entity2})
    
    # ==================== 文献查询 ====================
    
    def get_entity_studies(self, entity_name: str) -> List[Dict]:
        """获取提到某实体的文献"""
        cypher = """
        MATCH (e:Entity)-[:STUDIED_IN]->(s:Study)
        WHERE e.name = $name OR e.canonical_name = toLower($name)
        RETURN s.pmid as pmid, s.title as title, s.year as year
        ORDER BY s.year DESC
        LIMIT 20
        """
        return self.execute_query(cypher, {"name": entity_name})
    
    def get_relation_studies(self, entity1: str, entity2: str) -> List[Dict]:
        """获取研究两个实体关系的文献"""
        cypher = """
        MATCH (e1:Entity)-[:STUDIED_IN]->(s:Study)<-[:STUDIED_IN]-(e2:Entity)
        WHERE (e1.name = $name1 OR e1.canonical_name = toLower($name1))
          AND (e2.name = $name2 OR e2.canonical_name = toLower($name2))
        RETURN DISTINCT s.pmid as pmid, s.title as title, s.year as year
        ORDER BY s.year DESC
        LIMIT 10
        """
        return self.execute_query(cypher, {"name1": entity1, "name2": entity2})
    
    # ==================== 统计查询 ====================
    
    def get_statistics(self) -> Dict:
        """获取图谱统计信息"""
        stats = {}
        
        # 节点统计
        cypher_nodes = """
        MATCH (n)
        RETURN labels(n)[0] as type, count(*) as count
        ORDER BY count DESC
        """
        stats['nodes'] = self.execute_query(cypher_nodes)
        
        # 关系统计
        cypher_rels = """
        MATCH ()-[r]->()
        RETURN type(r) as type, count(*) as count
        ORDER BY count DESC
        """
        stats['relations'] = self.execute_query(cypher_rels)
        
        return stats
    
    def get_top_entities(self, entity_type: str, limit: int = 10) -> List[Dict]:
        """获取最常出现的实体"""
        entity_type = _validate_label(entity_type)
        limit = _bounded_int(limit, 1, 100, 10)
        cypher = f"""
        MATCH (e:Entity:{entity_type})
        OPTIONAL MATCH (e)-[:STUDIED_IN]->(s:Study)
        WITH e, count(DISTINCT s) as study_count
        RETURN e.name as name, coalesce(e.study_count, study_count) as study_count
        ORDER BY study_count DESC
        LIMIT $limit
        """
        return self.execute_query(cypher, {"limit": limit})
    
    def get_relation_distribution(self, entity_name: str) -> List[Dict]:
        """获取实体的关系类型分布"""
        cypher = """
        MATCH (e:Entity)-[r]-()
        WHERE (e.name = $name OR e.canonical_name = toLower($name))
          AND type(r) <> 'STUDIED_IN'
        RETURN type(r) as relation_type, count(*) as count
        ORDER BY count DESC
        """
        return self.execute_query(cypher, {"name": entity_name})
    
    # ==================== 高级查询（研究者版） ====================
    
    def find_research_gaps(self, entity_type: str = "ClimateFactor") -> List[Dict]:
        """发现研究空白（被研究较少的实体）"""
        entity_type = _validate_label(entity_type)
        cypher = f"""
        MATCH (e:Entity:{entity_type})
        OPTIONAL MATCH (e)-[:STUDIED_IN]->(s:Study)
        WITH e, count(DISTINCT s) as study_count
        WHERE study_count < 5
        RETURN e.name as name, study_count
        ORDER BY study_count ASC
        LIMIT 20
        """
        return self.execute_query(cypher)
    
    def find_co_occurrence(self, entity1: str, min_studies: int = 2) -> List[Dict]:
        """找到与指定实体共同出现的其他实体"""
        cypher = """
        MATCH (e1:Entity)-[:STUDIED_IN]->(s:Study)<-[:STUDIED_IN]-(e2:Entity)
        WHERE (e1.name = $name OR e1.canonical_name = toLower($name)) AND e1 <> e2
        WITH e2, count(DISTINCT s) as共同研究数
        WHERE 共同研究数 >= $min_studies
        RETURN e2.name as entity, coalesce(e2.type, labels(e2)[0]) as type, 共同研究数
        ORDER BY 共同研究数 DESC
        LIMIT 15
        """
        return self.execute_query(cypher, {"name": entity1, "min_studies": min_studies})
    
    def get_subgraph(self, entity_name: str, depth: int = 2) -> Dict:
        """获取以某实体为中心的子图"""
        depth = _bounded_int(depth, 1, 3, 2)
        cypher = f"""
        MATCH path = (center:Entity)-[*1..{depth}]-(neighbor:Entity)
        WHERE center.name = $name OR center.canonical_name = toLower($name)
        WITH collect(DISTINCT center) + collect(DISTINCT neighbor) as nodes,
             collect(DISTINCT relationships(path)) as rels_lists
        UNWIND rels_lists as rels_list
        UNWIND rels_list as rel
        RETURN 
          [node in nodes | {{name: node.name, type: coalesce(node.type, labels(node)[0])}}] as nodes,
          [r in collect(DISTINCT rel) | {{
            source: startNode(r).name, 
            target: endNode(r).name, 
            type: type(r)
          }}] as relationships
        LIMIT 1
        """
        results = self.execute_query(cypher, {"name": entity_name})
        return results[0] if results else {"nodes": [], "relationships": []}

    def get_schema_overview(self) -> Dict:
        """Return node and relationship schema statistics for the research UI."""
        node_rows = self.execute_query(
            """
            MATCH (e:Entity)
            RETURN coalesce(e.type, labels(e)[0]) AS type,
                   count(e) AS count,
                   round(avg(coalesce(e.study_count, 0)), 2) AS mean_study_count
            ORDER BY count DESC
            """
        )
        relation_rows = self.execute_query(
            """
            MATCH (:Entity)-[r]->(:Entity)
            WHERE type(r) <> 'STUDIED_IN'
            RETURN type(r) AS relation_type,
                   count(r) AS edge_count,
                   sum(coalesce(r.support_count, 0)) AS support_count
            ORDER BY support_count DESC
            """
        )
        return {"nodes": node_rows, "relationships": relation_rows}

    def get_quality_snapshot(self) -> Dict:
        """Return a compact provenance and quality snapshot."""
        provenance = self.execute_query(
            """
            MATCH (a:EvidenceAssertion)
            OPTIONAL MATCH (a)-[:DERIVED_FROM]->(s:Study)
            RETURN count(a) AS assertions,
                   count(s) AS assertions_with_study,
                   count(DISTINCT s) AS supporting_studies
            """
        )
        entity_quality = self.execute_query(
            """
            MATCH (e:Entity)
            RETURN count(e) AS entities,
                   sum(CASE WHEN e.entity_id IS NULL OR e.canonical_name IS NULL THEN 1 ELSE 0 END) AS missing_ids
            """
        )
        relationship_quality = self.execute_query(
            """
            MATCH (:Entity)-[r]->(:Entity)
            WHERE type(r) <> 'STUDIED_IN'
            RETURN count(r) AS evidence_edges,
                   sum(CASE WHEN r.pmids IS NULL OR size(r.pmids) = 0 THEN 1 ELSE 0 END) AS missing_pmids,
                   round(avg(coalesce(r.support_count, 0)), 2) AS mean_support_count
            """
        )
        return {
            "provenance": provenance[0] if provenance else {},
            "entity_quality": entity_quality[0] if entity_quality else {},
            "relationship_quality": relationship_quality[0] if relationship_quality else {},
        }

    def get_temporal_coverage(self) -> Dict:
        """Return publication-year coverage for the live KG."""
        annual_rows = self.execute_query(
            """
            MATCH (s:Study)
            WITH coalesce(
                s.year,
                CASE
                    WHEN s.publication_date IS NULL THEN NULL
                    ELSE toInteger(substring(toString(s.publication_date), 0, 4))
                END
            ) AS year
            WHERE year IS NOT NULL AND year >= 1900 AND year <= 2100
            RETURN year, count(*) AS records
            ORDER BY year
            """
        )
        years = [int(row["year"]) for row in annual_rows if row.get("year") is not None]
        if not years:
            return {
                "source": "Neo4j",
                "publication_window_start": "2006/01/01",
                "publication_window_end": "current",
                "window_label": "near-20-year publication window",
                "start_year": None,
                "end_year": None,
                "covered_years": 0,
                "demo_study_nodes": 0,
                "annual_counts": [],
            }

        start_year = min(years)
        end_year = max(years)
        count_by_year = {int(row["year"]): int(row.get("records", 0)) for row in annual_rows}
        annual_counts = [
            {"year": year, "records": count_by_year.get(year, 0)}
            for year in range(start_year, end_year + 1)
        ]
        return {
            "source": "Neo4j",
            "publication_window_start": "2006/01/01",
            "publication_window_end": "current",
            "window_label": "near-20-year publication window",
            "start_year": start_year,
            "end_year": end_year,
            "covered_years": end_year - start_year + 1,
            "demo_study_nodes": sum(row["records"] for row in annual_counts),
            "annual_counts": annual_counts,
        }


if __name__ == "__main__":
    # 测试
    import os

    service = GraphQueryService(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        username=os.getenv("NEO4J_USERNAME", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "")
    )
    
    # 测试查询
    results = service.search_entity("temperature")
    print(f"搜索结果: {results}")
    
    stats = service.get_statistics()
    print(f"\n图谱统计: {stats}")
    
    service.close()
