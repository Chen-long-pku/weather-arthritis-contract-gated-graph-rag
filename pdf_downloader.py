"""
PDF文献下载模块
支持多种渠道下载学术文献PDF
"""

import os
import requests
import time
import logging
from typing import Dict, List, Tuple
from pathlib import Path
import json
from urllib.parse import quote
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFDownloader:
    def __init__(self, output_dir: str = 'pdfs'):
        """
        初始化PDF下载器
        
        Args:
            output_dir: PDF保存目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        self.download_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'pmc_success': 0,
            'unpaywall_success': 0,
            'doi_success': 0,
            'failed_reasons': {}
        }
    
    def download_from_pmc(self, pmc_id: str, pmid: str) -> Tuple[bool, str]:
        """
        从PubMed Central下载开放获取文献
        
        Args:
            pmc_id: PMC ID (例如: PMC1234567)
            pmid: PubMed ID
            
        Returns:
            (是否成功, 文件路径或错误信息)
        """
        if not pmc_id:
            return False, "No PMC ID"
        
        # 确保PMC ID格式正确
        if not pmc_id.startswith('PMC'):
            pmc_id = f'PMC{pmc_id}'
        
        # 尝试多个PMC下载URL
        pmc_urls = [
            f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/',
            f'https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmc_id}&blobtype=pdf',
            f'https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/{pmc_id[3:5]}/{pmc_id[5:7]}/{pmc_id}.PMC.pdf'
        ]
        
        for url in pmc_urls:
            try:
                logger.debug(f"尝试PMC链接: {url}")
                response = requests.get(url, headers=self.headers, timeout=30, stream=True, allow_redirects=True)
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    # 检查内容
                    first_bytes = next(response.iter_content(chunk_size=1024), b'')
                    if first_bytes.startswith(b'%PDF'):
                        filename = os.path.join(self.output_dir, f'{pmid}_{pmc_id}.pdf')
                        
                        with open(filename, 'wb') as f:
                            f.write(first_bytes)
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        # 验证文件大小
                        if os.path.getsize(filename) > 10240:  # 至少10KB
                            logger.info(f"✓ PMC下载成功: {pmc_id}")
                            self.download_stats['pmc_success'] += 1
                            return True, filename
                        else:
                            os.remove(filename)
                            
            except Exception as e:
                logger.debug(f"PMC链接失败: {str(e)}")
                continue
        
        return False, "PMC not available"
    
    def download_from_unpaywall(self, doi: str, pmid: str) -> Tuple[bool, str]:
        """
        通过Unpaywall API查找开放获取版本
        
        Args:
            doi: DOI
            pmid: PubMed ID
            
        Returns:
            (是否成功, 文件路径或错误信息)
        """
        if not doi:
            return False, "No DOI"
        
        try:
            # Unpaywall API - 使用真实邮箱
            api_url = f'https://api.unpaywall.org/v2/{doi}?email=amberjay889@gmail.com'
            
            logger.debug(f"查询Unpaywall: {doi}")
            
            response = requests.get(api_url, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查所有可能的OA位置
                if data.get('is_oa', False):
                    # 尝试best_oa_location
                    best_loc = data.get('best_oa_location', {})
                    pdf_url = best_loc.get('url_for_pdf') or best_loc.get('url')
                    
                    if pdf_url:
                        success, result = self._download_pdf_from_url(pdf_url, pmid, 'unpaywall')
                        if success:
                            return success, result
                    
                    # 尝试其他oa_locations
                    for loc in data.get('oa_locations', []):
                        pdf_url = loc.get('url_for_pdf') or loc.get('url')
                        if pdf_url:
                            success, result = self._download_pdf_from_url(pdf_url, pmid, 'unpaywall')
                            if success:
                                return success, result
                    
                    return False, "No valid PDF URL"
                else:
                    return False, "Not OA"
            else:
                return False, f"API HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Unpaywall error: {str(e)}"
    
    def download_from_doi(self, doi: str, pmid: str) -> Tuple[bool, str]:
        """
        尝试通过DOI直接访问出版商
        
        Args:
            doi: DOI
            pmid: PubMed ID
            
        Returns:
            (是否成功, 文件路径或错误信息)
        """
        if not doi:
            return False, "No DOI"
        
        try:
            doi_url = f'https://doi.org/{doi}'
            
            logger.debug(f"尝试DOI解析: {doi}")
            
            # 获取重定向后的实际URL
            response = requests.get(doi_url, headers=self.headers, timeout=20, allow_redirects=True)
            
            if response.status_code == 200:
                actual_url = response.url
                
                # 扩展的PDF URL模式（针对不同出版商）
                pdf_patterns = []
                
                # ScienceDirect (Elsevier)
                if 'sciencedirect.com' in actual_url:
                    pdf_patterns.extend([
                        actual_url.replace('/abs/', '/pdfft?md5='),
                        actual_url.replace('/science/article/', '/science/article/pii/') + '/pdfft',
                        actual_url + '/pdfft'
                    ])
                
                # Springer
                elif 'springer.com' in actual_url:
                    pdf_patterns.append(actual_url.replace('/article/', '/content/pdf/') + '.pdf')
                
                # Nature
                elif 'nature.com' in actual_url:
                    pdf_patterns.append(actual_url + '.pdf')
                
                # Wiley
                elif 'wiley.com' in actual_url:
                    pdf_patterns.extend([
                        actual_url.replace('/abs/', '/pdfdirect/'),
                        actual_url.replace('/full/', '/pdfdirect/')
                    ])
                
                # 通用模式
                pdf_patterns.extend([
                    actual_url.replace('/abs/', '/pdf/'),
                    actual_url.replace('/abstract/', '/pdf/'),
                    actual_url.replace('/article/', '/pdf/'),
                    actual_url.replace('/full/', '/pdf/'),
                    actual_url + '.pdf',
                    actual_url + '/pdf'
                ])
                
                # 尝试所有模式
                for pdf_url in pdf_patterns:
                    if pdf_url != actual_url:
                        success, result = self._download_pdf_from_url(pdf_url, pmid, 'doi')
                        if success:
                            return success, result
                
                return False, "No PDF pattern matched"
            else:
                return False, f"DOI HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"DOI error: {str(e)}"
    
    def _download_pdf_from_url(self, url: str, pmid: str, source: str) -> Tuple[bool, str]:
        """
        从指定URL下载PDF
        
        Args:
            url: PDF URL
            pmid: PubMed ID
            source: 来源标识
            
        Returns:
            (是否成功, 文件路径或错误信息)
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=30, stream=True, allow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                
                # 读取前几个字节检查是否是PDF
                first_chunk = next(response.iter_content(chunk_size=1024), b'')
                
                # PDF文件以 %PDF 开头
                is_pdf = first_chunk.startswith(b'%PDF') or 'pdf' in content_type.lower()
                
                if is_pdf:
                    filename = os.path.join(self.output_dir, f'{pmid}_{source}.pdf')
                    
                    with open(filename, 'wb') as f:
                        f.write(first_chunk)
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # 验证文件大小
                    file_size = os.path.getsize(filename)
                    if file_size > 10240:  # 至少10KB
                        logger.info(f"✓ {source.upper()}下载成功: {pmid}")
                        self.download_stats[f'{source}_success'] += 1
                        return True, filename
                    else:
                        os.remove(filename)
                        return False, "File too small"
                else:
                    return False, "Not a PDF"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Download error: {str(e)}"
    
    def download_article(self, article: Dict) -> Dict:
        """
        尝试下载单篇文献（多渠道）
        
        Args:
            article: 文献信息字典
            
        Returns:
            下载结果字典
        """
        pmid = article['pmid']
        pmc_id = article.get('pmc_id', '')
        doi = article.get('doi', '')
        
        self.download_stats['total'] += 1
        
        result = {
            'pmid': pmid,
            'title': article['title'],
            'success': False,
            'source': None,
            'filepath': None,
            'error': None
        }
        
        # 检查是否已下载
        existing_files = list(Path(self.output_dir).glob(f'{pmid}_*.pdf'))
        if existing_files:
            result['success'] = True
            result['source'] = 'cached'
            result['filepath'] = str(existing_files[0])
            logger.info(f"文献已存在: {pmid}")
            self.download_stats['success'] += 1
            return result
        
        # 策略1: 尝试PMC（最可靠）
        if pmc_id:
            success, message = self.download_from_pmc(pmc_id, pmid)
            if success:
                result['success'] = True
                result['source'] = 'PMC'
                result['filepath'] = message
                self.download_stats['success'] += 1
                return result
            else:
                logger.debug(f"PMC失败 {pmid}: {message}")
        
        # 策略2: 尝试Unpaywall
        if doi:
            time.sleep(0.5)  # 避免请求过快
            success, message = self.download_from_unpaywall(doi, pmid)
            if success:
                result['success'] = True
                result['source'] = 'Unpaywall'
                result['filepath'] = message
                self.download_stats['success'] += 1
                return result
            else:
                logger.debug(f"Unpaywall失败 {pmid}: {message}")
        
        # 策略3: 尝试DOI直接访问
        if doi:
            time.sleep(0.5)
            success, message = self.download_from_doi(doi, pmid)
            if success:
                result['success'] = True
                result['source'] = 'DOI'
                result['filepath'] = message
                self.download_stats['success'] += 1
                return result
            else:
                logger.debug(f"DOI失败 {pmid}: {message}")
                result['error'] = message
        
        # 所有方法都失败
        self.download_stats['failed'] += 1
        
        # 记录失败原因
        if not pmc_id and not doi:
            reason = "No PMC ID or DOI"
        elif not pmc_id:
            reason = "No PMC ID (paywalled)"
        else:
            reason = "All methods failed"
        
        if reason not in self.download_stats['failed_reasons']:
            self.download_stats['failed_reasons'][reason] = 0
        self.download_stats['failed_reasons'][reason] += 1
        
        result['error'] = reason
        logger.warning(f"✗ 下载失败 {pmid}: {reason}")
        
        return result
    
    def batch_download(self, articles: List[Dict], max_count: int = None) -> List[Dict]:
        """
        批量下载文献
        
        Args:
            articles: 文献列表
            max_count: 最大下载数量（None表示全部）
            
        Returns:
            下载结果列表
        """
        if max_count:
            articles = articles[:max_count]
        
        logger.info(f"开始批量下载 {len(articles)} 篇文献...")
        
        results = []
        
        for i, article in enumerate(articles, 1):
            logger.info(f"进度: {i}/{len(articles)} - PMID: {article['pmid']}")
            
            result = self.download_article(article)
            results.append(result)
            
            # 每10篇休息一下
            if i % 10 == 0:
                logger.info(f"已处理 {i} 篇，休息2秒...")
                time.sleep(2)
            else:
                time.sleep(0.3)
        
        logger.info("批量下载完成！")
        self._print_stats()
        
        return results
    
    def _print_stats(self):
        """打印下载统计"""
        stats = self.download_stats
        logger.info("=" * 50)
        logger.info("下载统计报告")
        logger.info("=" * 50)
        logger.info(f"总数: {stats['total']}")
        logger.info(f"成功: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
        logger.info(f"失败: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
        logger.info(f"")
        logger.info(f"来源分布:")
        logger.info(f"  PMC: {stats['pmc_success']}")
        logger.info(f"  Unpaywall: {stats['unpaywall_success']}")
        logger.info(f"  DOI: {stats['doi_success']}")
        logger.info(f"")
        logger.info(f"失败原因:")
        for reason, count in stats['failed_reasons'].items():
            logger.info(f"  {reason}: {count}")
        logger.info("=" * 50)
    
    def save_results(self, results: List[Dict], output_file: str = 'download_results.json'):
        """保存下载结果"""
        output_path = os.path.join('data', output_file)
        os.makedirs('data', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'results': results,
                'stats': self.download_stats
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"下载结果已保存到: {output_path}")
        return output_path


def main():
    """主函数示例"""
    # 加载检索结果
    with open('data/pubmed_results.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # 创建下载器
    downloader = PDFDownloader(output_dir='pdfs')
    
    # 批量下载
    results = downloader.batch_download(articles, max_count=100)  # 先下载100篇测试
    
    # 保存结果
    downloader.save_results(results)


if __name__ == '__main__':
    main()
