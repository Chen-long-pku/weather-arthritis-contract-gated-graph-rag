"""
平台配置文件
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

# Neo4j配置
NEO4J_CONFIG = {
    "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    "username": os.getenv("NEO4J_USERNAME", "neo4j"),
    "password": os.getenv("NEO4J_PASSWORD", ""),
    "database": os.getenv("NEO4J_DATABASE", "neo4j")
}

# DeepSeek配置
DEEPSEEK_CONFIG = {
    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "model_name": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
    "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "temperature": 0.3,
    "max_tokens": 4096
}

# 数据路径
DATA_PATHS = {
    "extraction_results": ROOT_DIR / "data" / "extraction_results",
    "latest_results": ROOT_DIR / "data" / "extraction_results" / "extraction_results_20251210_183902.json"
}

# 平台角色配置
ROLE_CONFIG = {
    "public": {
        "name": "健康科普助手",
        "description": "面向普通公众，提供通俗易懂的健康科普",
        "llm_temperature": 0.5,  # 更生动
        "max_results": 5,
        "show_pmid": False,
        "show_technical": False
    },
    "medical": {
        "name": "临床辅助系统",
        "description": "面向医务工作者，提供专业临床参考",
        "llm_temperature": 0.3,  # 更准确
        "max_results": 10,
        "show_pmid": True,
        "show_technical": True
    },
    "researcher": {
        "name": "科研探索工具",
        "description": "面向研究人员，提供深度知识挖掘",
        "llm_temperature": 0.2,  # 最准确
        "max_results": 20,
        "show_pmid": True,
        "show_technical": True,
        "enable_cypher": True  # 允许Cypher查询
    }
}

# API配置
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "log_level": "info"
}

# Web配置
WEB_CONFIG = {
    "public_port": 8501,
    "medical_port": 8502,
    "researcher_port": 8503
}


def get_missing_platform_settings():
    """返回平台启动前缺失的关键配置项。"""
    missing = []
    if not DEEPSEEK_CONFIG["api_key"]:
        missing.append("DEEPSEEK_API_KEY")
    if not NEO4J_CONFIG["password"]:
        missing.append("NEO4J_PASSWORD")
    return missing
