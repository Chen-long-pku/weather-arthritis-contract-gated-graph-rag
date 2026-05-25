"""
LLM服务 - 调用DeepSeek API
"""

from typing import List, Dict, Optional
import json
import logging
import ssl
import time
import urllib.error
import urllib.request

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMService:
    """LLM调用服务"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com",
                 model_name: str = "deepseek-v4-flash"):
        """初始化"""
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.client = None
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=120.0,  # 增加到120秒超时
                max_retries=3  # 增加到3次重试
            )
        except TypeError as exc:
            if "proxies" not in str(exc):
                raise
            logger.warning("OpenAI/httpx version mismatch detected; falling back to urllib client.")
        logger.info(f"LLM服务初始化完成: {model_name}")
    
    def generate(self, messages: List[Dict[str, str]], 
                temperature: float = 0.3,
                max_tokens: int = 4096) -> str:
        """
        生成回答
        
        Args:
            messages: 对话消息列表 [{"role": "system/user/assistant", "content": "..."}]
            temperature: 温度参数（0-1，越高越随机）
            max_tokens: 最大token数
        
        Returns:
            生成的文本
        """
        try:
            if self.client is None:
                answer = self._generate_with_urllib(messages, temperature, max_tokens)
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False
                )
                answer = response.choices[0].message.content
            logger.info(f"LLM生成成功，长度: {len(answer)}")
            return answer
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM生成失败: {error_msg}")
            
            # 提供更友好的错误信息
            if "Connection error" in error_msg or "timeout" in error_msg.lower():
                return "抱歉，无法连接到AI服务。请检查：\n1. 网络连接是否正常\n2. DEEPSEEK_API_KEY是否正确\n3. 是否需要配置代理"
            elif "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                return "API密钥验证失败，请检查DEEPSEEK_API_KEY环境变量是否正确设置"
            else:
                return f"抱歉，生成回答时出错：{error_msg}"

    def _generate_with_urllib(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Minimal OpenAI-compatible chat completion client.

        This fallback avoids local OpenAI/httpx dependency conflicts while
        preserving the same API request body.
        """

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        context = self._ssl_context()
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=120, context=context) as response:
                    data = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="ignore")
                raise RuntimeError(f"HTTP {exc.code}: {body[:500]}") from exc
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
        else:
            raise RuntimeError(str(last_error))
        return data["choices"][0]["message"]["content"]

    def _ssl_context(self) -> ssl.SSLContext:
        try:
            import certifi

            return ssl.create_default_context(cafile=certifi.where())
        except Exception:
            return ssl.create_default_context()
    
    def generate_stream(self, messages: List[Dict[str, str]],
                       temperature: float = 0.3,
                       max_tokens: int = 4096):
        """
        流式生成（支持逐字输出）
        
        Yields:
            生成的文本片段
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"流式生成失败: {str(e)}")
            yield f"错误：{str(e)}"


if __name__ == "__main__":
    import os
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("请设置DEEPSEEK_API_KEY环境变量")
        exit(1)
    
    service = LLMService(api_key=api_key)
    
    # 测试
    messages = [
        {"role": "system", "content": "你是一个医学知识助手"},
        {"role": "user", "content": "什么是类风湿关节炎？"}
    ]
    
    answer = service.generate(messages)
    print(f"回答：\n{answer}")
