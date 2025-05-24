# 基于MCP架构的面经爬取与分析系统

这是一个基于MCP（Model-Context-Protocol）架构设计的面经爬取与分析系统，使用讯飞星火大模型进行面经分析，帮助求职者更好地准备面试。

## 系统架构

系统采用MCP架构，分为以下几个部分：

1. **MCP客户端**：负责协调各个服务器的请求和响应
2. **MCP服务器**：分别为牛客网、小红书和知乎提供专门的爬取服务
3. **讯飞星火API集成**：使用讯飞星火大模型分析面经数据

## 特点

- **分布式架构**：每个平台有独立的服务器组件
- **异步处理**：使用Python的asyncio进行并发请求
- **JSON配置**：使用JSON格式的配置文件，方便部署和维护
- **大模型分析**：利用讯飞星火大模型进行智能分析

## 安装与配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置文件

编辑`config.json`文件，填入您的讯飞星火API密钥和其他配置：

```json
{
  "spark_api": {
    "app_id": "your_app_id",
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "api_url": "wss://spark-api.xf-yun.com/v4.0/chat"
  },
  "crawler": {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "timeout": 10,
    "max_retries": 3
  },
  "mcp_servers": {
    "niuke": "http://localhost:8001",
    "xiaohongshu": "http://localhost:8002",
    "zhihu": "http://localhost:8003"
  }
}
```

## 使用方法

### 1. 启动MCP服务器

需要分别启动三个平台的MCP服务器：

```bash
# 终端1
python mcp_servers/niuke_server.py

# 终端2
python mcp_servers/xiaohongshu_server.py

# 终端3
python mcp_servers/zhihu_server.py
```

### 2. 运行主程序

```bash
python main.py
```

## 系统组件

- **main.py**：主程序，包含面经分析逻辑和示例用法
- **mcp_client.py**：MCP客户端，负责与各平台服务器通信
- **mcp_servers/niuke_server.py**：牛客网MCP服务器
- **mcp_servers/xiaohongshu_server.py**：小红书MCP服务器
- **mcp_servers/zhihu_server.py**：知乎MCP服务器
- **config.json**：系统配置文件

## 自定义开发

您可以通过以下方式扩展系统：

1. 添加更多平台的MCP服务器
2. 自定义面经分析提示词
3. 修改岗位描述和搜索条件

## 注意事项

- 本系统目前使用模拟数据，实际部署时需要实现真实的爬虫功能
- 使用讯飞星火API需要有效的API密钥
- 请遵守各平台的使用条款和爬虫政策
