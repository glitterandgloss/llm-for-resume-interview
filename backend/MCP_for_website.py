import os
import asyncio
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

# 导入自定义模块
from .spark_api import SparkAPI
from .crawlers import CrawlerManager, InterviewExperience

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="面经爬取与分析系统",
    description="基于MCP架构的智能面经爬取系统，使用讯飞星火大模型分析职位JD",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model: 数据模型定义
class JobDescription(BaseModel):
    """职位描述模型"""
    position: str
    company: str
    requirements: str
    
    class Config:
        schema_extra = {
            "example": {
                "position": "Python后端开发工程师",
                "company": "字节跳动",
                "requirements": "1. 熟练掌握Python编程语言，有Django/Flask框架经验\n2. 熟悉MySQL、Redis等数据库\n3. 了解微服务架构和容器化技术\n4. 有分布式系统开发经验优先"
            }
        }

class AnalysisResult(BaseModel):
    """分析结果模型"""
    keywords: List[str]
    experiences: List[Dict]
    total_count: int
    platform_stats: Dict[str, int]

# Context: 上下文管理和数据处理层
class InterviewAnalysisContext:
    """面经分析上下文管理器"""
    
    def __init__(self):
        """初始化上下文管理器"""
        self.spark_api = None
        self._initialize_spark_api()
    
    def _initialize_spark_api(self):
        """初始化讯飞星火API"""
        try:
            app_id = os.getenv("SPARK_APP_ID")
            api_key = os.getenv("SPARK_API_KEY")
            api_secret = os.getenv("SPARK_API_SECRET")
            
            if not all([app_id, api_key, api_secret]):
                logger.warning("讯飞星火API配置不完整，将使用模拟模式")
                self.spark_api = None
            else:
                self.spark_api = SparkAPI(app_id, api_key, api_secret)
                logger.info("讯飞星火API初始化成功")
        except Exception as e:
            logger.error(f"初始化讯飞星火API失败: {str(e)}")
            self.spark_api = None
    
    async def analyze_job_description(self, job: JobDescription) -> List[str]:
        """分析职位描述，提取关键词"""
        try:
            if self.spark_api:
                # 使用讯飞星火API分析
                keywords = await self.spark_api.analyze_job_keywords(
                    job.position, job.company, job.requirements
                )
                if keywords:
                    logger.info(f"成功提取关键词: {keywords}")
                    return keywords
            
            # 备用方案：基于规则的关键词提取
            logger.info("使用备用关键词提取方案")
            return self._extract_keywords_fallback(job)
            
        except Exception as e:
            logger.error(f"分析职位描述失败: {str(e)}")
            return self._extract_keywords_fallback(job)
    
    def _extract_keywords_fallback(self, job: JobDescription) -> List[str]:
        """备用关键词提取方案"""
        keywords = []
        
        # 从职位名称提取
        position_keywords = job.position.lower().split()
        keywords.extend(position_keywords)
        
        # 从要求中提取技术关键词
        tech_keywords = [
            'python', 'java', 'javascript', 'react', 'vue', 'django', 'flask',
            'mysql', 'redis', 'mongodb', 'docker', 'kubernetes', 'aws', 'git',
            'linux', 'nginx', 'spring', 'node.js', 'typescript', 'golang'
        ]
        
        requirements_lower = job.requirements.lower()
        for keyword in tech_keywords:
            if keyword in requirements_lower:
                keywords.append(keyword)
        
        # 添加通用面试关键词
        keywords.extend([job.position, '面试', '面经'])
        
        # 去重并返回前8个
        unique_keywords = list(dict.fromkeys(keywords))
        return unique_keywords[:8]

# Controller: 控制器层
class InterviewController:
    """面经控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.context = InterviewAnalysisContext()
        self.crawler_manager = CrawlerManager()
    
    async def process_job_analysis(self, job: JobDescription) -> AnalysisResult:
        """处理职位分析请求"""
        try:
            logger.info(f"开始分析职位: {job.position} - {job.company}")
            
            # 1. 分析职位描述，提取关键词
            keywords = await self.context.analyze_job_description(job)
            if not keywords:
                raise HTTPException(status_code=400, detail="无法提取有效关键词")
            
            logger.info(f"提取到关键词: {keywords}")
            
            # 2. 爬取面经
            experiences = await self.crawler_manager.crawl_all_platforms(keywords)
            
            # 3. 统计结果
            platform_stats = {}
            for exp in experiences:
                platform = exp.source
                platform_stats[platform] = platform_stats.get(platform, 0) + 1
            
            logger.info(f"爬取完成，共获取 {len(experiences)} 条面经")
            
            # 4. 构建返回结果
            result = AnalysisResult(
                keywords=keywords,
                experiences=[exp.to_dict() for exp in experiences],
                total_count=len(experiences),
                platform_stats=platform_stats
            )
            
            return result
            
        except Exception as e:
            logger.error(f"处理职位分析请求失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")

# 全局控制器实例
controller = InterviewController()

# API路由定义
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "面经爬取与分析系统",
        "version": "1.0.0",
        "description": "基于MCP架构的智能面经爬取系统"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_job_and_crawl(job: JobDescription) -> AnalysisResult:
    """
    分析职位描述并爬取相关面经
    
    - **position**: 职位名称
    - **company**: 公司名称  
    - **requirements**: 职位要求描述
    """
    return await controller.process_job_analysis(job)

@app.post("/keywords")
async def extract_keywords_only(job: JobDescription) -> Dict[str, List[str]]:
    """
    仅提取职位关键词，不进行爬取
    """
    try:
        keywords = await controller.context.analyze_job_description(job)
        return {"keywords": keywords}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/platforms")
async def get_supported_platforms():
    """获取支持的平台列表"""
    return {
        "platforms": ["牛客网", "知乎", "小红书"],
        "description": "当前支持的面经爬取平台"
    }

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}")
    return {"error": "服务器内部错误", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "MCP_for_website:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
