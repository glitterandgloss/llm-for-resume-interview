import httpx
import asyncio
from typing import List
from dataclasses import asdict

class MCPClient:
    def __init__(self, server_config: dict):
        self.servers = server_config
    
    async def _fetch_from_server(self, server_name: str, endpoint: str, params: dict) -> List:
        """通用MCP请求方法"""
        url = f"{self.servers[server_name]}/{endpoint}"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                url,
                json=params,
                headers={"User-Agent": "MCP Interview Crawler"}
            )
            response.raise_for_status()
            return [self._create_interview_experience(exp) for exp in response.json()]
    
    def _create_interview_experience(self, data):
        """创建InterviewExperience对象"""
        from main import InterviewExperience
        return InterviewExperience(**data)
    
    async def fetch_niuke_experiences(self, jd) -> List:
        """从牛客网获取面经"""
        params = {
            "position": jd.title,
            "skills": jd.skills,
            "experience": jd.experience,
            "company": jd.company
        }
        return await self._fetch_from_server("niuke", "fetch_interviews", params)
    
    async def fetch_xiaohongshu_experiences(self, jd) -> List:
        """从小红书获取面经"""
        params = {
            "position": jd.title,
            "keywords": jd.skills + ["面试", "面经"],
            "company": jd.company
        }
        return await self._fetch_from_server("xiaohongshu", "search_notes", params)
    
    async def fetch_zhihu_experiences(self, jd) -> List:
        """从知乎获取面经"""
        params = {
            "query": f"{jd.title} 面试 {jd.company or ''}",
            "skills": jd.skills
        }
        return await self._fetch_from_server("zhihu", "search_answers", params) 