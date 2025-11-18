"""
Agent核心控制器
"""
from typing import Dict, Optional
from loguru import logger

from agent.dialogue import DialogueManager
from agent.state import ConversationState
from utils.llm import get_llm_client
from config import prompts
from rag.retriever import get_retriever
from planner.itinerary_generator import get_itinerary_generator


class AgentCore:
    """Agent核心控制器"""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.dialogue_manager = DialogueManager()
        self.rag_retriever = get_retriever()  # 成员B：RAG检索服务
        self.itinerary_generator = get_itinerary_generator()  # 成员C：行程生成器
        
        # 会话存储（生产环境应使用数据库）
        self.sessions: Dict[str, ConversationState] = {}
        
        logger.info("Agent核心控制器初始化完成")
    
    def get_or_create_session(self, session_id: str) -> ConversationState:
        """
        获取或创建会话
        
        Args:
            session_id: 会话ID
        
        Returns:
            ConversationState: 会话状态
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationState(
                session_id=session_id
            )
            logger.info(f"创建新会话: {session_id}")
        
        return self.sessions[session_id]
    
    def reset_session(self, session_id: str):
        """重置会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"会话已重置: {session_id}")
    
    def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict:
        """
        处理用户消息的主入口
        
        Args:
            session_id: 会话ID
            user_message: 用户消息
        
        Returns:
            Dict: 包含reply, stage, requirements等信息的响应
        """
        try:
            # 获取会话状态
            state = self.get_or_create_session(session_id)
            
            logger.info(
                f"处理消息 - session_id: {session_id}, "
                f"stage: {state.current_stage}, "
                f"message: {user_message[:50]}"
            )
            
            # 对话管理
            reply = self.dialogue_manager.process_user_input(state, user_message)
            
            # 构建响应
            response = {
                "reply": reply,
                "stage": state.current_stage,
                "requirements": {
                    "destination": state.user_requirements.destination,
                    "province": state.user_requirements.province,
                    "days": state.user_requirements.days,
                    "budget": state.user_requirements.budget,
                    "preferences": state.user_requirements.preferences,
                    "travel_dates": state.user_requirements.travel_dates,
                    "companions": state.user_requirements.companions
                }
            }
            
            # 如果进入生成阶段，生成完整的行程
            if state.current_stage == "generating":
                itinerary = self._generate_itinerary(state)
                response["itinerary"] = itinerary
                response["reply"] = f"{reply}\n\n✨ 已为您生成行程安排，详见下方详情。"
            
            logger.debug(f"响应: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"处理消息时出错: {e}", exc_info=True)
            return {
                "reply": "抱歉，处理您的消息时出现了问题。请重试或换个说法。",
                "stage": "error",
                "requirements": {},
                "error": str(e)
            }
    
    def generate_welcome_message(self) -> str:
        """生成欢迎消息"""
        return prompts.WELCOME_MESSAGE
    
    def _generate_itinerary(self, state: ConversationState) -> Dict:
        """
        生成行程（集成成员B和C的功能）
        
        Args:
            state: 对话状态
        
        Returns:
            完整的行程信息
        """
        try:
            req = state.user_requirements
            
            # 第一步：调用成员B的RAG检索服务，获取景点信息
            attractions = self.rag_retriever.retrieve_attractions(
                city=req.destination,
                preferences=req.preferences or [],
                top_k=15,
                budget_max=req.budget or 1000
            )
            
            # 将景点对象转换为字典
            attractions_dict = [
                {
                    "name": a.name,
                    "category": a.category,
                    "ticket_price": a.ticket_price,
                    "duration_hours": a.duration_hours,
                    "rating": a.rating,
                    "description": a.description
                }
                for a in attractions
            ]
            
            # 第二步：调用成员C的行程生成器，生成优化的行程
            itinerary = self.itinerary_generator.generate_itinerary(
                destination=req.destination,
                days=req.days or 3,
                budget=req.budget or 2000,
                preferences=req.preferences or [],
                attractions=attractions_dict,
                start_date=req.travel_dates,
                companions=req.companions,
                companions_count=req.companions_count,
                departure_city=req.departure_city
            )
            
            logger.info(f"行程生成完成: {req.destination}")
            return itinerary
        
        except Exception as e:
            logger.error(f"生成行程时出错: {e}", exc_info=True)
            return {
                "error": str(e),
                "message": "行程生成遇到问题，请稍后重试"
            }
    
    def decide_tool_calls(self, state: ConversationState) -> list:
        """
        决定需要调用哪些工具
        
        Args:
            state: 对话状态
        
        Returns:
            需要调用的工具列表
        """
        tools_needed = []
        req = state.user_requirements
        
        # 如果进入生成阶段，需要调用工具
        if state.current_stage == "generating":
            # 天气查询
            if req.destination:
                tools_needed.append({
                    "tool": "weather",
                    "params": {
                        "city": req.destination,
                        "days": req.days or 7
                    }
                })
            
            # 景点查询
            if req.destination and req.preferences:
                tools_needed.append({
                    "tool": "attractions",
                    "params": {
                        "city": req.destination,
                        "preferences": req.preferences,
                        "top_k": 20
                    }
                })
        
        return tools_needed


# 全局Agent实例
_agent_core = None

def get_agent_core() -> AgentCore:
    """获取全局Agent实例（单例模式）"""
    global _agent_core
    if _agent_core is None:
        _agent_core = AgentCore()
    return _agent_core

