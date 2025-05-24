#!/usr/bin/env python3
"""
面经爬取系统启动脚本
"""
import os
import sys
import uvicorn
from pathlib import Path

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查必要的环境变量
    required_vars = ["SPARK_APP_ID", "SPARK_API_KEY", "SPARK_API_SECRET"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  警告: 以下环境变量未配置:")
        for var in missing_vars:
            print(f"   - {var}")
        print("   系统将使用备用关键词提取方案")
    else:
        print("✅ 讯飞星火API配置完整")
    
    # 检查.env文件
    env_file = Path(".env")
    if env_file.exists():
        print("✅ 找到.env配置文件")
    else:
        print("⚠️  未找到.env文件，请参考.env.example创建配置")
    
    return True

def start_server():
    """启动服务器"""
    print("🚀 启动面经爬取系统...")
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 配置参数
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"📡 服务器地址: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print("📚 API文档: http://localhost:8000/docs")
    print("🔍 系统监控: http://localhost:8000/health")
    print("\n" + "="*50)
    
    try:
        # 启动服务器
        uvicorn.run(
            "backend.MCP_for_website:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if debug else "warning",
            access_log=debug
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 