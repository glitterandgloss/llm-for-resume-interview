from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import json
import os

# 加载配置
with open(os.path.join(os.path.dirname(__file__), '..', 'config.json'), 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

app = FastAPI()

# 模拟数据
mock_answers = [
    {
        "source": "知乎",
        "title": "如何准备NLP算法工程师的面试？",
        "content": "建议从以下几个方面准备:\n1. 扎实的机器学习基础\n2. 深入理解Transformer架构\n3. 熟悉PyTorch/TensorFlow\n4. 刷LeetCode中等难度题",
        "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "upvotes": 432
    },
    {
        "source": "知乎",
        "title": "字节跳动NLP面试体验",
        "content": "面试流程:\n1. 简历面\n2. 技术一面\n3. 技术二面\n4. HR面\n每轮都有算法题，难度中等偏上",
        "date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
        "upvotes": 189
    }
]

@app.post("/search_answers")
async def search_answers(request: Request):
    data = await request.json()
    query = data.get("query", "")
    skills = data.get("skills", [])
    
    # 简单过滤逻辑
    filtered = [ans for ans in mock_answers 
                if any(skill in ans["content"] for skill in skills)]
    
    return JSONResponse(filtered)

if __name__ == "__main__":
    import uvicorn
    port = int(CONFIG["mcp_servers"]["zhihu"].split(":")[-1])
    uvicorn.run(app, host="0.0.0.0", port=port) 