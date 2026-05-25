"""
DeepSeek API entity-relation extractor
使用OpenAI兼容接口
"""

import json
import time
import logging
from typing import Dict, List, Optional
from openai import OpenAI

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


class DeepSeekExtractor:
    """DeepSeek model entity-relation extractor"""
    
    def __init__(self, api_key: str, model_name: str = "deepseek-v4-flash"):
        """
        初始化DeepSeek抽取器
        
        Args:
            api_key: DeepSeek API Key
            model_name: 模型名称 
                - "deepseek-v4-flash": model used in the manuscript extraction workflow
                - "deepseek-reasoner": optional reasoning model if configured by the user
        """
        self.api_key = api_key
        self.model_name = model_name
        
        # 使用OpenAI SDK连接DeepSeek API
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        logger.info(f"DeepSeek extractor initialized: {model_name}")
    
    def _call_api(self, messages: List[Dict], temperature: float = 0.3) -> Optional[str]:
        """
        调用DeepSeek API
        
        Args:
            messages: 消息列表
            temperature: 温度参数
        
        Returns:
            API响应文本，失败返回None
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=8192,
                stream=False
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}")
            return None
    
    def extract_from_text(self, pmid: str, title: str, text: str, 
                         prompt_type: str = "abstract") -> Optional[Dict]:
        """
        从文本中抽取实体关系
        
        Args:
            pmid: 文献PMID
            title: 文献标题
            text: 文献文本
            prompt_type: Prompt类型
        
        Returns:
            抽取结果字典，失败返回None
        """
        try:
            # 构建消息
            system_prompt = get_system_prompt()
            extraction_prompt = get_extraction_prompt(pmid, title, text, prompt_type)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": extraction_prompt}
            ]
            
            # 调用API
            logger.info(f"正在抽取 PMID:{pmid} 的实体关系...")
            response_text = self._call_api(messages)
            
            if not response_text:
                return None
            
            # 解析响应
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
        """解析JSON响应"""
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
        """从摘要中抽取"""
        try:
            prompt = ABSTRACT_EXTRACTION_PROMPT.format(
                pmid=pmid,
                title=title,
                abstract=abstract
            )
            
            messages = [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            logger.info(f"抽取摘要 PMID:{pmid}")
            response_text = self._call_api(messages)
            
            if not response_text:
                return None
            
            result = self._parse_json_response(response_text)
            
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

    def extract_quote_first_from_abstract(self, pmid: str, title: str, abstract: str) -> Optional[Dict]:
        """
        Quote-first extraction from an abstract.

        The prompt requires evidence_quote to be an exact abstract sentence. A
        deterministic post-check rejects selected relationships whose evidence
        quote is not an exact substring of the input abstract.
        """
        try:
            prompt = get_extraction_prompt(pmid, title, abstract, prompt_type="quote_first")
            messages = [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            logger.info(f"quote-first抽取 PMID:{pmid}")
            response_text = self._call_api(messages, temperature=0.0)
            if not response_text:
                return None
            result = self._parse_json_response(response_text)
            if not result:
                return None

            abstract_compact = " ".join((abstract or "").split())
            retained = []
            for relation in result.get("selected_relationships", []) or []:
                quote = " ".join(str(relation.get("evidence_quote", "")).split())
                if quote and quote in abstract_compact:
                    relation["evidence_quote_exactly_from_abstract"] = True
                    retained.append(relation)
                else:
                    relation["evidence_quote_exactly_from_abstract"] = False

            result["selected_relationships"] = retained
            result["post_validation"] = {
                "quote_exact_match_required": True,
                "retained_relationship_count": len(retained)
            }
            return {
                'pmid': pmid,
                'title': title,
                'extraction': result,
                'source': 'abstract',
                'model': self.model_name,
                'extraction_mode': 'quote_first_evidence_span_anchored'
            }

        except Exception as e:
            logger.error(f"quote-first摘要抽取失败 PMID:{pmid}: {str(e)}")
            return None
    
    def batch_extract(self, articles: List[Dict], use_abstract_only: bool = True,
                     delay: float = 1.0, max_retries: int = 3) -> List[Dict]:
        """批量抽取"""
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
        """保存抽取结果"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存: {output_file}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        
        extractor = DeepSeekExtractor(api_key=api_key)
        
        test_article = {
            'pmid': 'test001',
            'title': 'Test article',
            'abstract': 'Temperature affects arthritis pain. Lower temperature increases joint stiffness.'
        }
        
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
    else:
        print("用法: python deepseek_extractor.py YOUR_API_KEY")
