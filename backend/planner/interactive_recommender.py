"""
分步交互式推荐器
负责生成各阶段的推荐数据
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from utils.llm import LLMClient
from agent.state import UserRequirements


class InteractiveRecommender:
    """交互式推荐器"""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def recommend_transport(
        self,
        requirements: UserRequirements,
        transport_options: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        推荐交通方案
        
        Args:
            requirements: 用户需求
            transport_options: 交通选项列表（飞机、高铁、自驾）
        
        Returns:
            推荐数据，包含options和prompt
        """
        logger.info(f"开始推荐交通方案: {requirements.departure_city} -> {requirements.destination}")
        
        # 使用LLM分析并排序推荐
        prompt = f"""你是一个旅行规划专家。根据用户需求，分析以下交通方案并给出推荐理由。

用户需求:
- 出发地: {requirements.departure_city or '未指定'}
- 目的地: {requirements.destination}
- 天数: {requirements.days}天
- 预算: ¥{requirements.budget}
- 同行人数: {requirements.companions_count or 1}人
- 同行类型: {requirements.companions or '独行'}

可选交通方案:
{self._format_transport_options(transport_options)}

请为每个方案添加推荐理由，并标注最推荐的方案。
返回JSON格式:
{{
    "options": [
        {{
            "id": "方案ID",
            "method": "交通方式",
            "outbound": {{"method": "...", "cost": 0, "duration": "...", "details": "..."}},
            "return": {{"method": "...", "cost": 0, "duration": "...", "details": "..."}},
            "total_cost": 总费用,
            "reason": "推荐理由",
            "recommended": true/false
        }}
    ],
    "prompt": "给用户的提示文本"
}}
"""
        
        # 暂时直接使用默认推荐（LLM推荐不稳定）
        logger.info("使用默认交通推荐")
        return {
            "options": transport_options,
            "prompt": "🚗 为您推荐以下交通方案，请选择您偏好的出行方式："
        }
    
    def recommend_attractions_by_day(
        self,
        requirements: UserRequirements,
        all_attractions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        按天推荐景点
        
        Args:
            requirements: 用户需求
            all_attractions: 所有可选景点
        
        Returns:
            推荐数据，包含daily_attractions和prompt
        """
        logger.info(f"开始按天推荐景点: {requirements.days}天")
        
        prompt = f"""你是一个旅行规划专家。根据用户需求和可选景点，为每一天安排合适的景点。

用户需求:
- 目的地: {requirements.destination}
- 天数: {requirements.days}天
- 预算: ¥{requirements.budget}
- 偏好: {', '.join(requirements.preferences)}
- 同行: {requirements.companions or '独行'} {requirements.companions_count or 1}人

可选景点:
{self._format_attractions(all_attractions)}

规划要求:
1. 每天安排2-3个景点
2. 考虑景点之间的地理位置，同一天的景点尽量相近
3. 考虑用户偏好和预算
4. 合理分配免费和付费景点
5. 第一天和最后一天可以安排轻松一些

返回JSON格式:
{{
    "daily_attractions": {{
        "1": [
            {{
                "id": "景点ID",
                "name": "景点名称",
                "ticket_price": 门票价格,
                "visit_duration": "建议游玩时长",
                "reason": "推荐理由"
            }}
        ],
        "2": [...],
        ...
    }},
    "prompt": "给用户的提示文本，说明整体安排思路"
}}
"""
        
        # 暂时直接使用默认推荐
        logger.info("使用默认景点推荐")
        return self._default_attractions_recommendation(requirements, all_attractions)
    
    def recommend_food_by_day(
        self,
        requirements: UserRequirements,
        selected_attractions: Dict[int, List[Dict[str, Any]]],
        all_restaurants: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        按天推荐美食
        
        Args:
            requirements: 用户需求
            selected_attractions: 已选择的景点（按天）
            all_restaurants: 所有可选餐厅
        
        Returns:
            推荐数据，包含daily_restaurants和prompt
        """
        logger.info(f"开始按天推荐美食")
        
        prompt = f"""你是一个美食推荐专家。根据用户需求和每天的景点安排，推荐附近的餐厅。

用户需求:
- 目的地: {requirements.destination}
- 天数: {requirements.days}天
- 预算: ¥{requirements.budget}
- 偏好: {', '.join(requirements.preferences)}
- 同行人数: {requirements.companions_count or 1}人

每天的景点安排:
{self._format_daily_attractions(selected_attractions)}

可选餐厅:
{self._format_restaurants(all_restaurants)}

推荐要求:
1. 每天推荐2-3家餐厅（午餐、晚餐）
2. 餐厅位置要靠近当天的景点
3. 考虑用户预算，合理搭配高中低档
4. 如果用户偏好包含"美食"，可以多推荐特色餐厅

返回JSON格式:
{{
    "daily_restaurants": {{
        "1": [
            {{
                "id": "餐厅ID",
                "name": "餐厅名称",
                "cuisine": "菜系",
                "avg_price": 人均价格,
                "meal_type": "午餐/晚餐",
                "reason": "推荐理由"
            }}
        ],
        "2": [...],
        ...
    }},
    "prompt": "给用户的提示文本"
}}
"""
        
        # 暂时直接使用默认推荐
        logger.info("使用默认美食推荐")
        return self._default_food_recommendation(requirements, selected_attractions, all_restaurants)
    
    def recommend_accommodation(
        self,
        requirements: UserRequirements,
        selected_attractions: Dict[int, List[Dict[str, Any]]],
        all_hotels: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        推荐住宿
        
        Args:
            requirements: 用户需求
            selected_attractions: 已选择的景点（按天）
            all_hotels: 所有可选酒店
        
        Returns:
            推荐数据，包含options和prompt
        """
        logger.info(f"开始推荐住宿")
        
        prompt = f"""你是一个住宿推荐专家。根据用户需求和景点分布，推荐合适的酒店。

用户需求:
- 目的地: {requirements.destination}
- 天数: {requirements.days}天（需要住{requirements.days - 1}晚）
- 预算: ¥{requirements.budget}
- 同行: {requirements.companions or '独行'} {requirements.companions_count or 1}人

景点分布:
{self._format_daily_attractions(selected_attractions)}

可选酒店:
{self._format_hotels(all_hotels)}

推荐要求:
1. 推荐3-5家酒店，涵盖不同价位
2. 酒店位置要方便前往各个景点
3. 考虑用户预算和同行人数
4. 标注最推荐的酒店

返回JSON格式:
{{
    "options": [
        {{
            "id": "酒店ID",
            "name": "酒店名称",
            "price_per_night": 每晚价格,
            "nights": 晚数,
            "total_cost": 总费用,
            "star_rating": "星级",
            "location": "位置",
            "reason": "推荐理由",
            "recommended": true/false
        }}
    ],
    "prompt": "给用户的提示文本"
}}
"""
        
        # 暂时直接使用默认推荐
        logger.info("使用默认住宿推荐")
        return self._default_accommodation_recommendation(requirements, all_hotels)
    
    # ========== 辅助方法 ==========
    
    def _parse_llm_json(self, prompt: str) -> Dict[str, Any]:
        """
        调用LLM并解析JSON响应
        
        Args:
            prompt: 提示词
        
        Returns:
            解析后的JSON字典
        """
        import json
        import re
        
        # 添加更强的JSON输出提示
        enhanced_prompt = f"""{prompt}

重要提示：
1. 只返回JSON，不要有任何其他文字说明
2. 确保JSON格式正确，可以被直接解析
3. 不要使用markdown代码块包裹
"""
        
        messages = [{"role": "user", "content": enhanced_prompt}]
        response = self.llm.chat(messages)
        
        logger.debug(f"LLM原始响应: {response[:200]}...")
        
        # 清理响应
        response = response.strip()
        
        # 移除markdown代码块标记
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        # 尝试提取JSON（如果LLM返回了额外的文本）
        # 查找第一个{和最后一个}之间的内容
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"响应内容: {response[:500]}")
            raise
    
    def _format_transport_options(self, options: List[Dict[str, Any]]) -> str:
        """格式化交通选项"""
        lines = []
        for i, opt in enumerate(options, 1):
            lines.append(f"{i}. {opt.get('method', '未知')} - ¥{opt.get('cost', 0)} - {opt.get('duration', '未知')}")
        return "\n".join(lines)
    
    def _format_attractions(self, attractions: List[Dict[str, Any]]) -> str:
        """格式化景点列表"""
        lines = []
        for i, attr in enumerate(attractions[:20], 1):  # 最多20个
            lines.append(
                f"{i}. {attr.get('name', '未知')} - "
                f"¥{attr.get('ticket_price', 0)} - "
                f"{attr.get('tags', [])} - "
                f"{attr.get('description', '')[:50]}"
            )
        return "\n".join(lines)
    
    def _format_daily_attractions(self, daily_attractions: Dict[int, List[Dict[str, Any]]]) -> str:
        """格式化每日景点"""
        lines = []
        for day, attractions in sorted(daily_attractions.items()):
            lines.append(f"第{day}天:")
            for attr in attractions:
                lines.append(f"  - {attr.get('name', '未知')}")
        return "\n".join(lines)
    
    def _format_restaurants(self, restaurants: List[Any]) -> str:
        """格式化餐厅列表"""
        from dataclasses import is_dataclass
        lines = []
        for i, rest in enumerate(restaurants[:20], 1):
            # 处理dataclass或dict
            if is_dataclass(rest):
                name = getattr(rest, 'name', '未知')
                cuisine = getattr(rest, 'cuisine_type', '未知')
                price = getattr(rest, 'avg_price', 0)
            else:
                name = rest.get('name', '未知')
                cuisine = rest.get('cuisine_type', rest.get('cuisine', '未知'))
                price = rest.get('avg_price', 0)
            
            lines.append(f"{i}. {name} - {cuisine} - ¥{price}/人")
        return "\n".join(lines)
    
    def _format_hotels(self, hotels: List[Any]) -> str:
        """格式化酒店列表"""
        from dataclasses import is_dataclass
        lines = []
        for i, hotel in enumerate(hotels[:15], 1):
            # 处理dataclass或dict
            if is_dataclass(hotel):
                name = getattr(hotel, 'name', '未知')
                rating = getattr(hotel, 'star_rating', '未知')
                price = getattr(hotel, 'price_per_night', 0)
            else:
                name = hotel.get('name', '未知')
                rating = hotel.get('star_rating', '未知')
                price = hotel.get('price_per_night', 0)
            
            lines.append(f"{i}. {name} - {rating} - ¥{price}/晚")
        return "\n".join(lines)
    
    def _default_attractions_recommendation(
        self,
        requirements: UserRequirements,
        all_attractions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """默认景点推荐（LLM失败时使用）"""
        logger.info(f"默认景点推荐 - 总景点数: {len(all_attractions)}, 天数: {requirements.days}")
        daily_attractions = {}
        
        if len(all_attractions) == 0:
            logger.warning("没有可用的景点数据！")
            return {
                "daily_attractions": {},
                "prompt": "抱歉，暂时没有找到合适的景点推荐。"
            }
        
        attractions_per_day = max(1, len(all_attractions) // requirements.days)
        
        for day in range(1, requirements.days + 1):
            start_idx = (day - 1) * attractions_per_day
            end_idx = start_idx + min(3, attractions_per_day)
            daily_attractions[str(day)] = all_attractions[start_idx:end_idx]
            logger.info(f"第{day}天分配景点: {len(daily_attractions[str(day)])}个")
        
        return {
            "daily_attractions": daily_attractions,
            "prompt": f"✨ 为您安排了{requirements.days}天的景点行程，每天2-3个景点。请确认或调整："
        }
    
    def _default_food_recommendation(
        self,
        requirements: UserRequirements,
        selected_attractions: Dict[int, List[Dict[str, Any]]],
        all_restaurants: List[Any]
    ) -> Dict[str, Any]:
        """默认美食推荐"""
        from dataclasses import asdict, is_dataclass
        
        # 转换Restaurant对象为字典
        restaurants_list = []
        for r in all_restaurants[:6]:  # 最多取6个
            if is_dataclass(r):
                restaurants_list.append(asdict(r))
            elif isinstance(r, dict):
                restaurants_list.append(r)
        
        daily_restaurants = {}
        for day in range(1, requirements.days + 1):
            # 每天推荐2家餐厅
            start_idx = (day - 1) * 2
            end_idx = start_idx + 2
            daily_restaurants[str(day)] = restaurants_list[start_idx:end_idx]
        
        return {
            "daily_restaurants": daily_restaurants,
            "prompt": "🍜 根据您的景点安排，为您推荐了附近的美食餐厅。请确认或调整："
        }
    
    def _default_accommodation_recommendation(
        self,
        requirements: UserRequirements,
        all_hotels: List[Any]
    ) -> Dict[str, Any]:
        """默认住宿推荐"""
        from dataclasses import asdict, is_dataclass
        
        nights = requirements.days - 1
        options = []
        
        for hotel in all_hotels[:5]:
            # 转换为字典
            if is_dataclass(hotel):
                hotel_dict = asdict(hotel)
            elif isinstance(hotel, dict):
                hotel_dict = hotel
            else:
                continue
            
            options.append({
                **hotel_dict,
                "nights": nights,
                "total_cost": hotel_dict.get('price_per_night', 0) * nights,
                "recommended": False
            })
        
        if options and len(options) > 1:
            options[1]["recommended"] = True  # 标记中间价位为推荐
        
        return {
            "options": options,
            "prompt": f"🏨 根据您的行程，需要住宿{nights}晚。为您推荐以下酒店："
        }


def get_interactive_recommender(llm: LLMClient) -> InteractiveRecommender:
    """获取交互式推荐器实例"""
    return InteractiveRecommender(llm)

