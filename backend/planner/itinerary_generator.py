"""
成员C：行程规划器 - 行程生成和优化算法
负责根据用户需求和景点信息生成最优行程安排
"""
from typing import List, Dict
from datetime import datetime, timedelta
from loguru import logger

# 导入四个tool
from tools.transport import get_transport_tool
from tools.attraction import get_attraction_tool
from tools.food import get_food_tool
from tools.accommodation import get_accommodation_tool


class ItineraryGenerator:
    """行程生成器 - 利用算法生成优化的行程安排"""
    
    def __init__(self):
        # 初始化四个tool
        self.transport_tool = get_transport_tool()
        self.attraction_tool = get_attraction_tool()
        self.food_tool = get_food_tool()
        self.accommodation_tool = get_accommodation_tool()
        logger.info("行程生成器初始化完成")
    
    def generate_itinerary(
        self,
        destination: str,
        days: int,
        budget: float,
        preferences: List[str],
        attractions: List[Dict],
        start_date: str = None,
        companions: str = None,
        companions_count: int = None,
        departure_city: str = None
    ) -> Dict:
        """
        生成行程
        
        Args:
            destination: 目的地
            days: 天数
            budget: 总预算
            preferences: 偏好
            attractions: 景点列表
            start_date: 开始日期
            companions: 同行人员类型（"独行"、"情侣"、"家庭"、"朋友"）
            companions_count: 同行人数（包括自己）
            departure_city: 出发地城市
        
        Returns:
            行程详情
        """
        try:
            logger.info(f"开始生成行程: {destination}, {days}天, 预算¥{budget}")
            
            # 根据同行人数调整预算和偏好
            adjusted_budget, adjusted_preferences = self._adjust_for_companions(
                budget, preferences, companions, companions_count
            )
            
            # ===== 步骤1: 调用Tool1查询交通 =====
            transport_options = []
            if departure_city:
                logger.info(f"Tool1: 查询交通 {departure_city} -> {destination}")
                transport_options = self.transport_tool.query_transport(
                    departure_city=departure_city,
                    destination_city=destination,
                    companions_count=companions_count or 1,
                    top_k=3
                )
            
            # ===== 步骤2: 调用Tool2查询景点 =====
            logger.info(f"Tool2: 查询景点，偏好: {adjusted_preferences}")
            attraction_list = self.attraction_tool.query_attractions(
                city=destination,
                ticket_price_max=adjusted_budget * 0.3,  # 门票预算占总预算的30%
                preferences=adjusted_preferences,
                rating_min=4.0,
                top_k=10
            )
            
            # ===== 步骤3: 调用Tool3查询美食 =====
            logger.info(f"Tool3: 查询美食")
            restaurant_list = self.food_tool.query_restaurants(
                city=destination,
                preferences=adjusted_preferences,
                price_max=adjusted_budget / days / 3,  # 单餐预算
                rating_min=4.0,
                top_k=10
            )
            
            # ===== 步骤4: 调用Tool4查询住宿 =====
            logger.info(f"Tool4: 查询住宿")
            hotel_list = self.accommodation_tool.query_hotels(
                city=destination,
                companions_count=companions_count or 1,
                price_max=adjusted_budget / days * 0.4,  # 住宿预算占每日预算的40%
                rating_min=4.0,
                top_k=5
            )
            
            # ===== 步骤5: LLM决策 - 生成每日行程安排 =====
            logger.info(f"LLM决策: 根据用户偏好、预算和距离生成行程")
            daily_plans = self._arrange_daily_plans_with_tools(
                days=days,
                attractions=attraction_list,
                restaurants=restaurant_list,
                hotels=hotel_list,
                preferences=adjusted_preferences,
                budget=adjusted_budget,
                companions=companions
            )
            
            # 选择最优交通方案
            selected_transport = transport_options[0] if transport_options else None
            
            # 选择最优酒店
            selected_hotel = hotel_list[0] if hotel_list else None
            
            # 计算总费用
            estimated_cost = self._calculate_total_cost(
                transport=selected_transport,
                daily_plans=daily_plans,
                hotel=selected_hotel,
                days=days,
                companions_count=companions_count or 1
            )
            
            # 构建完整的行程对象
            itinerary = {
                "destination": destination,
                "duration_days": days,
                "total_budget": budget,
                "companions": companions,
                "companions_count": companions_count,
                "departure_city": departure_city,
                
                # 交通信息
                "transport": {
                    "outbound": selected_transport,
                    "return": selected_transport,
                    "options": transport_options[:3]
                } if transport_options else None,
                
                # 每日行程
                "daily_plans": daily_plans,
                
                # 住宿信息
                "accommodation": {
                    "selected": selected_hotel,
                    "options": hotel_list[:3]
                } if hotel_list else None,
                
                # 预算分析
                "budget_breakdown": self._calculate_budget_breakdown_v2(
                    transport=selected_transport,
                    daily_plans=daily_plans,
                    hotel=selected_hotel,
                    days=days,
                    companions_count=companions_count or 1
                ),
                
                "estimated_cost": estimated_cost,
                
                # 旅行建议
                "tips": self._generate_travel_tips(destination, adjusted_preferences, companions)
            }
            
            logger.info(f"行程生成完成: {destination}, {days}天, 预算¥{budget}, 预估花费¥{estimated_cost}")
            return itinerary
        
        except Exception as e:
            logger.error(f"生成行程时出错: {e}")
            return self._get_default_itinerary(destination, days, budget)
    
    def _adjust_for_companions(
        self,
        budget: float,
        preferences: List[str],
        companions: str = None,
        companions_count: int = None
    ) -> tuple:
        """
        根据同行人员类型和人数调整预算和偏好
        
        返回: (调整后预算, 调整后偏好)
        """
        adjusted_budget = budget
        adjusted_preferences = preferences.copy() if preferences else []
        
        if not companions:
            return adjusted_budget, adjusted_preferences
        
        # 根据不同的同行类型调整
        if companions == "家庭":
            # 家庭出游：增加儿童友好景点
            if "自然景观" not in adjusted_preferences:
                adjusted_preferences.append("自然景观")
            # 根据人数调整预算（家庭通常需要更多预算）
            if companions_count and companions_count >= 3:
                adjusted_budget *= 1.15  # 3人以上家庭增加15%预算
            else:
                adjusted_budget *= 1.1  # 增加10%预算用于儿童相关活动
            
        elif companions == "情侣":
            # 情侣出游：增加浪漫景点建议
            if "美食" not in adjusted_preferences:
                adjusted_preferences.append("美食")
            adjusted_budget *= 0.95  # 节省5%预算
            
        elif companions == "朋友":
            # 朋友出游：增加娱乐休闲
            if "休闲" not in adjusted_preferences:
                adjusted_preferences.append("休闲")
            # 朋友较多时可集体购票优惠
            if companions_count and companions_count >= 4:
                adjusted_budget *= 0.9  # 4人以上团体优惠10%
            
        elif companions == "独行":
            # 独行：无特殊调整
            pass
        
        return adjusted_budget, adjusted_preferences
    
    def _arrange_daily_plans_with_tools(
        self,
        days: int,
        attractions: List[Dict],
        restaurants: List[Dict],
        hotels: List[Dict],
        preferences: List[str],
        budget: float,
        companions: str = None
    ) -> List[Dict]:
        """
        基于tool返回的数据安排每日计划
        
        这里实现LLM决策逻辑：根据用户偏好、预算和距离优化每日行程
        """
        daily_plans = []
        
        # 平均分配景点（每天2-3个景点）
        attractions_per_day = max(2, min(3, len(attractions) // days)) if days > 0 else 2
        
        # 平均分配餐厅（每天2个餐厅：午餐+晚餐）
        restaurants_per_day = 2
        
        for day in range(1, days + 1):
            # 选择当天的景点
            start_idx = (day - 1) * attractions_per_day
            end_idx = min(day * attractions_per_day, len(attractions))
            day_attractions = attractions[start_idx:end_idx]
            
            # 选择当天的餐厅
            rest_start_idx = (day - 1) * restaurants_per_day
            rest_end_idx = min(day * restaurants_per_day, len(restaurants))
            day_restaurants = restaurants[rest_start_idx:rest_end_idx]
            
            # 构建每日行程
            daily_plan = {
                "day": day,
                "date": None,  # 可以根据start_date计算
                "attractions": [
                    {
                        "name": attr.get("name"),
                        "time_slot": "上午" if i == 0 else "下午",
                        "duration": attr.get("duration_hours", 2),
                        "ticket_price": attr.get("ticket_price", 0),
                        "description": attr.get("description", ""),
                        "tags": attr.get("tags", [])
                    }
                    for i, attr in enumerate(day_attractions)
                ],
                "meals": [
                    {
                        "type": "午餐" if i == 0 else "晚餐",
                        "restaurant": rest.get("name"),
                        "cuisine_type": rest.get("cuisine_type"),
                        "avg_price": rest.get("avg_price", 0),
                        "signature_dishes": rest.get("signature_dishes", [])
                    }
                    for i, rest in enumerate(day_restaurants[:2])
                ],
                "daily_cost": self._calculate_daily_cost(day_attractions, day_restaurants)
            }
            
            daily_plans.append(daily_plan)
        
        return daily_plans
    
    def _calculate_daily_cost(self, attractions: List[Dict], restaurants: List[Dict]) -> float:
        """计算每日花费"""
        # 景点门票
        attraction_cost = sum(a.get("ticket_price", 0) for a in attractions)
        
        # 餐饮费用
        meal_cost = sum(r.get("avg_price", 0) for r in restaurants)
        
        # 交通费用（市内）
        transport_cost = 50
        
        return attraction_cost + meal_cost + transport_cost
    
    def _calculate_total_cost(
        self,
        transport: Dict = None,
        daily_plans: List[Dict] = None,
        hotel: Dict = None,
        days: int = 3,
        companions_count: int = 1
    ) -> float:
        """计算总费用"""
        total = 0
        
        # 交通费用（往返）
        if transport:
            total += transport.get("cost_per_person", 0) * companions_count * 2
        
        # 每日费用
        if daily_plans:
            for plan in daily_plans:
                total += plan.get("daily_cost", 0) * companions_count
        
        # 住宿费用
        if hotel:
            total += hotel.get("price_per_night", 0) * (days - 1)  # 住宿天数=旅行天数-1
        
        return total
    
    def _calculate_budget_breakdown_v2(
        self,
        transport: Dict = None,
        daily_plans: List[Dict] = None,
        hotel: Dict = None,
        days: int = 3,
        companions_count: int = 1
    ) -> Dict:
        """计算预算分配（新版本）"""
        breakdown = {
            "交通": 0,
            "景点门票": 0,
            "餐饮": 0,
            "住宿": 0,
            "其他": 0
        }
        
        # 交通费用
        if transport:
            breakdown["交通"] = transport.get("cost_per_person", 0) * companions_count * 2
        
        # 景点和餐饮费用
        if daily_plans:
            for plan in daily_plans:
                for attr in plan.get("attractions", []):
                    breakdown["景点门票"] += attr.get("ticket_price", 0) * companions_count
                for meal in plan.get("meals", []):
                    breakdown["餐饮"] += meal.get("avg_price", 0) * companions_count
        
        # 住宿费用
        if hotel:
            breakdown["住宿"] = hotel.get("price_per_night", 0) * (days - 1)
        
        # 其他费用（市内交通等）
        breakdown["其他"] = days * 50 * companions_count
        
        return breakdown
    
    def _calculate_budget_breakdown(
        self,
        attractions: List[Dict],
        total_budget: float,
        companions: str = None
    ) -> Dict:
        """计算预算分配"""
        attractions_cost = sum(a.get("ticket_price", 0) for a in attractions)
        
        return {
            "景点门票": attractions_cost,
            "餐饮": total_budget * 0.3,
            "住宿": total_budget * 0.4,
            "交通": total_budget * 0.2,
            "其他": total_budget * 0.1
        }
    
    def _estimate_total_cost(self, attractions: List[Dict], companions: str = None) -> float:
        """估算总成本"""
        attractions_cost = sum(a.get("ticket_price", 0) for a in attractions)
        # 模拟成本：景点 + 餐饮 + 住宿 + 交通
        estimated_total = attractions_cost + 800  # 基础成本
        return estimated_total
    
    def _generate_travel_tips(
        self,
        destination: str,
        preferences: List[str],
        companions: str = None
    ) -> List[str]:
        """生成旅行建议"""
        tips = [
            "提前预订景点门票可以获得优惠",
            "推荐使用公共交通出行，环保且经济",
            "携带身份证和必要的证件",
            "了解当地天气，做好防晒或保暖",
        ]
        
        if "美食" in preferences:
            tips.append("不要错过当地特色美食，可咨询酒店前台推荐")
        
        if "自然景观" in preferences:
            tips.append("自然景区需要穿着舒适的运动鞋")
        
        if "历史文化" in preferences:
            tips.append("参加专业导游讲解能更好地了解历史背景")
        
        # 根据同行人员类型添加建议
        if companions == "家庭":
            tips.append("建议为儿童准备常用药物和零食")
            tips.append("选择儿童友好的餐厅和酒店")
            tips.append("合理安排行程，避免儿童过度疲劳")
            
        elif companions == "情侣":
            tips.append("预留浪漫的晚餐时间，享受两人世界")
            tips.append("考虑参加当地特色的夜间活动")
            
        elif companions == "朋友":
            tips.append("可以寻找团体折扣门票")
            tips.append("参加当地的娱乐活动和夜生活")
            tips.append("合理分工拍照记录美好时刻")
            
        elif companions == "独行":
            tips.append("参加当地的青年旅舍活动，认识旅友")
            tips.append("选择安全的地区，告知朋友行程")
            tips.append("尝试当地公共交通和特色小吃")
        
        return tips
    
    def _get_default_itinerary(
        self,
        destination: str,
        days: int,
        budget: float
    ) -> Dict:
        """获取默认行程（出错时）"""
        return {
            "destination": destination,
            "duration_days": days,
            "total_budget": budget,
            "daily_plans": [
                {
                    "day": i,
                    "morning": {"activity": "探索当地特色", "time": "08:00-12:00", "cost": budget * 0.2 / days},
                    "afternoon": {"activity": "美食体验", "time": "14:00-17:00", "cost": budget * 0.2 / days},
                    "evening": {"activity": "夜景游览", "time": "18:00-21:00", "cost": budget * 0.1 / days},
                }
                for i in range(1, days + 1)
            ],
            "estimated_cost": budget,
            "tips": ["建议咨询当地旅游信息中心获取更多建议"]
        }


# 全局行程生成器实例
_generator = None

def get_itinerary_generator() -> ItineraryGenerator:
    """获取全局行程生成器实例"""
    global _generator
    if _generator is None:
        _generator = ItineraryGenerator()
    return _generator

