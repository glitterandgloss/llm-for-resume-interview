import asyncio
import base64
import datetime
import hashlib
import hmac
import json
import websockets
import ssl
from typing import Dict, Optional, List
from urllib.parse import urlencode, quote

class SparkAPI:
    """讯飞星火认知大模型API封装类"""
    
    def __init__(self, app_id: str, api_key: str, api_secret: str, domain: str = "generalv3"):
        """
        初始化讯飞星火API
        :param app_id: 应用ID
        :param api_key: API密钥
        :param api_secret: API密钥secret
        :param domain: 领域版本，默认generalv3 (星火3.0)
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.domain = domain
        self.spark_url = "wss://spark-api.xf-yun.com/v3.1/chat"
        self.host = "spark-api.xf-yun.com"
        self.path = "/v3.1/chat"

    def _create_url(self) -> str:
        """生成鉴权URL"""
        # 生成RFC1123格式的时间戳
        now = datetime.datetime.utcnow()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 拼接字符串
        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"
        
        # 使用hmac-sha256进行加密
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode()
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
        
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数
        url = self.spark_url + '?' + urlencode(v)
        return url

    async def chat(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.5) -> Optional[str]:
        """
        发送对话请求
        :param prompt: 用户输入的文本
        :param max_tokens: 最大生成token数
        :param temperature: 温度参数，控制随机性
        :return: 模型返回的回答
        """
        url = self._create_url()
        
        # 构建请求数据
        data = {
            "header": {
                "app_id": self.app_id,
                "uid": "user123"
            },
            "parameter": {
                "chat": {
                    "domain": self.domain,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "user", "content": prompt}
                    ]
                }
            }
        }

        try:
            # 创建SSL上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            async with websockets.connect(url, ssl=ssl_context, ping_interval=None) as ws:
                await ws.send(json.dumps(data))
                
                # 接收完整响应
                full_response = ""
                async for message in ws:
                    response_dict = json.loads(message)
                    
                    # 检查错误
                    if response_dict["header"]["code"] != 0:
                        print(f"API Error: {response_dict['header']['message']}")
                        return None
                    
                    # 提取内容
                    choices = response_dict.get("payload", {}).get("choices", {})
                    if "text" in choices:
                        for text_item in choices["text"]:
                            full_response += text_item.get("content", "")
                    
                    # 检查是否结束
                    if response_dict["header"]["status"] == 2:
                        break
                
                return full_response.strip() if full_response else None
                
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return None

    async def analyze_job_keywords(self, position: str, company: str, requirements: str) -> List[str]:
        """
        分析职位描述，提取关键词
        :param position: 职位名称
        :param company: 公司名称
        :param requirements: 职位要求
        :return: 关键词列表
        """
        prompt = f"""
请分析以下职位描述，提取出最重要的技能关键词和面试考点，用于搜索相关面经。
请只返回关键词，每个关键词用逗号分隔，不要其他解释。

职位：{position}
公司：{company}
要求：{requirements}

请提取5-8个最核心的技术关键词和面试重点：
"""
        
        response = await self.chat(prompt, max_tokens=500, temperature=0.3)
        if response:
            # 解析关键词
            keywords = [kw.strip() for kw in response.split(',') if kw.strip()]
            return keywords[:8]  # 最多返回8个关键词
        return [] 