#!/usr/bin/env python3
"""
面经爬取系统测试脚本
"""
import asyncio
import json
import requests
import time
import base64
import hmac
import hashlib
import datetime
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any, Tuple
import re
from urllib.parse import quote, urlencode
import functools
import logging
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("MCP-System")

# 加载环境变量
load_dotenv()

# 缓存装饰器，减少API调用
def cache_response(ttl=3600):
    """缓存装饰器，用于减少重复请求
    
    Args:
        ttl: 缓存有效期(秒)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = hashlib.md5((str(args) + str(kwargs)).encode()).hexdigest()
            # 这里简化为内存缓存，实际应用可用Redis
            if not hasattr(wrapper, 'cache'):
                wrapper.cache = {}
            if cache_key in wrapper.cache and time.time() - wrapper.cache[cache_key]['time'] < ttl:
                logger.debug(f"Cache hit for {func.__name__}")
                return wrapper.cache[cache_key]['data']
            result = func(*args, **kwargs)
            wrapper.cache[cache_key] = {'data': result, 'time': time.time()}
            return result
        return wrapper
    return decorator

class RetryStrategy:
    """重试策略实现"""
    
    def __init__(self, max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
        """
        Args:
            max_retries: 最大重试次数
            delay: 初始延迟(秒)
            backoff: 退避倍数
            exceptions: 需要重试的异常类型
        """
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            current_delay = self.delay
            
            while retry_count < self.max_retries:
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    retry_count += 1
                    if retry_count >= self.max_retries:
                        logger.error(f"Max retries reached for {func.__name__}: {e}")
                        raise
                    
                    logger.warning(f"Retry {retry_count}/{self.max_retries} for {func.__name__} after {current_delay}s: {e}")
                    time.sleep(current_delay)
                    current_delay *= self.backoff
            
            return func(*args, **kwargs)  # 最后一次尝试
        return wrapper

class SparkAPI:
    """讯飞星火API封装"""
    
    def __init__(self, app_id: str, api_key: str, api_secret: str, domain: str = "generalv3"):
        """
        Args:
            app_id: 讯飞应用ID
            api_key: API密钥
            api_secret: API密钥secret
            domain: 模型领域，默认generalv3 (星火3.0)
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.domain = domain
        self.spark_url = "https://spark-api.xf-yun.com/v3.1/chat"
        self.host = "spark-api.xf-yun.com"
        self.path = "/v3.1/chat"
    
    def _create_auth_url(self) -> str:
        """生成鉴权URL"""
        # 生成RFC1123格式的时间戳
        now = datetime.datetime.utcnow()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 拼接签名原文
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
        
        # 构建URL参数
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        
        # 拼接鉴权参数
        url = self.spark_url + '?' + urlencode(v)
        return url
    
    @RetryStrategy(max_retries=3, delay=2)
    def chat(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.5) -> Dict:
        """发送对话请求
        
        Args:
            prompt: 用户输入的文本
            max_tokens: 最大生成token数
            temperature: 温度参数，控制随机性
            
        Returns:
            Dict: 解析后的响应结果
        """
        url = self._create_auth_url()
        
        # 构建请求数据
        data = {
            "header": {
                "app_id": self.app_id,
                "uid": f"mcp_user_{int(time.time())}"
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
        
        logger.info(f"Sending request to Spark API, prompt length: {len(prompt)}")
        
        try:
            # 发送请求
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json=data,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            # 解析响应
            if result["header"]["code"] != 0:
                logger.error(f"Spark API error: {result['header']['message']}")
                return {"error": result["header"]["message"]}
            
            content = result["payload"]["choices"]["text"][0]["content"]
            logger.info(f"Received response from Spark API, length: {len(content)}")
            return {"content": content}
            
        except Exception as e:
            logger.error(f"Spark API request failed: {str(e)}")
            return {"error": str(e)}

class UserAgentPool:
    """User-Agent池，用于反爬虫"""
    
    def __init__(self):
        self.agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        ]
        self.index = 0
    
    def get_random_agent(self) -> str:
        """获取随机User-Agent"""
        agent = self.agents[self.index]
        self.index = (self.index + 1) % len(self.agents)
        return agent

class SpiderEngine:
    """多平台爬虫引擎"""
    
    def __init__(self):
        self.ua_pool = UserAgentPool()
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.session = requests.Session()
    
    @cache_response(ttl=86400)  # 缓存一天
    @RetryStrategy(max_retries=3, delay=2)
    def fetch_page(self, url: str) -> str:
        """获取页面内容
        
        Args:
            url: 目标URL
            
        Returns:
            str: 页面HTML内容
        """
        headers = {
            'User-Agent': self.ua_pool.get_random_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.google.com/'
        }
        
        logger.info(f"Fetching page: {url}")
        
        try:
            # 随机延迟，避免被反爬
            time.sleep(1 + time.random())
            
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return ""
    
    def parse_nowcoder(self, html: str) -> List[Dict]:
        """解析牛客网面经
        
        Args:
            html: 页面HTML内容
            
        Returns:
            List[Dict]: 解析出的面经列表
        """
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        try:
            # 搜索结果页面
            items = soup.select('.discuss-main') or soup.select('.post-item')
            
            for item in items:
                try:
                    title_elem = item.select_one('.post-title') or item.select_one('a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    
                    # 获取链接
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = f"https://www.nowcoder.com{link}"
                    
                    # 获取内容摘要
                    content_elem = item.select_one('.post-content') or item.select_one('.post-topic-des')
                    content = content_elem.get_text(strip=True) if content_elem else ""
                    
                    # 获取作者信息
                    author_elem = item.select_one('.post-author') or item.select_one('.post-user')
                    author = author_elem.get_text(strip=True) if author_elem else "匿名用户"
                    
                    # 过滤非面经内容
                    if not any(keyword in title.lower() for keyword in ['面经', '面试', 'interview']):
                        continue
                    
                    posts.append({
                        'title': title,
                        'content': content[:500],  # 限制内容长度
                        'url': link,
                        'author': author,
                        'platform': 'nowcoder'
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing nowcoder item: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing nowcoder page: {str(e)}")
        
        logger.info(f"Parsed {len(posts)} posts from nowcoder")
        return posts
    
    def parse_xiaohongshu(self, html: str) -> List[Dict]:
        """解析小红书面经
        
        Args:
            html: 页面HTML内容
            
        Returns:
            List[Dict]: 解析出的面经列表
        """
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        try:
            # 小红书页面可能是动态加载的，这里尝试提取可见内容
            script_tags = soup.select('script')
            json_data = None
            
            # 尝试从script标签中提取数据
            for script in script_tags:
                script_text = script.string
                if script_text and 'window.__INITIAL_STATE__' in script_text:
                    json_str = script_text.split('window.__INITIAL_STATE__=')[1].split(';')[0]
                    try:
                        json_data = json.loads(json_str)
                        break
                    except:
                        pass
            
            # 如果找到了JSON数据
            if json_data and 'note' in json_data:
                notes = json_data['note'].get('noteList', [])
                for note in notes:
                    title = note.get('title', '无标题')
                    content = note.get('desc', '')
                    author = note.get('nickname', '匿名用户')
                    note_id = note.get('id', '')
                    url = f"https://www.xiaohongshu.com/discovery/item/{note_id}" if note_id else ""
                    
                    posts.append({
                        'title': title,
                        'content': content[:500],
                        'url': url,
                        'author': author,
                        'platform': 'xiaohongshu'
                    })
            else:
                # 备用方案：直接从HTML中提取
                items = soup.select('.note-item') or soup.select('.feed-item')
                
                for item in items:
                    try:
                        title_elem = item.select_one('.title') or item.select_one('.content-title')
                        title = title_elem.get_text(strip=True) if title_elem else "无标题"
                        
                        content_elem = item.select_one('.desc') or item.select_one('.content')
                        content = content_elem.get_text(strip=True) if content_elem else ""
                        
                        link_elem = item.select_one('a')
                        link = link_elem.get('href', '') if link_elem else ""
                        if link and not link.startswith('http'):
                            link = f"https://www.xiaohongshu.com{link}"
                        
                        author_elem = item.select_one('.author') or item.select_one('.nickname')
                        author = author_elem.get_text(strip=True) if author_elem else "匿名用户"
                        
                        posts.append({
                            'title': title,
                            'content': content[:500],
                            'url': link,
                            'author': author,
                            'platform': 'xiaohongshu'
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error parsing xiaohongshu item: {str(e)}")
                        continue
                
        except Exception as e:
            logger.error(f"Error parsing xiaohongshu page: {str(e)}")
        
        logger.info(f"Parsed {len(posts)} posts from xiaohongshu")
        return posts
    
    def parse_zhihu(self, html: str) -> List[Dict]:
        """解析知乎面经
        
        Args:
            html: 页面HTML内容
            
        Returns:
            List[Dict]: 解析出的面经列表
        """
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        try:
            # 知乎搜索结果页
            items = soup.select('.SearchResult-Card') or soup.select('.AnswerItem') or soup.select('.ContentItem')
            
            for item in items:
                try:
                    # 提取标题
                    title_elem = item.select_one('.ContentItem-title') or item.select_one('.QuestionItem-title')
                    title = title_elem.get_text(strip=True) if title_elem else "无标题"
                    
                    # 提取内容
                    content_elem = item.select_one('.RichContent-inner') or item.select_one('.SearchResult-snippet')
                    content = content_elem.get_text(strip=True) if content_elem else ""
                    
                    # 提取链接
                    link_elem = item.select_one('a')
                    link = link_elem.get('href', '') if link_elem else ""
                    if link and not link.startswith('http'):
                        link = f"https://www.zhihu.com{link}"
                    
                    # 提取作者
                    author_elem = item.select_one('.AuthorInfo-name') or item.select_one('.UserLink-link')
                    author = author_elem.get_text(strip=True) if author_elem else "匿名用户"
                    
                    # 过滤非面经内容
                    if not any(keyword in title.lower() or keyword in content.lower() for keyword in ['面经', '面试', 'interview']):
                        continue
                    
                    posts.append({
                        'title': title,
                        'content': content[:500],
                        'url': link,
                        'author': author,
                        'platform': 'zhihu'
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing zhihu item: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing zhihu page: {str(e)}")
        
        logger.info(f"Parsed {len(posts)} posts from zhihu")
        return posts
    
    def search_posts(self, keywords: List[str], platform: str = 'all') -> List[Dict]:
        """搜索各平台面经
        
        Args:
            keywords: 搜索关键词列表
            platform: 平台名称，'all'表示所有平台
            
        Returns:
            List[Dict]: 搜索结果
        """
        search_urls = []
        # 组合关键词，确保搜索面经
        search_query = " ".join(keywords[:3]) + " 面经"
        encoded_keyword = quote(search_query)
        
        if platform == 'all' or platform == 'nowcoder':
            search_urls.append((
                f'https://www.nowcoder.com/search?query={encoded_keyword}&type=post',
                'nowcoder'
            ))
        
        if platform == 'all' or platform == 'xiaohongshu':
            search_urls.append((
                f'https://www.xiaohongshu.com/search_result?keyword={encoded_keyword}',
                'xiaohongshu'
            ))
        
        if platform == 'all' or platform == 'zhihu':
            search_urls.append((
                f'https://www.zhihu.com/search?q={encoded_keyword}&type=content',
                'zhihu'
            ))
        
        results = []
        futures = []
        
        # 并发爬取各平台内容
        for url, platform in search_urls:
            futures.append(self.executor.submit(self.fetch_page, url))
        
        # 解析结果
        parsers = {
            'nowcoder': self.parse_nowcoder,
            'xiaohongshu': self.parse_xiaohongshu,
            'zhihu': self.parse_zhihu
        }
        
        for future, (url, platform) in zip(futures, search_urls):
            html = future.result()
            if html:
                parser = parsers.get(platform)
                if parser:
                    platform_results = parser(html)
                    results.extend(platform_results)
        
        return results

class AnalysisEngine:
    """分析引擎，使用讯飞星火大模型"""
    
    def __init__(self, spark_api: SparkAPI):
        """
        Args:
            spark_api: 讯飞星火API实例
        """
        self.spark_api = spark_api
    
    def extract_keywords(self, jd: str) -> List[str]:
        """从JD中提取关键词
        
        Args:
            jd: 岗位JD文本
            
        Returns:
            List[str]: 提取的关键词列表
        """
        prompt = f"""
请分析以下职位描述，提取5-8个关键技术词和面试考点，格式为逗号分隔的关键词列表，不要其他解释。

职位描述:
{jd}

关键词:
"""
        
        result = self.spark_api.chat(prompt, max_tokens=200, temperature=0.3)
        if "error" in result:
            logger.error(f"Failed to extract keywords: {result['error']}")
            # 备用方案：简单规则提取
            words = re.findall(r'\b[A-Za-z]+[+#]?\b', jd)
            tech_words = [w for w in words if len(w) > 2]
            return tech_words[:8]
        
        # 解析关键词列表
        content = result["content"]
        keywords = [kw.strip() for kw in content.split(',')]
        return [kw for kw in keywords if kw]
    
    def analyze_posts(self, posts: List[Dict], jd: str) -> Dict:
        """分析面经内容
        
        Args:
            posts: 面经列表
            jd: 岗位JD
            
        Returns:
            Dict: 分析结果
        """
        if not posts:
            return {
                "error": "No posts to analyze"
            }
        
        # 构建提示词
        posts_summary = "\n\n".join([
            f"【{p['platform']}】{p['title']}\n{p['content'][:300]}..."
            for p in posts[:10]  # 限制数量，避免超出token限制
        ])
        
        prompt = f"""
作为一位资深技术面试专家，请根据以下岗位JD和收集到的面经进行分析：

岗位JD:
{jd}

收集到的面经(共{len(posts)}篇):
{posts_summary}

请提供以下分析:
1. 技术考点: 列出5-10个高频技术考察点，按重要性排序
2. 典型面试问题: 列出8-12个典型面试问题，每个问题附带简要分析
3. 面试趋势: 总结该岗位近期面试趋势和变化
4. 准备建议: 给出针对性的准备建议

请以结构化方式呈现，使用Markdown格式。
"""
        
        result = self.spark_api.chat(prompt, max_tokens=2048, temperature=0.5)
        if "error" in result:
            logger.error(f"Failed to analyze posts: {result['error']}")
            return {"error": result["error"]}
        
        return {
            "analysis": result["content"],
            "post_count": len(posts),
            "platforms": list(set(p["platform"] for p in posts))
        }

class MCPSystem:
    """MCP协议主系统"""
    
    def __init__(self):
        """初始化MCP系统"""
        # 从环境变量获取配置
        spark_app_id = os.getenv("SPARK_APP_ID", "")
        spark_api_key = os.getenv("SPARK_API_KEY", "")
        spark_api_secret = os.getenv("SPARK_API_SECRET", "")
        
        # 初始化组件
        self.spark_api = SparkAPI(spark_app_id, spark_api_key, spark_api_secret)
        self.spider = SpiderEngine()
        self.analyzer = AnalysisEngine(self.spark_api)
    
    def process_jd(self, job_description: str, platform: str = 'all') -> Dict:
        """处理岗位JD，爬取并分析面经
        
        Args:
            job_description: 岗位JD文本
            platform: 指定平台，'all'表示所有平台
            
        Returns:
            Dict: 处理结果
        """
        logger.info(f"Processing JD: {job_description[:50]}...")
        
        try:
            # 1. 提取关键词
            logger.info("Extracting keywords from JD...")
            keywords = self.analyzer.extract_keywords(job_description)
            logger.info(f"Extracted keywords: {keywords}")
            
            if not keywords:
                return {"error": "Failed to extract keywords from JD"}
            
            # 2. 爬取面经
            logger.info(f"Searching posts with keywords: {keywords}")
            posts = self.spider.search_posts(keywords, platform)
            logger.info(f"Found {len(posts)} posts")
            
            if not posts:
                return {
                    "job_description": job_description,
                    "keywords": keywords,
                    "error": "No relevant posts found"
                }
            
            # 3. 分析面经
            logger.info("Analyzing posts...")
            analysis_result = self.analyzer.analyze_posts(posts, job_description)
            
            # 4. 整理结果
            result = {
                'job_description': job_description,
                'keywords': keywords,
                'posts_count': len(posts),
                'platforms': list(set(p['platform'] for p in posts)),
                'posts_sample': posts[:5],  # 样例面经
                'analysis': analysis_result.get("analysis", "")
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing JD: {str(e)}")
            return {"error": str(e)}

def create_env_file():
    """创建环境变量模板文件"""
    env_content = """# 讯飞星火API配置
SPARK_APP_ID=your_app_id_here
SPARK_API_KEY=your_api_key_here
SPARK_API_SECRET=your_api_secret_here

# 爬虫配置
MAX_RETRIES=3
REQUEST_TIMEOUT=30
CRAWL_DELAY=2
"""
    
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    logger.info("Created .env.example file. Please rename to .env and fill in your API keys.")

# 示例使用
if __name__ == "__main__":
    # 创建环境变量模板
    if not os.path.exists(".env.example"):
        create_env_file()
    
    # 初始化系统
    system = MCPSystem()
    
    # 示例岗位JD
    jd = """
    小红书NLP算法工程师岗位要求：
    1. 熟悉自然语言处理、机器学习、深度学习相关算法
    2. 熟悉Transformer、BERT、GPT等模型原理和实践
    3. 有推荐系统、搜索算法经验者优先
    4. 熟悉Python、PyTorch/TensorFlow框架
    5. 良好的算法基础和工程实现能力
    """
    
    # 处理JD
    result = system.process_jd(jd)
    
    # 打印结果
    print("\n分析结果:")
    if "error" in result:
        print(f"错误: {result['error']}")
    else:
        print(f"关键词: {result['keywords']}")
        print(f"面经数量: {result['posts_count']}")
        print(f"平台: {result['platforms']}")
        print("\n分析内容:")
        print(result['analysis']) 