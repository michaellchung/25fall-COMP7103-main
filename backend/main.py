"""
TravelMate AI - FastAPI主程序
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from config.settings import settings
from api import chat, itinerary, rag, tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 TravelMate AI 正在启动...")
    print(f"📍 API地址: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 文档地址: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    
    yield
    
    # 关闭时执行
    print("👋 TravelMate AI 正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="个性化旅游攻略生成Agent - 基于LLM和RAG技术",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(chat.router, prefix="/api", tags=["对话"])
app.include_router(itinerary.router, prefix="/api", tags=["行程"])
app.include_router(rag.router, prefix="/api", tags=["RAG知识库"])
app.include_router(tools.router, prefix="/api", tags=["工具"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to TravelMate AI! 🌍",
        "docs": "/docs",
        "version": settings.APP_VERSION
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "服务器内部错误"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

