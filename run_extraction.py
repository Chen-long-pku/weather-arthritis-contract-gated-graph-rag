"""
主运行脚本
执行完整的实体抽取和知识图谱构建流程
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extraction.batch_processor import BatchProcessor
from knowledge_graph.neo4j_connector import Neo4jConnector
from knowledge_graph.graph_builder import GraphBuilder
from config_extraction import (
    API_CONFIG, NEO4J_CONFIG, PATH_CONFIG, PROCESSING_CONFIG,
    set_api_key, validate_config, print_config
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def step1_extract_entities(api_key: str, model_type: str, use_fulltext: bool, max_count: int = None):
    """
    步骤1: 实体关系抽取
    
    Args:
        api_key: API密钥
        model_type: 模型类型 ('gemini' 或 'deepseek')
        use_fulltext: 是否使用全文
        max_count: 最大处理数量
    
    Returns:
        抽取结果文件路径
    """
    logger.info("\n" + "=" * 80)
    logger.info("步骤1: 实体关系抽取")
    logger.info("=" * 80)
    
    # 创建处理器
    processor = BatchProcessor(
        api_key=api_key,
        model_type=model_type,
        model_name=API_CONFIG[model_type]['model_name']
    )
    
    # 执行抽取
    if use_fulltext:
        logger.info("使用PDF全文进行抽取...")
        results = processor.process_from_pdfs(
            pdf_dir=PATH_CONFIG['pdf_dir'],
            metadata_file=PATH_CONFIG['metadata_file'],
            output_dir=PATH_CONFIG['extraction_output_dir'],
            use_fulltext=True,
            max_count=max_count
        )
    else:
        logger.info("使用摘要进行抽取...")
        results = processor.process_from_metadata(
            metadata_file=PATH_CONFIG['metadata_file'],
            output_dir=PATH_CONFIG['extraction_output_dir'],
            use_abstract_only=True,
            max_count=max_count
        )
    
    # 获取最新的结果文件
    output_dir = PATH_CONFIG['extraction_output_dir']
    result_files = [f for f in os.listdir(output_dir) if f.startswith('extraction_results_')]
    if result_files:
        latest_file = sorted(result_files)[-1]
        result_path = os.path.join(output_dir, latest_file)
        logger.info(f"\n抽取结果已保存: {result_path}")
        return result_path
    else:
        logger.error("未找到抽取结果文件")
        return None


def step2_build_graph(extraction_file: str, clear_existing: bool = False):
    """
    步骤2: 构建知识图谱
    
    Args:
        extraction_file: 抽取结果文件
        clear_existing: 是否清空现有数据
    """
    logger.info("\n" + "=" * 80)
    logger.info("步骤2: 构建知识图谱")
    logger.info("=" * 80)
    
    # 连接Neo4j
    connector = Neo4jConnector(
        uri=NEO4J_CONFIG['uri'],
        username=NEO4J_CONFIG['username'],
        password=NEO4J_CONFIG['password'],
        database=NEO4J_CONFIG['database']
    )
    
    # 验证连接
    if not connector.verify_connection():
        logger.error("Neo4j连接失败，请确保Neo4j数据库已启动")
        return False
    
    # 构建图谱
    builder = GraphBuilder(connector)
    builder.build_from_extraction_results(extraction_file, clear_existing=clear_existing)
    
    # 添加统计信息
    builder.add_entity_statistics()
    
    # 关闭连接
    connector.close()
    
    logger.info("\n知识图谱构建完成")
    return True


def run_full_pipeline(api_key: str, 
                      model_type: str = 'gemini',
                      use_fulltext: bool = False,
                      max_count: int = None,
                      clear_graph: bool = False,
                      skip_extraction: bool = False,
                      extraction_file: str = None):
    """
    运行完整流程
    
    Args:
        api_key: API密钥
        model_type: 模型类型
        use_fulltext: 是否使用全文
        max_count: 最大处理数量
        clear_graph: 是否清空现有图谱
        skip_extraction: 是否跳过抽取步骤
        extraction_file: 已有的抽取结果文件
    """
    start_time = datetime.now()
    
    logger.info("\n" + "=" * 80)
    logger.info("气候对关节炎影响知识图谱 - 实体抽取与图谱构建")
    logger.info("=" * 80)
    
    # 打印配置
    print_config()
    
    # 验证配置
    if not validate_config():
        logger.error("配置验证失败，退出")
        return
    
    # 步骤1: 实体抽取（如果不跳过）
    if not skip_extraction:
        result_file = step1_extract_entities(api_key, model_type, use_fulltext, max_count)
        if not result_file:
            logger.error("实体抽取失败，退出")
            return
    else:
        result_file = extraction_file
        if not result_file or not os.path.exists(result_file):
            logger.error("指定的抽取结果文件不存在")
            return
        logger.info(f"使用已有抽取结果: {result_file}")
    
    # 步骤2: 构建知识图谱
    success = step2_build_graph(result_file, clear_existing=clear_graph)
    
    if not success:
        logger.error("知识图谱构建失败")
        return
    
    # 完成
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("\n" + "=" * 80)
    logger.info("完整流程执行完成")
    logger.info("=" * 80)
    logger.info(f"总耗时: {duration}")
    logger.info(f"抽取结果: {result_file}")
    logger.info("=" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='气候对关节炎影响知识图谱 - 实体抽取与图谱构建',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:

1. 使用Gemini抽取摘要并构建图谱（推荐）:
   python run_extraction.py --api-key YOUR_GEMINI_KEY --model gemini

2. 使用DeepSeek抽取:
   python run_extraction.py --api-key YOUR_DEEPSEEK_KEY --model deepseek

3. 使用PDF全文抽取:
   python run_extraction.py --api-key YOUR_KEY --fulltext

4. 只处理前100篇测试:
   python run_extraction.py --api-key YOUR_KEY --max-count 100

5. 清空现有图谱重新构建:
   python run_extraction.py --api-key YOUR_KEY --clear-graph

6. 只构建图谱（使用已有抽取结果）:
   python run_extraction.py --skip-extraction --extraction-file results.json
        """
    )
    
    parser.add_argument('--api-key', type=str, required=True,
                       help='API密钥（Gemini或DeepSeek）')
    
    parser.add_argument('--model', type=str, default='gemini',
                       choices=['gemini', 'deepseek'],
                       help='使用的模型类型（默认: gemini）')
    
    parser.add_argument('--fulltext', action='store_true',
                       help='使用PDF全文而非摘要')
    
    parser.add_argument('--max-count', type=int, default=None,
                       help='最大处理文献数量（默认: 全部）')
    
    parser.add_argument('--clear-graph', action='store_true',
                       help='清空现有知识图谱')
    
    parser.add_argument('--skip-extraction', action='store_true',
                       help='跳过实体抽取步骤')
    
    parser.add_argument('--extraction-file', type=str, default=None,
                       help='已有的抽取结果文件（与--skip-extraction配合使用）')
    
    args = parser.parse_args()
    
    # 设置API Key
    set_api_key(args.model, args.api_key)
    
    # 运行流程
    run_full_pipeline(
        api_key=args.api_key,
        model_type=args.model,
        use_fulltext=args.fulltext,
        max_count=args.max_count,
        clear_graph=args.clear_graph,
        skip_extraction=args.skip_extraction,
        extraction_file=args.extraction_file
    )


if __name__ == '__main__':
    main()
