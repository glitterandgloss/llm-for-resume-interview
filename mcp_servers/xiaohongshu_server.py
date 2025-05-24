from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import random
import json
import os

# 加载配置
with open(os.path.join(os.path.dirname(__file__), '..', 'config.json'), 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

app = FastAPI()

# 模拟数据
mock_notes = [
    {
        "source": "小红书",
        "title": "字节NLP面试全流程分享",
        "content": "一共三轮技术面+HR面\n技术面主要考察: 1. 项目细节 2. 算法实现 3. 论文理解\nHR面问职业规划",
        "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "upvotes": 128
    },
    {
        "source": "小红书",
        "title": "NLP算法岗面试准备攻略",
        "content": "重点复习: 1. Transformer 2. 常见NLP任务 3. Python编程 4. 机器学习基础",
        "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
        "upvotes": 256
    }
]

@app.post("/search_notes")
async def search_notes(request: Request):
    data = await request.json()
    keywords = data.get("keywords", [])
    company = data.get("company", "")
    
    # 简单过滤逻辑
    filtered = [note for note in mock_notes 
                if any(kw in note["title"] or kw in note["content"] for kw in keywords)]
    
    if company:
        filtered = [note for note in filtered if company in note["title"]]
    
    return JSONResponse(filtered)

if __name__ == "__main__":
    import uvicorn
    port = int(CONFIG["mcp_servers"]["xiaohongshu"].split(":")[-1])
    uvicorn.run(app, host="0.0.0.0", port=port) 