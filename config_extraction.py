"""
配置文件
实体抽取和知识图谱构建的配置参数
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

# API配置
API_CONFIG = {
    # Gemini配置
    "gemini": {
        "api_key": os.getenv("GEMINI_API_KEY", ""),  # 从环境变量读取
        "model_name": "gemini-2.0-flash",  # 可选: gemini-2.5-flash, gemini-1.5-pro
        "temperature": 0.3,
        "max_output_tokens": 8192,
        "proxy": os.getenv("HTTPS_PROXY", ""),  # 代理配置
    },
    # DeepSeek configuration used for extraction
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "model_name": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),  # model used in the manuscript run unless overridden
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),  # OpenAI兼容接口
        "temperature": 0.3,
        "max_output_tokens": 8192,
    },
}

# Neo4j配置
NEO4J_CONFIG = {
    "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    "username": os.getenv("NEO4J_USERNAME", "neo4j"),
    "password": os.getenv("NEO4J_PASSWORD", ""),
    "database": os.getenv("NEO4J_DATABASE", "neo4j"),  # 使用默认数据库
}

# 文件路径配置
PATH_CONFIG = {
    "data_dir": "data",
    "pdf_dir": "pdfs",
    "extraction_output_dir": "data/extraction_results",
    "metadata_file": "data/pubmed_results_20251206_162915.json",
}

# 处理配置
PROCESSING_CONFIG = {
    # 是否只使用摘要
    "use_abstract_only": True,
    # 是否使用PDF全文
    "use_fulltext": False,
    # 最大处理数量（None表示全部）
    "max_count": None,
    # API请求间隔（秒）
    "request_delay": 1.0,
    # 最大重试次数
    "max_retries": 3,
    # 批量处理大小
    "batch_size": 50,
}

# PDF解析配置
PDF_CONFIG = {
    # 解析方法：pypdf2, pdfplumber, auto
    "parser_method": "auto",
    # 是否只提取摘要
    "extract_abstract_only": False,
    # 最小文本长度（字符）
    "min_text_length": 100,
}

# 知识图谱构建配置
GRAPH_CONFIG = {
    # 是否清空现有数据
    "clear_existing": False,
    # 是否创建索引
    "create_indexes": True,
    # 是否合并相似实体
    "merge_similar_entities": False,
    # 相似度阈值
    "similarity_threshold": 0.9,
}


def get_api_key(model_type: str = "gemini") -> str:
    """
    获取API Key

    Args:
        model_type: 模型类型 ('gemini' 或 'deepseek')

    Returns:
        API Key
    """
    api_key = API_CONFIG.get(model_type, {}).get("api_key", "")

    if not api_key:
        raise ValueError(
            f"未设置{model_type}的API Key，请设置环境变量或修改config_extraction.py"
        )

    return api_key


def set_api_key(model_type: str, api_key: str):
    """
    设置API Key

    Args:
        model_type: 模型类型
        api_key: API密钥
    """
    if model_type in API_CONFIG:
        API_CONFIG[model_type]["api_key"] = api_key
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")


def validate_config() -> bool:
    """验证配置是否完整"""
    errors = []

    if not NEO4J_CONFIG["password"]:
        errors.append("未设置NEO4J_PASSWORD，请在.env中配置Neo4j密码")

    # 检查数据文件
    if not os.path.exists(PATH_CONFIG["metadata_file"]):
        errors.append(f"元数据文件不存在: {PATH_CONFIG['metadata_file']}")

    if PROCESSING_CONFIG["use_fulltext"] and not os.path.exists(PATH_CONFIG["pdf_dir"]):
        errors.append(f"PDF目录不存在: {PATH_CONFIG['pdf_dir']}")

    if errors:
        for error in errors:
            print(f"配置错误: {error}")
        return False

    return True


def print_config():
    """打印当前配置"""
    print("=" * 80)
    print("当前配置")
    print("=" * 80)

    print("\nAPI配置:")
    for model_type, config in API_CONFIG.items():
        api_key = config["api_key"]
        masked_key = api_key[:10] + "..." if len(api_key) > 10 else "未设置"
        print(f"  {model_type}:")
        print(f"    API Key: {masked_key}")
        print(f"    Model: {config['model_name']}")

    print("\nNeo4j配置:")
    print(f"  URI: {NEO4J_CONFIG['uri']}")
    print(f"  Username: {NEO4J_CONFIG['username']}")
    print(f"  Database: {NEO4J_CONFIG['database']}")

    print("\n处理配置:")
    print(f"  使用摘要: {PROCESSING_CONFIG['use_abstract_only']}")
    print(f"  使用全文: {PROCESSING_CONFIG['use_fulltext']}")
    print(f"  最大处理数: {PROCESSING_CONFIG['max_count'] or '全部'}")

    print("=" * 80)


if __name__ == "__main__":
    print_config()

    if validate_config():
        print("\n配置验证通过")
    else:
        print("\n配置验证失败")
