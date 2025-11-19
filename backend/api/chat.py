"""
对话API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from loguru import logger

from agent.core import get_agent_core

router = APIRouter()


class ChatRequest(BaseModel):
    """对话请求模型"""
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None  # 用户选择数据


class ChatResponse(BaseModel):
    """对话响应模型"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ResetRequest(BaseModel):
    """重置请求模型"""
    session_id: str


@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    对话接口
    
    接收用户消息，返回Agent回复
    """
    try:
        logger.info(f"📨 API收到请求 - session: {request.session_id}")
        logger.info(f"💬 消息内容: {request.message}")
        logger.info(f"📦 selection数据: {request.selection}")
        
        # 获取Agent实例
        agent = get_agent_core()
        
        # 处理消息
        result = agent.process_message(
            session_id=request.session_id,
            user_message=request.message,
            selection=request.selection
        )
        
        logger.info(f"✅ API返回成功")
        
        return ChatResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        logger.error(f"对话处理失败: {e}", exc_info=True)
        return ChatResponse(
            success=False,
            error=str(e)
        )


@router.post("/chat/reset")
async def reset_chat(request: ResetRequest) -> ChatResponse:
    """
    重置对话
    """
    try:
        # 获取Agent实例
        agent = get_agent_core()
        
        # 重置会话
        agent.reset_session(request.session_id)
        
        return ChatResponse(
            success=True,
            data={"message": "对话已重置"}
        )
        
    except Exception as e:
        logger.error(f"重置对话失败: {e}", exc_info=True)
        return ChatResponse(
            success=False,
            error=str(e)
        )


@router.get("/chat/welcome")
async def get_welcome_message() -> ChatResponse:
    """
    获取欢迎消息
    """
    try:
        agent = get_agent_core()
        welcome_msg = agent.generate_welcome_message()
        
        return ChatResponse(
            success=True,
            data={"message": welcome_msg}
        )
        
    except Exception as e:
        logger.error(f"获取欢迎消息失败: {e}")
        return ChatResponse(
            success=False,
            error=str(e)
        )


@router.get("/attractions/{city}")
async def get_attractions(city: str, preferences: Optional[str] = None) -> ChatResponse:
    """
    获取景点信息（成员B接口）
    
    Args:
        city: 城市名称
        preferences: 偏好类别，逗号分隔
    """
    try:
        agent = get_agent_core()
        prefs = preferences.split(",") if preferences else []
        
        attractions = agent.rag_retriever.retrieve_attractions(
            city=city,
            preferences=prefs,
            top_k=10
        )
        
        return ChatResponse(
            success=True,
            data={
                "city": city,
                "attractions": [
                    {
                        "name": a.name,
                        "category": a.category,
                        "description": a.description,
                        "ticket_price": a.ticket_price,
                        "rating": a.rating,
                        "duration_hours": a.duration_hours,
                        "opening_hours": a.opening_hours
                    }
                    for a in attractions
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"获取景点失败: {e}")
        return ChatResponse(
            success=False,
            error=str(e)
        )


@router.get("/itinerary/{session_id}")
async def get_itinerary(session_id: str) -> ChatResponse:
    """
    获取已生成的行程（成员C接口）
    
    Args:
        session_id: 会话ID
    """
    try:
        agent = get_agent_core()
        state = agent.get_or_create_session(session_id)
        
        if state.current_stage != "generating":
            return ChatResponse(
                success=False,
                error="行程还未生成，请先完成旅行需求确认"
            )
        
        itinerary = agent._generate_itinerary(state)
        
        return ChatResponse(
            success=True,
            data=itinerary
        )
        
    except Exception as e:
        logger.error(f"获取行程失败: {e}")
        return ChatResponse(
            success=False,
            error=str(e)
        )

