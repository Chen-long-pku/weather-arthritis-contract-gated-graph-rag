"""
PDF解析器
提取PDF文件中的文本内容
"""

import os
import re
import logging
from typing import Dict, Optional
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFParser:
    """PDF文本提取器"""
    
    def __init__(self):
        """初始化PDF解析器"""
        self.available_parsers = []
        
        if PyPDF2:
            self.available_parsers.append('pypdf2')
        if pdfplumber:
            self.available_parsers.append('pdfplumber')
        
        if not self.available_parsers:
            logger.warning("没有可用的PDF解析库，请安装 PyPDF2 或 pdfplumber")
        else:
            logger.info(f"可用的PDF解析器: {', '.join(self.available_parsers)}")
    
    def extract_text_from_pdf(self, pdf_path: str, method: str = 'auto') -> Optional[str]:
        """
        从PDF提取文本
        
        Args:
            pdf_path: PDF文件路径
            method: 解析方法 ('pypdf2', 'pdfplumber', 'auto')
        
        Returns:
            提取的文本，失败返回None
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF文件不存在: {pdf_path}")
            return None
        
        # 自动选择方法
        if method == 'auto':
            if 'pdfplumber' in self.available_parsers:
                method = 'pdfplumber'
            elif 'pypdf2' in self.available_parsers:
                method = 'pypdf2'
            else:
                logger.error("没有可用的PDF解析方法")
                return None
        
        try:
            if method == 'pypdf2':
                return self._extract_with_pypdf2(pdf_path)
            elif method == 'pdfplumber':
                return self._extract_with_pdfplumber(pdf_path)
            else:
                logger.error(f"不支持的解析方法: {method}")
                return None
        except Exception as e:
            logger.error(f"PDF解析失败 {pdf_path}: {str(e)}")
            return None
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Optional[str]:
        """使用PyPDF2提取文本"""
        if not PyPDF2:
            logger.error("PyPDF2未安装")
            return None
        
        try:
            text = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            
            full_text = '\n'.join(text)
            return full_text if full_text.strip() else None
            
        except Exception as e:
            logger.error(f"PyPDF2提取失败: {str(e)}")
            return None
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Optional[str]:
        """使用pdfplumber提取文本"""
        if not pdfplumber:
            logger.error("pdfplumber未安装")
            return None
        
        try:
            text = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            
            full_text = '\n'.join(text)
            return full_text if full_text.strip() else None
            
        except Exception as e:
            logger.error(f"pdfplumber提取失败: {str(e)}")
            return None
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        从全文中提取不同部分
        
        Args:
            text: PDF全文
        
        Returns:
            分段字典 {'abstract': ..., 'methods': ..., 'results': ..., 'discussion': ...}
        """
        sections = {
            'abstract': '',
            'introduction': '',
            'methods': '',
            'results': '',
            'discussion': '',
            'conclusion': '',
            'full_text': text
        }
        
        # 标题关键词
        section_keywords = {
            'abstract': ['abstract', 'summary'],
            'introduction': ['introduction', 'background'],
            'methods': ['methods', 'methodology', 'materials and methods', 'patients and methods'],
            'results': ['results', 'findings'],
            'discussion': ['discussion'],
            'conclusion': ['conclusion', 'conclusions']
        }
        
        # 尝试按标题分割
        lines = text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # 检查是否是新的section标题
            for section_name, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    # 保存上一个section
                    if current_section and section_content:
                        sections[current_section] = '\n'.join(section_content)
                    
                    # 开始新section
                    current_section = section_name
                    section_content = []
                    break
            else:
                # 不是标题，加入当前section
                if current_section:
                    section_content.append(line)
        
        # 保存最后一个section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
        
        return sections
    
    def clean_text(self, text: str) -> str:
        """
        清理PDF提取的文本
        
        Args:
            text: 原始文本
        
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 移除页码和页眉页脚常见模式
        text = re.sub(r'\d+\s*\|\s*Page', '', text)
        text = re.sub(r'Page\s*\|\s*\d+', '', text)
        
        # 移除过短的行（可能是页码）
        lines = text.split('\n')
        lines = [line for line in lines if len(line.strip()) > 10]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def extract_abstract_only(self, text: str) -> str:
        """
        只提取摘要部分
        
        Args:
            text: PDF全文
        
        Returns:
            摘要文本
        """
        sections = self.extract_sections(text)
        abstract = sections.get('abstract', '')
        
        # 如果没有找到abstract section，尝试提取前500个词
        if not abstract or len(abstract) < 100:
            words = text.split()[:500]
            abstract = ' '.join(words)
        
        return self.clean_text(abstract)
    
    def get_text_stats(self, text: str) -> Dict:
        """
        获取文本统计信息
        
        Args:
            text: 文本
        
        Returns:
            统计信息字典
        """
        if not text:
            return {
                'char_count': 0,
                'word_count': 0,
                'line_count': 0
            }
        
        return {
            'char_count': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n'))
        }


def batch_extract_pdfs(pdf_dir: str, output_dir: str, use_abstract_only: bool = False):
    """
    批量提取PDF文本
    
    Args:
        pdf_dir: PDF文件夹路径
        output_dir: 输出文件夹路径
        use_abstract_only: 是否只提取摘要
    """
    parser = PDFParser()
    
    if not parser.available_parsers:
        logger.error("没有可用的PDF解析器")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = list(Path(pdf_dir).glob('*.pdf'))
    logger.info(f"找到 {len(pdf_files)} 个PDF文件")
    
    success_count = 0
    fail_count = 0
    
    for pdf_file in pdf_files:
        logger.info(f"处理: {pdf_file.name}")
        
        text = parser.extract_text_from_pdf(str(pdf_file))
        
        if text:
            # 清理文本
            text = parser.clean_text(text)
            
            # 如果只要摘要
            if use_abstract_only:
                text = parser.extract_abstract_only(text)
            
            # 保存
            output_file = Path(output_dir) / f"{pdf_file.stem}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            stats = parser.get_text_stats(text)
            logger.info(f"成功: {stats['word_count']} 词")
            success_count += 1
        else:
            logger.warning(f"失败: {pdf_file.name}")
            fail_count += 1
    
    logger.info(f"批量提取完成: 成功 {success_count}, 失败 {fail_count}")


if __name__ == '__main__':
    # 测试
    parser = PDFParser()
    
    test_pdf = 'pdfs/37078741_PMC10120534.pdf'
    if os.path.exists(test_pdf):
        text = parser.extract_text_from_pdf(test_pdf)
        if text:
            print("提取成功")
            print(f"字符数: {len(text)}")
            print(f"前500字符:\n{text[:500]}")
        else:
            print("提取失败")
    else:
        print(f"测试文件不存在: {test_pdf}")
