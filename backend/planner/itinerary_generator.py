"""
成员C：行程规划器 - 行程生成和优化算法
负责根据用户需求和景点信息生成最优行程安排
"""
from typing import List, Dict
from datetime import datetime, timedelta
from loguru import logger


class ItineraryGenerator:
    """行程生成器 - 利用算法生成优化的行程安排"""
    
    def __init__(self):
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
            # 计算每天的预算
            daily_budget = budget / days if days > 0 else 0
            
            # 根据同行人数调整预算和偏好
            adjusted_budget, adjusted_preferences = self._adjust_for_companions(
                budget, preferences, companions, companions_count
            )
            
            # 模拟行程安排逻辑
            itinerary = {
                "destination": destination,
                "duration_days": days,
                "total_budget": budget,
                "daily_budget": daily_budget,
                "companions": companions,
                "companions_count": companions_count,
                "departure_city": departure_city,
                "daily_plans": self._arrange_daily_plans(
                    attractions, days, daily_budget, companions
                ),
                "budget_breakdown": self._calculate_budget_breakdown(attractions, budget, companions),
                "estimated_cost": self._estimate_total_cost(attractions, companions),
                "tips": self._generate_travel_tips(destination, adjusted_preferences, companions)
            }
            
            logger.info(f"生成行程: {destination}, {days}天, 预算¥{budget}, 同行:{companions}")
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
    
    def _arrange_daily_plans(
        self,
        attractions: List[Dict],
        days: int,
        daily_budget: float,
        companions: str = None
    ) -> List[Dict]:
        """安排每日计划"""
        daily_plans = []
        
        # 平均分配景点
        attractions_per_day = max(1, len(attractions) // days) if days > 0 else 1
        
        for day in range(1, days + 1):
            start_idx = (day - 1) * attractions_per_day
            end_idx = day * attractions_per_day
            day_attractions = attractions[start_idx:end_idx]
            
            if day == days and end_idx < len(attractions):
                # 最后一天包含剩余的景点
                day_attractions = attractions[start_idx:]
            
            daily_plan = {
                "day": day,
                "morning": {
                    "activity": f"游览{day_attractions[0]['name'] if day_attractions else '景点'}",
                    "time": "08:00-12:00",
                    "cost": day_attractions[0].get("ticket_price", 0) if day_attractions else 0
                },
                "afternoon": {
                    "activity": f"游览{day_attractions[1]['name'] if len(day_attractions) > 1 else '当地美食'}",
                    "time": "14:00-17:00",
                    "cost": day_attractions[1].get("ticket_price", 0) if len(day_attractions) > 1 else 50
                },
                "evening": {
                    "activity": "品尝当地美食或夜景游览",
                    "time": "18:00-21:00",
                    "cost": 80
                },
                "daily_cost": sum(
                    a.get("ticket_price", 0) for a in day_attractions
                ) + 80
            }
            
            daily_plans.append(daily_plan)
        
        return daily_plans
    
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

