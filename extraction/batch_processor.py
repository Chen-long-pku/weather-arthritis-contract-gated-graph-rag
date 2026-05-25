"""
批量处理控制器
协调PDF解析、实体抽取、结果保存
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from .pdf_parser import PDFParser
from .gemini_extractor import GeminiExtractor
from .deepseek_extractor import DeepSeekExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """批量处理控制器"""
    
    def __init__(self, 
                 api_key: str,
                 model_type: str = "gemini",
                 model_name: Optional[str] = None):
        """
        初始化批量处理器
        
        Args:
            api_key: API密钥
            model_type: 模型类型 ('gemini' 或 'deepseek')
            model_name: 具体模型名称（可选）
        """
        self.api_key = api_key
        self.model_type = model_type
        
        # 初始化PDF解析器
        self.pdf_parser = PDFParser()
        
        # 初始化抽取器
        if model_type == "gemini":
            model_name = model_name or "gemini-2.0-flash"
            self.extractor = GeminiExtractor(api_key=api_key, model_name=model_name)
            logger.info(f"使用Gemini模型: {model_name}")
        elif model_type == "deepseek":
            model_name = model_name or "deepseek-v4-flash"
            self.extractor = DeepSeekExtractor(api_key=api_key, model_name=model_name)
            logger.info(f"使用DeepSeek模型: {model_name}")
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        self.results = []
    
    def process_from_metadata(self, 
                             metadata_file: str,
                             output_dir: str,
                             use_abstract_only: bool = True,
                             max_count: Optional[int] = None) -> List[Dict]:
        """
        从元数据文件处理
        
        Args:
            metadata_file: 文献元数据文件 (JSON格式)
            output_dir: 输出目录
            use_abstract_only: 是否只使用摘要
            max_count: 最大处理数量
        
        Returns:
            抽取结果列表
        """
        logger.info("=" * 80)
        logger.info("开始批量处理")
        logger.info("=" * 80)
        
        # 加载元数据
        logger.info(f"加载元数据: {metadata_file}")
        with open(metadata_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        logger.info(f"加载了 {len(articles)} 篇文献")
        
        # 限制数量
        if max_count and max_count < len(articles):
            articles = articles[:max_count]
            logger.info(f"限制处理数量: {max_count} 篇")
        
        # 准备文章数据
        processed_articles = []
        for article in articles:
            item = {
                'pmid': article.get('pmid', ''),
                'title': article.get('title', ''),
                'abstract': article.get('abstract', '')
            }
            processed_articles.append(item)
        
        # 批量抽取
        logger.info("\n开始实体关系抽取...")
        results = self.extractor.batch_extract(
            processed_articles,
            use_abstract_only=use_abstract_only,
            delay=1.0
        )
        
        # 保存结果
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'extraction_results_{timestamp}.json')
        
        self.extractor.save_results(results, output_file)
        
        # 生成统计报告
        self._generate_stats(results, output_dir, timestamp)
        
        logger.info("=" * 80)
        logger.info("批量处理完成")
        logger.info("=" * 80)
        
        self.results = results
        return results
    
    def process_from_pdfs(self,
                         pdf_dir: str,
                         metadata_file: str,
                         output_dir: str,
                         use_fulltext: bool = True,
                         max_count: Optional[int] = None) -> List[Dict]:
        """
        从PDF文件处理（使用全文）
        
        Args:
            pdf_dir: PDF文件夹路径
            metadata_file: 元数据文件（包含pmid, title信息）
            output_dir: 输出目录
            use_fulltext: 是否使用全文
            max_count: 最大处理数量
        
        Returns:
            抽取结果列表
        """
        logger.info("=" * 80)
        logger.info("开始PDF全文处理")
        logger.info("=" * 80)
        
        # 加载元数据
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        if max_count and max_count < len(metadata):
            metadata = metadata[:max_count]
        
        # 构建pmid到metadata的映射
        pmid_map = {item['pmid']: item for item in metadata}
        
        # 获取PDF文件列表
        pdf_files = list(Path(pdf_dir).glob('*.pdf'))
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        # 处理每个PDF
        processed_articles = []
        for pdf_file in pdf_files:
            # 从文件名提取PMID
            pmid = pdf_file.stem.split('_')[0]
            
            if pmid not in pmid_map:
                logger.warning(f"PMID {pmid} 不在元数据中，跳过")
                continue
            
            # 提取PDF文本
            logger.info(f"解析PDF: {pdf_file.name}")
            text = self.pdf_parser.extract_text_from_pdf(str(pdf_file))
            
            if not text:
                logger.warning(f"PDF解析失败: {pdf_file.name}")
                continue
            
            # 清理文本
            text = self.pdf_parser.clean_text(text)
            
            # 如果不用全文，只提取摘要
            if not use_fulltext:
                text = self.pdf_parser.extract_abstract_only(text)
            
            # 添加到处理列表
            processed_articles.append({
                'pmid': pmid,
                'title': pmid_map[pmid].get('title', ''),
                'text': text
            })
        
        logger.info(f"成功解析 {len(processed_articles)} 个PDF")
        
        # 批量抽取
        logger.info("\n开始实体关系抽取...")
        results = self.extractor.batch_extract(
            processed_articles,
            use_abstract_only=False,
            delay=1.5
        )
        
        # 保存结果
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'extraction_fulltext_{timestamp}.json')
        
        self.extractor.save_results(results, output_file)
        
        # 生成统计报告
        self._generate_stats(results, output_dir, timestamp)
        
        logger.info("=" * 80)
        logger.info("PDF全文处理完成")
        logger.info("=" * 80)
        
        self.results = results
        return results
    
    def _generate_stats(self, results: List[Dict], output_dir: str, timestamp: str):
        """生成统计报告"""
        
        stats = {
            'total_articles': len(results),
            'model_used': self.model_type,
            'timestamp': timestamp,
            'entity_counts': {},
            'relation_counts': {},
            'total_entities': 0,
            'total_relations': 0
        }
        
        # 统计实体和关系
        for result in results:
            extraction = result.get('extraction', {})
            
            # 统计实体（适配DeepSeek格式）
            # 方式1：标准格式 entities列表
            entities = extraction.get('entities', [])
            stats['total_entities'] += len(entities)
            
            for entity in entities:
                entity_type = entity.get('type', 'Unknown')
                stats['entity_counts'][entity_type] = stats['entity_counts'].get(entity_type, 0) + 1
            
            # 方式2：DeepSeek格式 按类型分组
            for entity_type in ['arthritis_types', 'climate_factors', 'symptoms', 'mechanisms', 'populations']:
                entity_list = extraction.get(entity_type, [])
                if entity_list:
                    stats['total_entities'] += len(entity_list)
                    stats['entity_counts'][entity_type] = stats['entity_counts'].get(entity_type, 0) + len(entity_list)
            
            # 统计关系
            relationships = extraction.get('relationships', [])
            stats['total_relations'] += len(relationships)
            
            for rel in relationships:
                rel_type = rel.get('relationship_type', rel.get('relation', 'Unknown'))
                stats['relation_counts'][rel_type] = stats['relation_counts'].get(rel_type, 0) + 1
        
        # 保存统计
        stats_file = os.path.join(output_dir, f'extraction_stats_{timestamp}.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        # 打印统计
        logger.info("\n" + "=" * 80)
        logger.info("抽取统计")
        logger.info("=" * 80)
        logger.info(f"处理文献数: {stats['total_articles']}")
        logger.info(f"总实体数: {stats['total_entities']}")
        logger.info(f"总关系数: {stats['total_relations']}")
        
        logger.info("\n实体类型分布:")
        for entity_type, count in sorted(stats['entity_counts'].items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {entity_type}: {count}")
        
        logger.info("\n关系类型分布:")
        for rel_type, count in sorted(stats['relation_counts'].items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {rel_type}: {count}")
        
        logger.info("=" * 80)
        logger.info(f"统计报告已保存: {stats_file}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python batch_processor.py API_KEY [model_type]")
        print("model_type: gemini (默认) 或 deepseek")
        sys.exit(1)
    
    api_key = sys.argv[1]
    model_type = sys.argv[2] if len(sys.argv) > 2 else "gemini"
    
    # 测试
    processor = BatchProcessor(api_key=api_key, model_type=model_type)
    
    # 使用摘要处理
    results = processor.process_from_metadata(
        metadata_file='data/pubmed_results_20251206_162915.json',
        output_dir='data/extraction_results',
        use_abstract_only=True,
        max_count=10
    )
    
    print(f"\n处理完成，共抽取 {len(results)} 篇文献")
