"""
Gemini API实体关系抽取器
"""

import json
import time
import logging
import os
from typing import Dict, List, Optional
import google.generativeai as genai

from .prompt_templates import (
    get_system_prompt,
    get_extraction_prompt,
    ABSTRACT_EXTRACTION_PROMPT
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GeminiExtractor:
    """Gemini模型实体关系抽取器"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash", proxy: str = None):
        """
        初始化Gemini抽取器
        
        Args:
            api_key: Google API Key
            model_name: 模型名称 (gemini-2.0-flash, gemini-2.5-flash, gemini-1.5-pro等)
            proxy: 代理地址 (例如: http://127.0.0.1:7897)
        """
        self.api_key = api_key
        self.model_name = model_name
        
        # 设置代理
        if proxy:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
            logger.info(f"使用代理: {proxy}")
        elif os.getenv('HTTPS_PROXY'):
            logger.info(f"使用环境变量代理: {os.getenv('HTTPS_PROXY')}")
        
        # 配置API
        genai.configure(api_key=api_key)
        
        # 初始化模型
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        logger.info(f"Gemini抽取器初始化完成: {model_name}")
    
    def extract_from_text(self, pmid: str, title: str, text: str, 
                         prompt_type: str = "abstract") -> Optional[Dict]:
        """
        从文本中抽取实体关系
        
        Args:
            pmid: 文献PMID
            title: 文献标题
            text: 文献文本
            prompt_type: Prompt类型 ('abstract' 或 'fulltext')
        
        Returns:
            抽取结果字典，失败返回None
        """
        try:
            # 构建Prompt
            system_prompt = get_system_prompt()
            extraction_prompt = get_extraction_prompt(pmid, title, text, prompt_type)
            
            # 组合完整Prompt
            full_prompt = f"{system_prompt}\n\n{extraction_prompt}"
            
            # 调用API
            logger.info(f"正在抽取 PMID:{pmid} 的实体关系...")
            response = self.model.generate_content(full_prompt)
            
            # 解析响应
            response_text = response.text.strip()
            
            # 尝试提取JSON
            result = self._parse_json_response(response_text)
            
            if result:
                logger.info(f"PMID:{pmid} 抽取成功")
                return {
                    'pmid': pmid,
                    'title': title,
                    'extraction': result,
                    'model': self.model_name
                }
            else:
                logger.warning(f"PMID:{pmid} 无法解析响应")
                return None
                
        except Exception as e:
            logger.error(f"PMID:{pmid} 抽取失败: {str(e)}")
            return None
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict]:
        """
        解析JSON响应
        
        Args:
            response_text: API响应文本
        
        Returns:
            解析的字典，失败返回None
        """
        # 尝试直接解析
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取JSON代码块
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试提取任何JSON对象
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        logger.warning("无法从响应中提取有效JSON")
        return None
    
    def extract_from_abstract(self, pmid: str, title: str, abstract: str) -> Optional[Dict]:
        """
        从摘要中抽取（简化版）
        
        Args:
            pmid: PMID
            title: 标题
            abstract: 摘要
        
        Returns:
            抽取结果
        """
        try:
            prompt = ABSTRACT_EXTRACTION_PROMPT.format(
                pmid=pmid,
                title=title,
                abstract=abstract
            )
            
            logger.info(f"抽取摘要 PMID:{pmid}")
            response = self.model.generate_content(prompt)
            
            result = self._parse_json_response(response.text.strip())
            
            if result:
                return {
                    'pmid': pmid,
                    'title': title,
                    'extraction': result,
                    'source': 'abstract',
                    'model': self.model_name
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"摘要抽取失败 PMID:{pmid}: {str(e)}")
            return None
    
    def batch_extract(self, articles: List[Dict], use_abstract_only: bool = True,
                     delay: float = 1.0, max_retries: int = 3) -> List[Dict]:
        """
        批量抽取
        
        Args:
            articles: 文献列表，每个包含 pmid, title, abstract/text
            use_abstract_only: 是否只使用摘要
            delay: 请求间隔（秒）
            max_retries: 最大重试次数
        
        Returns:
            抽取结果列表
        """
        results = []
        
        logger.info(f"开始批量抽取 {len(articles)} 篇文献")
        
        for idx, article in enumerate(articles, 1):
            pmid = article.get('pmid', '')
            title = article.get('title', '')
            
            if use_abstract_only:
                text = article.get('abstract', '')
            else:
                text = article.get('text', article.get('abstract', ''))
            
            if not text:
                logger.warning(f"[{idx}/{len(articles)}] PMID:{pmid} 无文本内容，跳过")
                continue
            
            # 重试机制
            success = False
            for attempt in range(max_retries):
                try:
                    if use_abstract_only:
                        result = self.extract_from_abstract(pmid, title, text)
                    else:
                        result = self.extract_from_text(pmid, title, text, 'fulltext')
                    
                    if result:
                        results.append(result)
                        logger.info(f"[{idx}/{len(articles)}] PMID:{pmid} 成功")
                        success = True
                        break
                    else:
                        logger.warning(f"[{idx}/{len(articles)}] PMID:{pmid} 抽取为空 (尝试 {attempt+1}/{max_retries})")
                        
                except Exception as e:
                    logger.error(f"[{idx}/{len(articles)}] PMID:{pmid} 出错 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                    
                if attempt < max_retries - 1:
                    time.sleep(delay * 2)
            
            if not success:
                logger.error(f"[{idx}/{len(articles)}] PMID:{pmid} 最终失败")
            
            # 请求间隔
            if idx < len(articles):
                time.sleep(delay)
            
            # 每10篇打印进度
            if idx % 10 == 0:
                logger.info(f"进度: {idx}/{len(articles)}, 成功: {len(results)}")
        
        logger.info(f"批量抽取完成: 总数 {len(articles)}, 成功 {len(results)}")
        return results
    
    def save_results(self, results: List[Dict], output_file: str):
        """
        保存抽取结果
        
        Args:
            results: 抽取结果列表
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存: {output_file}")


def test_gemini_extractor(api_key: str):
    """测试Gemini抽取器"""
    
    # 初始化
    extractor = GeminiExtractor(api_key=api_key, model_name="gemini-2.0-flash")
    
    # 测试样本
    test_article = {
        'pmid': '37078741',
        'title': 'Associations between weather conditions and osteoarthritis pain: a systematic review and meta-analysis',
        'abstract': '''Background: Patients with osteoarthritis often report weather conditions 
        influence their pain. This systematic review and meta-analysis examined associations 
        between weather conditions and pain in people with osteoarthritis. Methods: We searched 
        databases for studies examining associations between weather conditions (temperature, 
        humidity, atmospheric pressure) and osteoarthritis pain. Results: Temperature was 
        negatively associated with pain (lower temperature associated with higher pain). 
        Humidity showed positive associations with pain in some studies. Atmospheric pressure 
        changes were associated with increased pain sensitivity.'''
    }
    
    # 测试抽取
    result = extractor.extract_from_abstract(
        test_article['pmid'],
        test_article['title'],
        test_article['abstract']
    )
    
    if result:
        print("\n抽取成功!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("\n抽取失败")


if __name__ == '__main__':
    # 测试需要API Key
    import sys
    
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        test_gemini_extractor(api_key)
    else:
        print("用法: python gemini_extractor.py YOUR_API_KEY")
