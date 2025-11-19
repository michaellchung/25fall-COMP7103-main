"""
Agent核心控制器 - 分步交互式版本
"""
from typing import Dict, Optional, Any, List
from loguru import logger

from agent.dialogue import DialogueManager
from agent.state import ConversationState, ItineraryStage
from utils.llm import get_llm_client
from config import prompts
from tools.attraction import get_attraction_service
from planner.interactive_recommender import get_interactive_recommender
from tools.transport import get_transport_service
from tools.food import get_food_service
from tools.accommodation import get_accommodation_service


class AgentCore:
    """Agent核心控制器 - 支持分步交互式推荐"""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.dialogue_manager = DialogueManager()
        self.attraction_service = get_attraction_service()  # 景点检索服务（原RAG检索器）
        
        # 分步推荐相关服务
        self.recommender = get_interactive_recommender(self.llm)
        self.transport_service = get_transport_service()
        self.food_service = get_food_service()
        self.accommodation_service = get_accommodation_service()
        
        # 会话存储（生产环境应使用数据库）
        self.sessions: Dict[str, ConversationState] = {}
        
        logger.info("Agent核心控制器初始化完成（分步交互式模式）")
    
    def get_or_create_session(self, session_id: str) -> ConversationState:
        """获取或创建会话"""
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
        user_message: str,
        selection: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        处理用户消息的主入口
        
        Args:
            session_id: 会话ID
            user_message: 用户消息
            selection: 用户选择数据（可选）
        
        Returns:
            Dict: 包含reply, stage, requirements, recommendation等信息的响应
        """
        try:
            # 获取会话状态
            state = self.get_or_create_session(session_id)
            
            logger.info(
                f"处理消息 - session_id: {session_id}, "
                f"stage: {state.current_stage}, "
                f"message: {user_message[:50]}"
            )
            
            # 根据当前阶段处理消息
            if state.current_stage in [
                ItineraryStage.GREETING,
                ItineraryStage.COLLECTING_REQUIREMENTS,
                ItineraryStage.CONFIRMING_REQUIREMENTS
            ]:
                # 需求收集阶段
                return self._handle_requirement_collection(state, user_message)
            
            elif state.current_stage == ItineraryStage.WAITING_TRANSPORT_SELECTION:
                # 等待交通选择
                return self._handle_transport_selection(state, user_message, selection)
            
            elif state.current_stage == ItineraryStage.WAITING_ATTRACTIONS_SELECTION:
                # 等待景点选择
                return self._handle_attractions_selection(state, user_message, selection)
            
            elif state.current_stage == ItineraryStage.WAITING_FOOD_SELECTION:
                # 等待美食选择
                return self._handle_food_selection(state, user_message, selection)
            
            elif state.current_stage == ItineraryStage.WAITING_ACCOMMODATION_SELECTION:
                # 等待住宿选择
                return self._handle_accommodation_selection(state, user_message, selection)
            
            else:
                return {
                    "reply": "当前阶段暂不支持，请重新开始。",
                    "stage": state.current_stage.value,
                    "requirements": self._format_requirements(state)
                }
            
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
    
    # ========== 需求收集阶段 ==========
    
    def _handle_requirement_collection(
        self,
        state: ConversationState,
        user_message: str
    ) -> Dict:
        """处理需求收集阶段"""
        # 使用对话管理器处理
        reply = self.dialogue_manager.process_user_input(state, user_message)
        
        # 构建响应
        response = {
            "reply": reply,
            "stage": state.current_stage.value,
            "requirements": self._format_requirements(state)
        }
        
        # 如果需求收集完成，进入交通推荐阶段
        if state.current_stage == ItineraryStage.CONFIRMING_REQUIREMENTS:
            # 使用DialogueManager的智能确认判断
            if self.dialogue_manager._is_confirmation(user_message):
                logger.info("用户确认需求，进入交通推荐阶段")
                return self._start_transport_recommendation(state)
        
        return response
    
    # ========== 交通推荐阶段 ==========
    
    def _start_transport_recommendation(self, state: ConversationState) -> Dict:
        """开始交通推荐"""
        logger.info("=" * 80)
        logger.info("阶段1: 交通方案推荐")
        logger.info("=" * 80)
        
        try:
            req = state.user_requirements
            
            # 获取交通选项
            transport_options = self.transport_service.get_transport_options(
                departure_city=req.departure_city or "北京",
                destination_city=req.destination,
                travel_date=req.travel_dates,
                companions_count=req.companions_count or 1
            )
            
            # 使用推荐器生成推荐
            recommendation = self.recommender.recommend_transport(
                requirements=req,
                transport_options=transport_options
            )
            
            # 更新状态
            state.current_stage = ItineraryStage.WAITING_TRANSPORT_SELECTION
            
            return {
                "reply": recommendation.get("prompt", "请选择您的交通方式："),
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state),
                "recommendation": {
                    "type": "transport",
                    "data": recommendation
                }
            }
            
        except Exception as e:
            logger.error(f"交通推荐失败: {e}", exc_info=True)
            return {
                "reply": "抱歉，交通推荐出现问题，请稍后再试。",
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state)
            }
    
    def _handle_transport_selection(
        self,
        state: ConversationState,
        user_message: str,
        selection: Optional[Dict[str, Any]]
    ) -> Dict:
        """处理交通选择"""
        logger.info(f"处理交通选择: {user_message}")
        logger.info(f"📦 收到的selection参数: {selection}")
        
        try:
            # 解析用户选择
            if selection:
                # 前端传来的selection就是choice数据本身
                # 格式: {'method': '飞机', 'cost': 850, 'outbound': {...}, 'return': {...}}
                transport_choice = selection
                logger.info(f"✅ 直接使用selection作为transport_choice: {transport_choice}")
            else:
                # 使用LLM解析自然语言选择
                transport_choice = self._parse_transport_selection(user_message)
                logger.info(f"⚠️ 未收到selection，从消息中解析: {transport_choice}")
            
            # 记录选择
            state.user_selections.transport_choice = transport_choice
            logger.info(f"💾 交通选择已保存到state")
            logger.info(f"📊 完整的transport_choice数据: {state.user_selections.transport_choice}")
            
            # 进入景点推荐阶段
            return self._start_attractions_recommendation(state)
            
        except Exception as e:
            logger.error(f"处理交通选择失败: {e}", exc_info=True)
            return {
                "reply": "抱歉，我没有理解您的选择。请重新选择交通方式（飞机/高铁/自驾）：",
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state)
            }
    
    # ========== 景点推荐阶段 ==========
    
    def _start_attractions_recommendation(self, state: ConversationState) -> Dict:
        """开始景点推荐"""
        logger.info("=" * 80)
        logger.info("阶段2: 景点推荐（按天分配）")
        logger.info("=" * 80)
        
        try:
            req = state.user_requirements
            
            # 获取景点数据
            attractions = self.attraction_service.retrieve_attractions(
                city=req.destination,
                preferences=req.preferences or [],
                top_k=20,
                budget_max=req.budget or 5000
            )
            
            # 转换为字典格式
            attractions_list = [
                {
                    "id": a.id,
                    "name": a.name,
                    "category": a.category,
                    "ticket_price": a.ticket_price,
                    "duration_hours": a.duration_hours,
                    "rating": a.rating,
                    "description": a.description,
                    "tags": a.tags,
                    "address": a.address
                }
                for a in attractions
            ]
            
            # 使用推荐器生成按天推荐
            recommendation = self.recommender.recommend_attractions_by_day(
                requirements=req,
                all_attractions=attractions_list
            )
            
            # 保存推荐数据到状态（用于用户确认时使用）
            state.last_recommendation_data = recommendation.get("daily_attractions", {})
            
            # 更新状态
            state.current_stage = ItineraryStage.WAITING_ATTRACTIONS_SELECTION
            
            return {
                "reply": recommendation.get("prompt", "请确认或调整景点安排："),
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state),
                "selections": self._format_selections(state),
                "recommendation": {
                    "type": "attractions",
                    "data": recommendation
                }
            }
            
        except Exception as e:
            logger.error(f"景点推荐失败: {e}", exc_info=True)
            return {
                "reply": "抱歉，景点推荐出现问题，请稍后再试。",
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state)
            }
    
    def _handle_attractions_selection(
        self,
        state: ConversationState,
        user_message: str,
        selection: Optional[Dict[str, Any]]
    ) -> Dict:
        """处理景点选择"""
        logger.info(f"处理景点选择: {user_message}")
        
        try:
            # 解析用户选择
            if selection and "choice" in selection:
                attractions_choice = selection["choice"]
            else:
                # 用户确认，使用上一步的推荐数据
                attractions_choice = state.last_recommendation_data or {}
                logger.info(f"使用推荐数据: {len(attractions_choice)} 天")
            
            # 记录选择
            state.user_selections.attractions_by_day = attractions_choice
            logger.info(f"✅ 景点选择已记录")
            
            # 进入美食推荐阶段
            return self._start_food_recommendation(state)
            
        except Exception as e:
            logger.error(f"处理景点选择失败: {e}", exc_info=True)
            return {
                "reply": "抱歉，我没有理解您的选择。请确认景点安排或提出修改：",
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state)
            }
    
    # ========== 美食推荐阶段 ==========
    
    def _start_food_recommendation(self, state: ConversationState) -> Dict:
        """开始美食推荐"""
        logger.info("=" * 80)
        logger.info("阶段3: 美食推荐（按天分配）")
        logger.info("=" * 80)
        
        try:
            req = state.user_requirements
            
            # 获取已选景点
            selected_attractions = state.user_selections.attractions_by_day or {}
            
            # 获取餐厅数据
            # 这里简化处理，返回所有餐厅
            all_restaurants = list(self.food_service.restaurants_db.values()) if isinstance(self.food_service.restaurants_db, dict) else self.food_service.restaurants_db
            
            # 使用推荐器生成按天推荐
            recommendation = self.recommender.recommend_food_by_day(
                requirements=req,
                selected_attractions=selected_attractions,
                all_restaurants=all_restaurants
            )
            
            # 保存推荐数据到状态（用于用户确认时使用）
            state.last_recommendation_data = recommendation.get("daily_restaurants", {})
            
            # 更新状态
            state.current_stage = ItineraryStage.WAITING_FOOD_SELECTION
            
            return {
                "reply": recommendation.get("prompt", "请确认或调整美食安排："),
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state),
                "selections": self._format_selections(state),
                "recommendation": {
                    "type": "food",
                    "data": recommendation
                }
            }
            
        except Exception as e:
            logger.error(f"美食推荐失败: {e}", exc_info=True)
            return {
                "reply": "抱歉，美食推荐出现问题，请稍后再试。",
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state)
            }
    
    def _handle_food_selection(
        self,
        state: ConversationState,
        user_message: str,
        selection: Optional[Dict[str, Any]]
    ) -> Dict:
        """处理美食选择"""
        logger.info(f"处理美食选择: {user_message}")
        
        try:
            # 解析用户选择
            if selection and "choice" in selection:
                food_choice = selection["choice"]
            else:
                # 用户确认，使用上一步的推荐数据
                food_choice = state.last_recommendation_data or {}
                logger.info(f"使用推荐数据: {len(food_choice)} 天")
            
            # 记录选择
            state.user_selections.food_by_day = food_choice
            logger.info(f"✅ 美食选择已记录")
            
            # 进入住宿推荐阶段
            return self._start_accommodation_recommendation(state)
            
        except Exception as e:
            logger.error(f"处理美食选择失败: {e}", exc_info=True)
            return {
                "reply": "抱歉，我没有理解您的选择。请确认美食安排或提出修改：",
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state)
            }
    
    # ========== 住宿推荐阶段 ==========
    
    def _start_accommodation_recommendation(self, state: ConversationState) -> Dict:
        """开始住宿推荐"""
        logger.info("=" * 80)
        logger.info("阶段4: 住宿推荐")
        logger.info("=" * 80)
        
        try:
            req = state.user_requirements
            
            # 获取已选景点
            selected_attractions = state.user_selections.attractions_by_day or {}
            
            # 获取酒店数据
            # 将selected_attractions转换为列表格式
            attractions_list = []
            for day_attractions in selected_attractions.values():
                attractions_list.extend(day_attractions)
            
            all_hotels = self.accommodation_service.get_hotels_in_area(
                city=req.destination,
                attractions=attractions_list,
                budget_per_night=req.budget // req.days if req.budget and req.days else 500,
                nights=req.days - 1 if req.days else 2,
                companions_count=req.companions_count or 1
            )
            
            # 使用推荐器生成推荐
            recommendation = self.recommender.recommend_accommodation(
                requirements=req,
                selected_attractions=selected_attractions,
                all_hotels=all_hotels
            )
            
            # 更新状态
            state.current_stage = ItineraryStage.WAITING_ACCOMMODATION_SELECTION
            
            return {
                "reply": recommendation.get("prompt", "请选择您的住宿："),
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state),
                "selections": self._format_selections(state),
                "recommendation": {
                    "type": "accommodation",
                    "data": recommendation
                }
            }
            
        except Exception as e:
            logger.error(f"住宿推荐失败: {e}", exc_info=True)
            return {
                "reply": "抱歉，住宿推荐出现问题，请稍后再试。",
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state)
            }
    
    def _handle_accommodation_selection(
        self,
        state: ConversationState,
        user_message: str,
        selection: Optional[Dict[str, Any]]
    ) -> Dict:
        """处理住宿选择"""
        logger.info(f"处理住宿选择: {user_message}")
        logger.info(f"📦 收到的selection参数: {selection}")
        
        try:
            # 解析用户选择
            if selection:
                # 前端传来的selection就是choice数据本身
                # 格式: {'id': 'hz_hotel_001', 'name': '...', 'price_per_night': 1200, ...}
                accommodation_choice = selection
                logger.info(f"✅ 直接使用selection作为accommodation_choice: {accommodation_choice}")
            else:
                accommodation_choice = {}
                logger.info(f"⚠️ 未收到selection，使用空对象")
            
            # 记录选择
            state.user_selections.accommodation_choice = accommodation_choice
            logger.info(f"💾 住宿选择已保存到state")
            logger.info(f"📊 完整的accommodation_choice数据: {state.user_selections.accommodation_choice}")
            
            # 生成最终攻略
            return self._generate_final_itinerary(state)
            
        except Exception as e:
            logger.error(f"处理住宿选择失败: {e}", exc_info=True)
            return {
                "reply": "抱歉，我没有理解您的选择。请选择住宿或提出修改：",
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state)
            }
    
    # ========== 最终攻略生成 ==========
    
    def _generate_final_itinerary(self, state: ConversationState) -> Dict:
        """生成最终攻略"""
        logger.info("=" * 80)
        logger.info("阶段5: 生成最终攻略")
        logger.info("=" * 80)
        
        try:
            req = state.user_requirements
            sel = state.user_selections
            
            # 整合所有选择，生成完整行程
            # 确保交通数据结构正确
            transport_data = sel.transport_choice or {}
            if transport_data and 'outbound' not in transport_data:
                # 如果没有outbound/return结构，构建一个
                method = transport_data.get('method', '未知')
                cost = transport_data.get('cost', 0)
                
                # 如果cost为0，根据交通方式估算默认费用
                if cost == 0:
                    default_costs = {
                        '飞机': 800,
                        '高铁': 300,
                        '火车': 200,
                        '自驾': 500
                    }
                    cost = default_costs.get(method, 0)
                
                transport_data = {
                    'method': method,
                    'cost': cost,
                    'outbound': {
                        'method': method,
                        'cost': cost,
                        'duration': transport_data.get('duration', '未知'),
                        'reason': transport_data.get('reason', f'{method}出行')
                    },
                    'return': {
                        'method': method,
                        'cost': cost,
                        'duration': transport_data.get('duration', '未知'),
                        'reason': transport_data.get('reason', f'{method}返程')
                    }
                }
            
            itinerary = {
                "destination": req.destination,
                "departure_city": req.departure_city,
                "duration_days": req.days,
                "total_budget": req.budget,
                "companions": req.companions,
                "companions_count": req.companions_count,
                
                # 交通
                "transport": transport_data,
                
                # 每日计划（整合景点和美食）
                "daily_plans": self._build_daily_plans(
                    sel.attractions_by_day or {},
                    sel.food_by_day or {}
                ),
                
                # 住宿
                "hotel": sel.accommodation_choice,
                
                # 预算分配
                "budget_breakdown": self._calculate_budget_breakdown(sel, req),
                
                # 旅行建议
                "tips": [
                    "建议提前预订交通和酒店",
                    "景点门票可在官方平台购买，避免排队",
                    "根据天气情况调整行程"
                ]
            }
            
            # 更新状态
            state.current_stage = ItineraryStage.COMPLETED
            
            return {
                "reply": "✅ 太好了！您的专属旅行攻略已生成完毕。祝您旅途愉快！",
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state),
                "selections": self._format_selections(state),
                "itinerary": itinerary
            }
            
        except Exception as e:
            logger.error(f"生成最终攻略失败: {e}", exc_info=True)
            return {
                "reply": "抱歉，生成攻略时出现问题，请稍后再试。",
                "stage": state.current_stage.value,
                "requirements": self._format_requirements(state)
            }
    
    # ========== 辅助方法 ==========
    
    def _parse_transport_selection(self, user_message: str) -> Dict[str, Any]:
        """解析交通选择（使用LLM）"""
        # 简化处理：关键词匹配
        if "飞机" in user_message:
            return {"method": "飞机"}
        elif "高铁" in user_message or "火车" in user_message:
            return {"method": "高铁"}
        elif "自驾" in user_message or "开车" in user_message:
            return {"method": "自驾"}
        else:
            return {"method": "高铁"}  # 默认
    
    def _build_daily_plans(
        self,
        attractions_by_day: Dict,
        food_by_day: Dict
    ) -> List[Dict[str, Any]]:
        """构建每日计划"""
        logger.info(f"构建每日计划 - 景点天数: {len(attractions_by_day)}, 美食天数: {len(food_by_day)}")
        daily_plans = []
        
        # 合并所有天数的键（确保都转换为字符串）
        all_days = set(str(k) for k in attractions_by_day.keys()) | set(str(k) for k in food_by_day.keys())
        logger.info(f"总天数: {sorted(all_days)}")
        
        for day_str in sorted(all_days):
            schedule = []
            
            # 添加景点（尝试字符串和整数键）
            attractions = attractions_by_day.get(day_str, attractions_by_day.get(int(day_str) if day_str.isdigit() else 0, []))
            logger.info(f"第{day_str}天景点数: {len(attractions)}")
            for attr in attractions:
                schedule.append({
                    "time": "09:00-12:00",  # 简化处理
                    "type": "景点",
                    "name": attr.get("name", "未知"),
                    "cost": attr.get("ticket_price", 0),
                    "reason": attr.get("reason", "")
                })
            
            # 添加餐厅（尝试字符串和整数键）
            restaurants = food_by_day.get(day_str, food_by_day.get(int(day_str) if day_str.isdigit() else 0, []))
            logger.info(f"第{day_str}天餐厅数: {len(restaurants)}")
            for rest in restaurants:
                schedule.append({
                    "time": "12:00-13:30",  # 简化处理
                    "type": rest.get("meal_type", "午餐"),
                    "name": rest.get("name", "未知"),
                    "cost": rest.get("avg_price", 0),
                    "reason": rest.get("reason", "")
                })
            
            daily_plans.append({
                "day": int(day_str) if day_str.isdigit() else day_str,
                "date": None,  # 可以根据travel_dates计算
                "theme": f"第{day_str}天",
                "schedule": schedule,
                "daily_cost": sum(item.get("cost", 0) for item in schedule)
            })
        
        logger.info(f"生成了{len(daily_plans)}天的计划")
        return daily_plans
    
    def _calculate_budget_breakdown(
        self,
        selections: Any,
        requirements: Any
    ) -> Dict[str, int]:
        """计算预算分配"""
        logger.info("开始计算预算分配")
        
        try:
            # 计算交通费用
            transport_cost = 0
            if selections.transport_choice:
                # 尝试获取总费用或往返费用
                transport_cost = selections.transport_choice.get("total_cost", 0)
                if transport_cost == 0:
                    # 如果没有total_cost，尝试计算往返费用
                    outbound_cost = selections.transport_choice.get("outbound", {}).get("cost", 0)
                    return_cost = selections.transport_choice.get("return", {}).get("cost", 0)
                    transport_cost = outbound_cost + return_cost
                if transport_cost == 0:
                    # 如果还是0，尝试单程费用*2
                    single_cost = selections.transport_choice.get("cost", 0)
                    transport_cost = single_cost * 2
            
            logger.info(f"交通费用: {transport_cost}")
            
            # 计算住宿费用
            hotel_cost = 0
            if selections.accommodation_choice:
                hotel_cost = selections.accommodation_choice.get("total_cost", 0)
            
            logger.info(f"住宿费用: {hotel_cost}")
            
            # 计算景点费用
            attractions_cost = 0
            if selections.attractions_by_day:
                for day, attractions in selections.attractions_by_day.items():
                    for attr in attractions:
                        attractions_cost += attr.get("ticket_price", 0)
            
            logger.info(f"景点费用: {attractions_cost}")
            
            # 计算餐饮费用
            food_cost = 0
            if selections.food_by_day:
                for day, restaurants in selections.food_by_day.items():
                    for rest in restaurants:
                        food_cost += rest.get("avg_price", 0)
            
            logger.info(f"餐饮费用: {food_cost}")
            
            # 其他费用（预算的10%）
            misc_cost = int(requirements.budget * 0.1) if requirements.budget else 500
            
            total = transport_cost + hotel_cost + attractions_cost + food_cost + misc_cost
            
            logger.info(f"总费用: {total}")
            
            return {
                "transport": transport_cost,
                "attractions": attractions_cost,
                "food": food_cost,
                "accommodation": hotel_cost,
                "misc": misc_cost,
                "total": total
            }
        except Exception as e:
            logger.error(f"计算预算分配失败: {e}", exc_info=True)
            # 返回默认值
            return {
                "transport": 0,
                "attractions": 500,
                "food": 1000,
                "accommodation": 0,
                "misc": 500,
                "total": 2000
            }
    
    def _format_requirements(self, state: ConversationState) -> Dict:
        """格式化需求数据"""
        req = state.user_requirements
        return {
            "destination": req.destination,
            "province": req.province,
            "departure_city": req.departure_city,
            "days": req.days,
            "budget": req.budget,
            "preferences": req.preferences,
            "travel_dates": req.travel_dates,
            "companions": req.companions,
            "companions_count": req.companions_count
        }
    
    def _format_selections(self, state: ConversationState) -> Dict:
        """格式化选择数据"""
        sel = state.user_selections
        return {
            "transport": sel.transport_choice,
            "attractions": sel.attractions_by_day,
            "food": sel.food_by_day,
            "accommodation": sel.accommodation_choice
        }


# 全局实例
_agent_core = None


def get_agent_core() -> AgentCore:
    """获取Agent核心实例（单例）"""
    global _agent_core
    if _agent_core is None:
        _agent_core = AgentCore()
    return _agent_core
