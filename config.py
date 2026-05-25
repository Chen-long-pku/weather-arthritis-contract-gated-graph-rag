"""
配置文件
项目的全局配置参数
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")

# PubMed检索配置
PUBMED_CONFIG = {
    # 检索式已在 pubmed_searcher.py 中定义
    # 这里可以添加其他检索相关配置
    'max_retries': 3,  # 最大重试次数
    'retry_delay': 2,  # 重试延迟（秒）
    'batch_size': 100,  # 批量获取文献详情的批次大小
}

# PDF下载配置
DOWNLOAD_CONFIG = {
    'timeout': 30,  # 请求超时时间（秒）
    'delay_between_requests': 0.5,  # 请求间隔（秒）
    'delay_after_batch': 2,  # 每批次后休息时间（秒）
    'batch_size': 10,  # 每批次下载数量
    'max_file_size': 50 * 1024 * 1024,  # 最大文件大小（50MB）
    'min_file_size': 1024,  # 最小文件大小（1KB）
}

# 目录配置
DIRECTORY_CONFIG = {
    'data_dir': 'data',
    'pdf_dir': 'pdfs',
    'report_dir': 'reports',
    'log_dir': 'logs',
}

# LLM配置（后续阶段使用）
LLM_CONFIG = {
    'model': 'deepseek-v4-flash',
    'temperature': 0.3,
    'max_tokens': 4000,
}

# Neo4j配置（后续阶段使用）
NEO4J_CONFIG = {
    'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    'username': os.getenv('NEO4J_USERNAME', 'neo4j'),
    'password': os.getenv('NEO4J_PASSWORD', ''),  # 请在.env中配置
    'database': os.getenv('NEO4J_DATABASE', 'neo4j'),
}

# 实体类型定义（后续阶段使用）
ENTITY_TYPES = [
    'ChronicDisease',  # 常见慢性病
    'ArthritisType',  # 关节炎类型
    'ClimateFactor',  # 气候因素
    'Symptom',  # 症状
    'Mechanism',  # 机制
    'Treatment',  # 治疗方法
    'Population',  # 人群
    'Location',  # 地点
]

# 关系类型定义（后续阶段使用）
RELATION_TYPES = [
    'AFFECTS',  # 影响
    'CORRELATES_WITH',  # 相关
    'CAUSES',  # 导致
    'ALLEVIATES',  # 缓解
    'EXACERBATES',  # 加重
    'ASSOCIATED_WITH',  # 关联
]
