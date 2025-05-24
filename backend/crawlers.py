import asyncio
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import List, Dict
import time
import random
from urllib.parse import quote

class InterviewExperience:
    """面经数据结构"""
    def __init__(self, source: str, title: str, content: str, url: str, author: str = ""):
        self.source = source
        self.title = title
        self.content = content
        self.url = url
        self.author = author
    
    def to_dict(self):
        return {
            "source": self.source,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "author": self.author
        }

class BaseCrawler:
    """爬虫基类"""
    def __init__(self):
        self.session = None
        self.delay_range = (1, 3)  # 请求延迟范围
    
    async def random_delay(self):
        """随机延迟，避免被反爬"""
        delay = random.uniform(*self.delay_range)
        await asyncio.sleep(delay)

class NowcoderCrawler(BaseCrawler):
    """牛客网爬虫"""
    
    async def search_interviews(self, keywords: List[str]) -> List[InterviewExperience]:
        """搜索牛客网面经"""
        experiences = []
        search_query = " ".join(keywords[:3]) + " 面经"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # 设置用户代理
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # 搜索URL
                search_url = f"https://www.nowcoder.com/search?query={quote(search_query)}&type=all"
                await page.goto(search_url, wait_until="networkidle")
                
                # 等待页面加载
                await page.wait_for_timeout(2000)
                
                # 查找面经相关内容
                items = await page.query_selector_all('.search-item, .feed-item, .discuss-item')
                
                for item in items[:10]:  # 获取前10个结果
                    try:
                        # 提取标题
                        title_elem = await item.query_selector('.title, .feed-title, h3, h4')
                        title = await title_elem.inner_text() if title_elem else "无标题"
                        
                        # 提取链接
                        link_elem = await item.query_selector('a')
                        url = await link_elem.get_attribute('href') if link_elem else ""
                        if url and not url.startswith('http'):
                            url = f"https://www.nowcoder.com{url}"
                        
                        # 提取内容摘要
                        content_elem = await item.query_selector('.content, .feed-content, .discuss-content')
                        content = await content_elem.inner_text() if content_elem else ""
                        content = content[:300] + "..." if len(content) > 300 else content
                        
                        # 过滤面经相关内容
                        if any(keyword in title.lower() for keyword in ['面经', '面试', 'interview']) or \
                           any(keyword in content.lower() for keyword in ['面经', '面试', 'interview']):
                            experiences.append(InterviewExperience(
                                source="牛客网",
                                title=title.strip(),
                                content=content.strip(),
                                url=url
                            ))
                        
                        await self.random_delay()
                        
                    except Exception as e:
                        print(f"提取牛客网内容时出错: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"牛客网爬取出错: {str(e)}")
            finally:
                await browser.close()
        
        return experiences

class ZhihuCrawler(BaseCrawler):
    """知乎爬虫"""
    
    async def search_interviews(self, keywords: List[str]) -> List[InterviewExperience]:
        """搜索知乎面经"""
        experiences = []
        search_query = " ".join(keywords[:3]) + " 面经"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # 设置用户代理
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # 搜索URL
                search_url = f"https://www.zhihu.com/search?type=content&q={quote(search_query)}"
                await page.goto(search_url, wait_until="networkidle")
                
                # 等待页面加载
                await page.wait_for_timeout(3000)
                
                # 查找搜索结果
                items = await page.query_selector_all('.SearchResult-Card, .List-item')
                
                for item in items[:10]:  # 获取前10个结果
                    try:
                        # 提取标题
                        title_elem = await item.query_selector('.SearchResult-title, .ContentItem-title')
                        title = await title_elem.inner_text() if title_elem else "无标题"
                        
                        # 提取链接
                        link_elem = await item.query_selector('a')
                        url = await link_elem.get_attribute('href') if link_elem else ""
                        if url and not url.startswith('http'):
                            url = f"https://www.zhihu.com{url}"
                        
                        # 提取内容摘要
                        content_elem = await item.query_selector('.SearchResult-excerpt, .RichContent')
                        content = await content_elem.inner_text() if content_elem else ""
                        content = content[:300] + "..." if len(content) > 300 else content
                        
                        # 提取作者
                        author_elem = await item.query_selector('.UserLink-link, .AuthorInfo-name')
                        author = await author_elem.inner_text() if author_elem else ""
                        
                        # 过滤面经相关内容
                        if any(keyword in title.lower() for keyword in ['面经', '面试', 'interview']) or \
                           any(keyword in content.lower() for keyword in ['面经', '面试', 'interview']):
                            experiences.append(InterviewExperience(
                                source="知乎",
                                title=title.strip(),
                                content=content.strip(),
                                url=url,
                                author=author.strip()
                            ))
                        
                        await self.random_delay()
                        
                    except Exception as e:
                        print(f"提取知乎内容时出错: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"知乎爬取出错: {str(e)}")
            finally:
                await browser.close()
        
        return experiences

class XiaohongshuCrawler(BaseCrawler):
    """小红书爬虫"""
    
    async def search_interviews(self, keywords: List[str]) -> List[InterviewExperience]:
        """搜索小红书面经"""
        experiences = []
        search_query = " ".join(keywords[:3]) + " 面经"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # 设置用户代理
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # 搜索URL
                search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(search_query)}"
                await page.goto(search_url, wait_until="networkidle")
                
                # 等待页面加载
                await page.wait_for_timeout(3000)
                
                # 查找笔记内容
                items = await page.query_selector_all('.note-item, .feeds-page .note-item')
                
                for item in items[:8]:  # 获取前8个结果
                    try:
                        # 提取标题
                        title_elem = await item.query_selector('.title, .note-title')
                        title = await title_elem.inner_text() if title_elem else "无标题"
                        
                        # 提取链接
                        link_elem = await item.query_selector('a')
                        url = await link_elem.get_attribute('href') if link_elem else ""
                        if url and not url.startswith('http'):
                            url = f"https://www.xiaohongshu.com{url}"
                        
                        # 提取内容摘要
                        content_elem = await item.query_selector('.content, .note-content')
                        content = await content_elem.inner_text() if content_elem else ""
                        content = content[:200] + "..." if len(content) > 200 else content
                        
                        # 提取作者
                        author_elem = await item.query_selector('.author, .user-name')
                        author = await author_elem.inner_text() if author_elem else ""
                        
                        # 过滤面经相关内容
                        if any(keyword in title.lower() for keyword in ['面经', '面试', 'interview']) or \
                           any(keyword in content.lower() for keyword in ['面经', '面试', 'interview']):
                            experiences.append(InterviewExperience(
                                source="小红书",
                                title=title.strip(),
                                content=content.strip(),
                                url=url,
                                author=author.strip()
                            ))
                        
                        await self.random_delay()
                        
                    except Exception as e:
                        print(f"提取小红书内容时出错: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"小红书爬取出错: {str(e)}")
            finally:
                await browser.close()
        
        return experiences

class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self):
        self.crawlers = {
            "nowcoder": NowcoderCrawler(),
            "zhihu": ZhihuCrawler(),
            "xiaohongshu": XiaohongshuCrawler()
        }
    
    async def crawl_all_platforms(self, keywords: List[str]) -> List[InterviewExperience]:
        """并发爬取所有平台"""
        all_experiences = []
        
        # 创建爬取任务
        tasks = []
        for platform, crawler in self.crawlers.items():
            task = asyncio.create_task(crawler.search_interviews(keywords))
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 收集结果
        for result in results:
            if isinstance(result, list):
                all_experiences.extend(result)
            elif isinstance(result, Exception):
                print(f"爬取任务出错: {str(result)}")
        
        return all_experiences 