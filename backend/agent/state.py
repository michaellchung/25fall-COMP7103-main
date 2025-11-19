"""
对话状态管理
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class ItineraryStage(str, Enum):
    """行程规划阶段"""
    # 需求收集阶段
    GREETING = "greeting"
    COLLECTING_REQUIREMENTS = "collecting_requirements"
    CONFIRMING_REQUIREMENTS = "confirming_requirements"
    
    # 分步推荐阶段
    RECOMMENDING_TRANSPORT = "recommending_transport"
    WAITING_TRANSPORT_SELECTION = "waiting_transport_selection"
    
    RECOMMENDING_ATTRACTIONS = "recommending_attractions"
    WAITING_ATTRACTIONS_SELECTION = "waiting_attractions_selection"
    
    RECOMMENDING_FOOD = "recommending_food"
    WAITING_FOOD_SELECTION = "waiting_food_selection"
    
    RECOMMENDING_ACCOMMODATION = "recommending_accommodation"
    WAITING_ACCOMMODATION_SELECTION = "waiting_accommodation_selection"
    
    # 最终生成阶段
    GENERATING_FINAL_ITINERARY = "generating_final_itinerary"
    COMPLETED = "completed"


class UserRequirements(BaseModel):
    """用户需求数据模型"""
    destination: Optional[str] = None
    province: Optional[str] = None
    departure_city: Optional[str] = None  # 出发地
    days: Optional[int] = None
    budget: Optional[int] = None
    travel_dates: Optional[str] = None
    preferences: List[str] = Field(default_factory=list)
    companions: Optional[str] = None  # 同行类型：独行/情侣/家庭/朋友
    companions_count: Optional[int] = None  # 同行人数（包括自己）
    special_needs: Optional[str] = None
    
    def is_complete(self) -> bool:
        """检查必填项是否完整"""
        return all([
            self.destination,
            self.days,
            self.budget,
            len(self.preferences) > 0
        ])
    
    def missing_fields(self) -> List[str]:
        """返回缺失的字段"""
        missing = []
        if not self.destination:
            missing.append("目的地")
        if not self.days:
            missing.append("旅行天数")
        if not self.budget:
            missing.append("预算")
        if not self.preferences:
            missing.append("旅行偏好")
        return missing


class UserSelections(BaseModel):
    """用户在各阶段的选择记录"""
    
    # 交通选择
    transport_choice: Optional[Dict[str, Any]] = None
    # 格式: {"outbound": {...}, "return": {...}}
    
    # 景点选择（按天）
    attractions_by_day: Optional[Dict[int, List[Dict[str, Any]]]] = None
    # 格式: {1: [景点1, 景点2], 2: [景点3, 景点4], ...}
    
    # 美食选择（按天）
    food_by_day: Optional[Dict[int, List[Dict[str, Any]]]] = None
    # 格式: {1: [餐厅1, 餐厅2], 2: [餐厅3], ...}
    
    # 住宿选择
    accommodation_choice: Optional[Dict[str, Any]] = None


class ConversationState(BaseModel):
    """对话状态"""
    session_id: str
    user_requirements: UserRequirements = Field(default_factory=UserRequirements)
    user_selections: UserSelections = Field(default_factory=UserSelections)
    dialogue_history: List[Dict[str, str]] = Field(default_factory=list)
    tool_calls: List[Dict] = Field(default_factory=list)
    current_stage: ItineraryStage = ItineraryStage.GREETING
    created_at: datetime = Field(default_factory=datetime.now)
    last_recommendation_data: Optional[Dict[str, Any]] = None  # 保存最后一次推荐的数据
    
    def add_message(self, role: str, content: str):
        """添加对话消息"""
        self.dialogue_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_recent_history(self, n: int = 5) -> List[Dict[str, str]]:
        """获取最近n轮对话"""
        return self.dialogue_history[-n*2:] if self.dialogue_history else []
    
    def record_tool_call(self, tool_name: str, result: Dict):
        """记录工具调用"""
        self.tool_calls.append({
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })

