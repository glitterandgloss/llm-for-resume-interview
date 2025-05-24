import asyncio
import json
import os
from typing import List, Dict, Any
import httpx
from dataclasses import dataclass
from mcp_client import MCPClient

# 加载配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

@dataclass
class JobDescription:
    title: str
    skills: List[str]
    experience: str
    company: str = None

@dataclass
class InterviewExperience:
    source: str
    title: str
    content: str
    date: str
    upvotes: int = 0

async def analyze_with_spark(experiences: List[InterviewExperience], jd: JobDescription) -> str:
    """使用讯飞星火大模型分析面经"""
    prompt = f"""
    你是一个资深面试分析师，请根据以下岗位描述和面经数据，生成详细的面试准备报告。

    岗位描述:
    - 职位名称: {jd.title}
    - 技能要求: {', '.join(jd.skills)}
    - 经验要求: {jd.experience}
    - 公司: {jd.company or '未指定'}

    面经数据:
    {json.dumps([exp.__dict__ for exp in experiences], indent=2, ensure_ascii=False)}
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            CONFIG["spark_api"]["api_url"],
            headers={"Authorization": f"Bearer {CONFIG['spark_api']['api_key']}"},
            json={
                "header": {"app_id": CONFIG["spark_api"]["app_id"]},
                "parameter": {"chat": {"domain": "4.0Ultra"}},
                "payload": {"message": {"text": [{"role": "user", "content": prompt}]}}
            }
        )
        return response.json().get("payload", {}).get("choices", {}).get("text", [""])[0]

async def main():
    # 示例岗位描述
    jd = JobDescription(
        title="NLP算法工程师",
        skills=["Python", "深度学习", "自然语言处理", "Transformer"],
        experience="1-3年",
        company="字节跳动"
    )
    
    # 初始化MCP客户端
    mcp_client = MCPClient(CONFIG["mcp_servers"])
    
    print("开始爬取面经数据...")
    
    # 并行爬取各平台数据
    tasks = [
        mcp_client.fetch_niuke_experiences(jd),
        mcp_client.fetch_xiaohongshu_experiences(jd),
        mcp_client.fetch_zhihu_experiences(jd)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 合并结果
    all_experiences = []
    for exp_list in results:
        if isinstance(exp_list, list):
            all_experiences.extend(exp_list)
    
    print(f"共爬取到{len(all_experiences)}条面经数据")
    
    # 使用讯飞星火分析
    print("正在使用讯飞星火大模型分析数据...")
    analysis_result = await analyze_with_spark(all_experiences, jd)
    
    # 输出分析报告
    print("\n=== 面试准备报告 ===")
    print(analysis_result)

if __name__ == "__main__":
    asyncio.run(main()) 