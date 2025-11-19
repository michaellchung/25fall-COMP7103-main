"""
分步决策行程生成器
使用LLM分4步生成完整行程：
1. 选择景点
2. 选择美食
3. 选择酒店
4. 规划详细行程
"""
from typing import List, Dict
from loguru import logger
import json
from utils.llm import LLMClient
from config.settings import settings


class StepByStepItineraryGenerator:
    """分步决策行程生成器"""
    
    def __init__(self):
        self.llm = LLMClient()
        logger.info("分步决策行程生成器初始化完成")
    
    def generate_itinerary(
        self,
        user_requirements: Dict,
        transport_options: List[Dict],
        all_attractions: List[Dict],
        food_service,
        accommodation_service
    ) -> Dict:
        """
        分步生成完整行程
        
        Args:
            user_requirements: 用户需求
            transport_options: 交通方案列表
            all_attractions: 所有景点列表
            food_service: 美食服务
            accommodation_service: 住宿服务
        
        Returns:
            完整行程
        """
        logger.info("=" * 80)
        logger.info("开始分步决策生成行程")
        logger.info("=" * 80)
        
        try:
            # Step 1: LLM选择景点
            selected_attractions = self._step1_select_attractions(
                user_requirements,
                all_attractions
            )
            logger.info(f"✅ Step 1完成: 选择了 {len(selected_attractions)} 个景点")
            
            # Step 2: 根据选中的景点查询美食
            restaurants_by_attraction = food_service.get_restaurants_for_attractions(
                selected_attractions,
                top_k_per_attraction=2
            )
            logger.info(f"✅ Step 2完成: 查询了 {len(restaurants_by_attraction)} 个景点的美食")
            
            # Step 3: 根据景点位置查询酒店
            hotels = accommodation_service.get_hotels_in_area(
                city=user_requirements.get("destination"),
                attractions=selected_attractions,
                budget_per_night=user_requirements.get("budget", 5000) / user_requirements.get("days", 3) / 3,  # 预算的1/3用于住宿
                nights=user_requirements.get("days", 3) - 1,
                companions_count=user_requirements.get("companions_count", 1),
                top_k=5
            )
            logger.info(f"✅ Step 3完成: 查询了 {len(hotels)} 家酒店")
            
            # Step 4: LLM规划完整行程
            itinerary = self._step4_plan_detailed_itinerary(
                user_requirements,
                transport_options,
                selected_attractions,
                restaurants_by_attraction,
                hotels
            )
            logger.info("✅ Step 4完成: 生成完整行程")
            
            logger.info("=" * 80)
            logger.info("行程生成完成！")
            logger.info("=" * 80)
            
            return itinerary
            
        except Exception as e:
            logger.error(f"生成行程失败: {e}", exc_info=True)
            return self._get_fallback_itinerary(user_requirements)
    
    def _step1_select_attractions(
        self,
        user_requirements: Dict,
        all_attractions: List[Dict]
    ) -> List[Dict]:
        """Step 1: LLM选择景点"""
        logger.info("\n" + "=" * 80)
        logger.info("Step 1: LLM选择景点")
        logger.info("=" * 80)
        
        prompt = f"""你是一个专业的旅行规划师。根据用户需求从候选景点中选择合适的景点。

## 用户需求
- 目的地: {user_requirements.get('destination')}
- 天数: {user_requirements.get('days')}天
- 预算: {user_requirements.get('budget')}元
- 偏好: {', '.join(user_requirements.get('preferences', []))}
- 同行: {user_requirements.get('companions')} ({user_requirements.get('companions_count')}人)

## 候选景点
{json.dumps(all_attractions, ensure_ascii=False, indent=2)}

## 选择要求
1. 根据用户偏好优先选择相关景点
2. 考虑预算，优先选择免费或低价景点
3. 每天安排3-4个景点，总共选择 {user_requirements.get('days', 3) * 3} 个左右
4. 景点之间尽量地理位置接近
5. 考虑景点游玩时长，避免行程过于紧张

## 输出格式（JSON数组）
请从候选景点中选择合适的景点，返回景点ID列表：
```json
{{
  "selected_attraction_ids": ["hz001", "hz002", "hz003", ...],
  "reason": "选择理由"
}}
```

只返回JSON，不要其他内容。"""

        try:
            # 调用LLM
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.chat(messages)
            logger.debug(f"LLM原始响应: {response[:200]}...")
            
            # 解析JSON
            result = self.llm.extract_json(prompt, response)
            selected_ids = result.get("selected_attraction_ids", [])
            reason = result.get("reason", "")
            
            logger.info(f"选择理由: {reason}")
            logger.info(f"选中景点ID: {selected_ids}")
            
            # 根据ID筛选景点
            selected = [a for a in all_attractions if a.get("id") in selected_ids]
            
            # 如果LLM没选够，补充热门景点
            if len(selected) < user_requirements.get('days', 3) * 2:
                logger.warning(f"LLM只选了{len(selected)}个景点，补充热门景点")
                remaining = [a for a in all_attractions if a not in selected]
                selected.extend(remaining[:user_requirements.get('days', 3) * 3 - len(selected)])
            
            return selected
            
        except Exception as e:
            logger.error(f"LLM选择景点失败: {e}，使用fallback")
            # Fallback: 按评分选择
            sorted_attractions = sorted(
                all_attractions,
                key=lambda x: x.get("rating", 0),
                reverse=True
            )
            return sorted_attractions[:user_requirements.get('days', 3) * 3]
    
    def _step4_plan_detailed_itinerary(
        self,
        user_requirements: Dict,
        transport_options: List[Dict],
        selected_attractions: List[Dict],
        restaurants: Dict[str, List[Dict]],
        hotels: List[Dict]
    ) -> Dict:
        """Step 4: LLM规划完整行程"""
        logger.info("\n" + "=" * 80)
        logger.info("Step 4: LLM规划完整行程")
        logger.info("=" * 80)
        
        prompt = f"""你是一个专业的旅行规划师。根据已选择的景点、餐厅、酒店，制定详细的旅行行程。

## 用户需求
- 目的地: {user_requirements.get('destination')}
- 出发地: {user_requirements.get('departure_city')}
- 天数: {user_requirements.get('days')}天
- 预算: {user_requirements.get('budget')}元
- 偏好: {', '.join(user_requirements.get('preferences', []))}
- 同行: {user_requirements.get('companions')} ({user_requirements.get('companions_count')}人)
- 出行日期: {user_requirements.get('travel_dates', '待定')}

## 交通方案（选择1个往返方案）
{json.dumps(transport_options, ensure_ascii=False, indent=2)}

## 已选景点
{json.dumps(selected_attractions, ensure_ascii=False, indent=2)}

## 餐厅选择（按景点分组）
{json.dumps(restaurants, ensure_ascii=False, indent=2)}

## 酒店选择（选择1家，全程住同一家）
{json.dumps(hotels, ensure_ascii=False, indent=2)}

## 规划要求
1. **交通**: 从交通方案中选择1种往返方式，说明理由
2. **住宿**: 从酒店中选择1家，全程住同一家，说明理由
3. **每日安排**:
   - 每天安排3-4个景点
   - 同一天的景点尽量地理位置接近
   - 每天安排午餐和晚餐（从对应景点的餐厅中选择）
   - 时间安排：09:00开始，21:00结束
   - 考虑景点游玩时长、用餐时间、交通时间
4. **预算控制**: 总费用 ≤ {user_requirements.get('budget')}元
5. **旅行建议**: 给出3-5条实用的旅行贴士

## 输出格式（JSON）
```json
{{
  "transport": {{
    "outbound": {{
      "method": "高铁",
      "cost": 553,
      "reason": "性价比高，时间适中"
    }},
    "return": {{
      "method": "高铁",
      "cost": 553,
      "reason": "返程同样选择高铁"
    }}
  }},
  "hotel": {{
    "id": "hz_hotel_004",
    "name": "维也纳酒店(西湖文化广场店)",
    "nights": 2,
    "total_cost": 700,
    "reason": "位置中心，性价比高"
  }},
  "daily_plans": [
    {{
      "day": 1,
      "date": "2025-12-01",
      "theme": "西湖文化之旅",
      "schedule": [
        {{
          "time": "09:00-12:00",
          "type": "景点",
          "name": "西湖",
          "cost": 0,
          "reason": "杭州必游，免费景点"
        }},
        {{
          "time": "12:00-13:30",
          "type": "午餐",
          "name": "外婆家",
          "cost": 160,
          "reason": "西湖附近，性价比高"
        }},
        {{
          "time": "14:00-17:00",
          "type": "景点",
          "name": "雷峰塔",
          "cost": 80,
          "reason": "西湖边，文化景点"
        }},
        {{
          "time": "18:00-19:30",
          "type": "晚餐",
          "name": "楼外楼",
          "cost": 300,
          "reason": "杭帮菜老字号"
        }}
      ],
      "daily_cost": 540
    }}
  ],
  "budget_breakdown": {{
    "transport": 1106,
    "attractions": 450,
    "food": 1200,
    "accommodation": 700,
    "misc": 500,
    "total": 3956
  }},
  "tips": [
    "建议提前预订高铁票",
    "西湖周边可租自行车游览",
    "雷峰塔建议傍晚游览，可看日落"
  ]
}}
```

只返回JSON，不要其他内容。"""

        try:
            # 调用LLM
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.chat(messages)
            logger.debug(f"LLM原始响应: {response[:200]}...")
            
            # 解析JSON
            itinerary = self.llm.extract_json(prompt, response)
            
            # 添加基础信息
            itinerary["destination"] = user_requirements.get("destination")
            itinerary["departure_city"] = user_requirements.get("departure_city")
            itinerary["duration_days"] = user_requirements.get("days")
            itinerary["total_budget"] = user_requirements.get("budget")
            itinerary["companions"] = user_requirements.get("companions")
            itinerary["companions_count"] = user_requirements.get("companions_count")
            
            logger.info(f"生成了 {len(itinerary.get('daily_plans', []))} 天的行程")
            logger.info(f"预估总费用: {itinerary.get('budget_breakdown', {}).get('total', 0)}元")
            
            return itinerary
            
        except Exception as e:
            logger.error(f"LLM规划行程失败: {e}，使用fallback")
            return self._get_fallback_itinerary(user_requirements)
    
    def _get_fallback_itinerary(self, user_requirements: Dict) -> Dict:
        """Fallback: 返回简单行程"""
        logger.warning("使用Fallback行程")
        
        return {
            "destination": user_requirements.get("destination"),
            "departure_city": user_requirements.get("departure_city"),
            "duration_days": user_requirements.get("days"),
            "total_budget": user_requirements.get("budget"),
            "companions": user_requirements.get("companions"),
            "companions_count": user_requirements.get("companions_count"),
            "transport": {
                "outbound": {"method": "高铁", "cost": 553, "reason": "推荐方案"},
                "return": {"method": "高铁", "cost": 553, "reason": "推荐方案"}
            },
            "hotel": {
                "name": "如家酒店(西湖店)",
                "nights": user_requirements.get("days", 3) - 1,
                "total_cost": 220 * (user_requirements.get("days", 3) - 1),
                "reason": "经济实惠"
            },
            "daily_plans": [
                {
                    "day": i + 1,
                    "date": "待定",
                    "theme": f"第{i+1}天行程",
                    "schedule": [
                        {"time": "09:00-12:00", "type": "景点", "name": "西湖", "cost": 0},
                        {"time": "12:00-13:30", "type": "午餐", "name": "外婆家", "cost": 80},
                        {"time": "14:00-17:00", "type": "景点", "name": "灵隐寺", "cost": 75},
                        {"time": "18:00-19:30", "type": "晚餐", "name": "楼外楼", "cost": 150}
                    ],
                    "daily_cost": 305
                }
                for i in range(user_requirements.get("days", 3))
            ],
            "budget_breakdown": {
                "transport": 1106,
                "attractions": 300,
                "food": 900,
                "accommodation": 440,
                "misc": 300,
                "total": 3046
            },
            "tips": [
                "这是一个简化的行程方案",
                "建议根据实际情况调整",
                "提前预订可获得更优惠的价格"
            ]
        }


# 单例
_step_generator = None

def get_step_by_step_generator() -> StepByStepItineraryGenerator:
    """获取分步生成器单例"""
    global _step_generator
    if _step_generator is None:
        _step_generator = StepByStepItineraryGenerator()
    return _step_generator

