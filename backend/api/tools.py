"""
工具API
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any

router = APIRouter()


@router.get("/tools/weather/{city}")
async def get_weather(
    city: str,
    days: int = 7
):
    """
    获取天气信息
    """
    try:
        # TODO: 调用天气工具
        return {
            "success": True,
            "data": {
                "city": city,
                "forecast": []
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/tools/attractions")
async def search_attractions(
    city: Optional[str] = None,
    preferences: Optional[str] = None,
    top_k: int = 20
):
    """
    查询景点
    
    参数：
        city: 城市名称
        preferences: 偏好（逗号分隔，如"文化,美食"）
        top_k: 返回数量
    """
    try:
        # TODO: 调用景点查询工具
        prefs = preferences.split(",") if preferences else []
        
        return {
            "success": True,
            "data": {
                "attractions": [],
                "total": 0
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

