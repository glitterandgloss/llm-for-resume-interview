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

# 模拟数据库
mock_experiences = [
    {
        "source": "牛客网",
        "title": "字节跳动NLP算法工程师一面面经",
        "content": "1. 自我介绍\n2. 项目深挖\n3. 手写Attention代码\n4. 算法题: 最长回文子串",
        "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "upvotes": 45
    },
    {
        "source": "牛客网",
        "title": "NLP算法工程师二面记录",
        "content": "1. Transformer原理\n2. BERT和GPT区别\n3. 多任务学习如何处理\n4. 算法题: 编辑距离",
        "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "upvotes": 32
    }
]

@app.post("/fetch_interviews")
async def fetch_interviews(request: Request):
    data = await request.json()
    position = data.get("position", "")
    skills = data.get("skills", [])
    
    # 简单过滤逻辑
    filtered = [exp for exp in mock_experiences 
                if position in exp["title"] and any(skill in exp["content"] for skill in skills)]
    
    # 模拟随机失败
    if random.random() < 0.1:
        return JSONResponse({"error": "Service temporarily unavailable"}, status_code=503)
    
    return JSONResponse(filtered)

if __name__ == "__main__":
    import uvicorn
    port = int(CONFIG["mcp_servers"]["niuke"].split(":")[-1])
    uvicorn.run(app, host="0.0.0.0", port=port) 