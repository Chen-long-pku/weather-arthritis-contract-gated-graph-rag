"""
PubMed文献检索模块
用于从PubMed检索气候敏感性常见慢性病文献；关节炎pilot可通过环境变量保留。
"""

import time
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

try:
    from Bio import Entrez
except ImportError:
    Entrez = None

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PubMedSearcher:
    def __init__(self, email: str, api_key: str = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        初始化PubMed检索器
        
        Args:
            email: 用户邮箱（NCBI要求）
            api_key: NCBI API密钥（可选，但有助于提高请求速率）
            start_date: 文献发表日期起点，默认使用近20年窗口
            end_date: 文献发表日期终点，默认使用当天
        """
        if Entrez is None:
            raise ImportError("缺少Biopython依赖，请先安装：pip install biopython")
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key
        self.start_date = self._normalise_pubmed_date(
            start_date or os.getenv("PUBMED_START_DATE") or f"{datetime.now().year - 20}/01/01"
        )
        env_end = end_date or os.getenv("PUBMED_END_DATE") or "today"
        self.end_date = (
            datetime.now().strftime("%Y/%m/%d")
            if str(env_end).strip().lower() in {"", "today", "auto", "current"}
            else self._normalise_pubmed_date(str(env_end))
        )
        self.disease_scope = os.getenv("PUBMED_DISEASE_SCOPE", "common_chronic").strip().lower()
        self.search_query = self._build_search_query()

    @staticmethod
    def _normalise_pubmed_date(value: str) -> str:
        """Normalize YYYY-MM-DD or YYYY/MM/DD into PubMed-friendly YYYY/MM/DD."""
        return str(value).strip().replace("-", "/")
        
    def _build_search_query(self) -> str:
        """构建检索查询语句"""
        arthritis_terms = (
            '("arthritis"[MeSH Terms] OR arthritis[tiab] OR '
            '"osteoarthritis"[MeSH Terms] OR osteoarthritis[tiab] OR '
            '"rheumatoid arthritis"[MeSH Terms] OR "rheumatoid arthritis"[tiab] OR '
            '"inflammatory joint disease"[tiab])'
        )

        chronic_disease_terms = (
            '("chronic disease"[MeSH Terms] OR "chronic disease"[tiab] OR '
            '"cardiovascular diseases"[MeSH Terms] OR "cardiovascular disease"[tiab] OR '
            '"hypertension"[MeSH Terms] OR hypertension[tiab] OR '
            '"heart failure"[MeSH Terms] OR "heart failure"[tiab] OR '
            '"ischemic heart disease"[tiab] OR "coronary disease"[MeSH Terms] OR '
            '"pulmonary disease, chronic obstructive"[MeSH Terms] OR COPD[tiab] OR '
            '"chronic obstructive pulmonary disease"[tiab] OR '
            '"asthma"[MeSH Terms] OR asthma[tiab] OR '
            '"diabetes mellitus"[MeSH Terms] OR diabetes[tiab] OR '
            '"kidney diseases"[MeSH Terms] OR "chronic kidney disease"[tiab] OR '
            '"mental disorders"[MeSH Terms] OR "mental health"[tiab] OR depression[tiab] OR '
            '"chronic pain"[MeSH Terms] OR "chronic pain"[tiab] OR '
            '"multimorbidity"[tiab] OR multimorbidity[tiab] OR '
            f'{arthritis_terms})'
        )
        
        climate_terms = (
            '("weather"[MeSH Terms] OR weather[tiab] OR '
            '"meteorological factors"[tiab] OR meteorology[tiab] OR '
            '"climate change"[MeSH Terms] OR "climate change"[tiab] OR climate[tiab] OR '
            '"temperature"[MeSH Terms] OR temperature[tiab] OR '
            '"barometric pressure"[tiab] OR "atmospheric pressure"[tiab] OR '
            'humidity[tiab] OR "precipitation"[tiab] OR "wind speed"[tiab] OR '
            '"cold exposure"[tiab] OR "heat wave"[tiab])'
        )
        
        date_filter = f'("{self.start_date}"[Date - Publication] : "{self.end_date}"[Date - Publication])'
        
        disease_terms = arthritis_terms if self.disease_scope in {"arthritis", "arthritis_pilot", "pilot"} else chronic_disease_terms
        full_query = f'{disease_terms} AND {climate_terms} AND {date_filter}'
        
        return full_query

    def get_search_scope(self) -> Dict[str, str]:
        """Return a machine-readable description of the KG literature scope."""
        return {
            "source": "PubMed",
            "publication_window_start": self.start_date,
            "publication_window_end": self.end_date,
            "window_label": "rolling near-20-year publication window",
            "disease_scope": self.disease_scope,
            "query": self.search_query,
        }
    
    def search(self, retmax: int = 10000) -> List[str]:
        """
        执行PubMed检索
        
        Args:
            retmax: 最大返回结果数
            
        Returns:
            PubMed ID列表
        """
        logger.info(f"开始检索PubMed...")
        logger.info(f"检索式: {self.search_query}")
        
        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=self.search_query,
                retmax=retmax,
                sort="relevance"
            )
            results = Entrez.read(handle)
            handle.close()
            
            id_list = results["IdList"]
            count = results["Count"]
            
            logger.info(f"检索完成！共找到 {count} 篇文献")
            logger.info(f"获取到 {len(id_list)} 个PubMed ID")
            
            return id_list
            
        except Exception as e:
            logger.error(f"检索失败: {str(e)}")
            raise

    def search_since(
        self,
        since_date: str,
        retmax: int = 500,
        datetype: str = "edat",
        sort: str = "pub+date",
    ) -> List[str]:
        """
        Incrementally search PubMed records updated or entered since a date.

        Args:
            since_date: Date in YYYY/MM/DD or YYYY-MM-DD format.
            retmax: Maximum number of PMIDs to return.
            datetype: PubMed date type. "edat" tracks Entrez entry/update date.
            sort: PubMed sort option.

        Returns:
            PubMed ID list sorted by PubMed response order.
        """
        normalized_since = since_date.replace("-", "/")
        max_date = datetime.now().strftime("%Y/%m/%d")

        logger.info("开始增量检索PubMed...")
        logger.info("检索起始日期: %s (%s)", normalized_since, datetype)

        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=self.search_query,
                retmax=retmax,
                sort=sort,
                datetype=datetype,
                mindate=normalized_since,
                maxdate=max_date,
            )
            results = Entrez.read(handle)
            handle.close()

            id_list = list(results.get("IdList", []))
            logger.info("增量检索完成：PubMed返回 %s 条，获取 %s 个PMID", results.get("Count", 0), len(id_list))
            return id_list

        except Exception as e:
            logger.error(f"增量检索失败: {str(e)}")
            raise
    
    def fetch_details(self, id_list: List[str], batch_size: int = 100) -> List[Dict]:
        """
        获取文献详细信息
        
        Args:
            id_list: PubMed ID列表
            batch_size: 批次大小
            
        Returns:
            文献详细信息列表
        """
        logger.info(f"开始获取 {len(id_list)} 篇文献的详细信息...")
        
        all_articles = []
        
        for i in range(0, len(id_list), batch_size):
            batch_ids = id_list[i:i + batch_size]
            logger.info(f"正在处理第 {i//batch_size + 1} 批 ({i+1}-{min(i+batch_size, len(id_list))}/{len(id_list)})")
            
            try:
                handle = Entrez.efetch(
                    db="pubmed",
                    id=batch_ids,
                    rettype="medline",
                    retmode="xml"
                )
                records = Entrez.read(handle)
                handle.close()
                
                for record in records['PubmedArticle']:
                    article_info = self._parse_article(record)
                    if article_info:
                        all_articles.append(article_info)
                
                # 避免请求过快
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"获取批次 {i//batch_size + 1} 失败: {str(e)}")
                time.sleep(2)
                continue
        
        logger.info(f"成功获取 {len(all_articles)} 篇文献的详细信息")
        return all_articles
    
    def _parse_article(self, record) -> Dict:
        """解析单篇文献信息"""
        try:
            article = record['MedlineCitation']['Article']
            
            # 基本信息
            pmid = str(record['MedlineCitation']['PMID'])
            title = article.get('ArticleTitle', 'No Title')
            
            # 摘要
            abstract = ''
            if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                abstract_parts = article['Abstract']['AbstractText']
                if isinstance(abstract_parts, list):
                    abstract = ' '.join([str(part) for part in abstract_parts])
                else:
                    abstract = str(abstract_parts)
            
            # 作者
            authors = []
            if 'AuthorList' in article:
                for author in article['AuthorList']:
                    if 'LastName' in author and 'ForeName' in author:
                        authors.append(f"{author['LastName']} {author['ForeName']}")
            
            # 期刊信息
            journal = article.get('Journal', {}).get('Title', 'Unknown Journal')
            
            # 发表日期
            pub_date = ''
            if 'Journal' in article and 'JournalIssue' in article['Journal']:
                pub_date_info = article['Journal']['JournalIssue'].get('PubDate', {})
                year = pub_date_info.get('Year', '')
                month = pub_date_info.get('Month', '')
                day = pub_date_info.get('Day', '')
                pub_date = f"{year}-{month}-{day}".strip('-')
            
            # DOI
            doi = ''
            if 'ELocationID' in article:
                for eloc in article['ELocationID']:
                    if eloc.attributes.get('EIdType') == 'doi':
                        doi = str(eloc)
                        break
            
            # PMC ID
            pmc_id = ''
            if 'PubmedData' in record and 'ArticleIdList' in record['PubmedData']:
                for article_id in record['PubmedData']['ArticleIdList']:
                    if article_id.attributes.get('IdType') == 'pmc':
                        pmc_id = str(article_id)
                        break
            
            return {
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'journal': journal,
                'publication_date': pub_date,
                'doi': doi,
                'pmc_id': pmc_id
            }
            
        except Exception as e:
            logger.error(f"解析文献失败: {str(e)}")
            return None
    
    def save_results(self, articles: List[Dict], output_dir: str = 'data'):
        """
        保存检索结果
        
        Args:
            articles: 文献列表
            output_dir: 输出目录
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存为JSON
        json_path = os.path.join(output_dir, f'pubmed_results_{timestamp}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        logger.info(f"结果已保存到: {json_path}")
        
        # 保存简化的CSV格式
        csv_path = os.path.join(output_dir, f'pubmed_results_{timestamp}.csv')
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write('PMID,Title,Journal,DOI,PMC_ID,Publication_Date,Authors_Count\n')
            for article in articles:
                f.write(f'"{article["pmid"]}","{article["title"]}","{article["journal"]}",'
                       f'"{article["doi"]}","{article["pmc_id"]}","{article["publication_date"]}",'
                       f'{len(article["authors"])}\n')
        logger.info(f"CSV已保存到: {csv_path}")
        
        return json_path, csv_path


def main():
    """主函数示例"""
    # 请替换为你的邮箱
    searcher = PubMedSearcher(email="your_email@example.com")
    
    # 执行检索
    id_list = searcher.search()
    
    # 获取详细信息
    articles = searcher.fetch_details(id_list)
    
    # 保存结果
    searcher.save_results(articles)


if __name__ == '__main__':
    main()
