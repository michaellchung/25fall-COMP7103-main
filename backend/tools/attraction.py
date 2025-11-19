"""
Tool 2: 景点查询工具
基于向量数据库查询景点信息
"""
from typing import List, Dict
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class Attraction:
    """景点信息"""
    name: str
    city: str
    category: List[str]  # ["自然风光", "历史文化"]
    rating: float  # 评分 (0-5)
    ticket_price: float  # 门票价格
    duration_hours: float  # 建议游玩时长
    location: Dict  # {"lat": 30.25, "lng": 120.13, "address": "..."}
    description: str  # 景点描述
    tags: List[str]  # ["必游", "免费", "适合拍照"]
    opening_hours: str  # 开放时间
    best_season: List[str]  # 最佳季节


class AttractionTool:
    """景点查询工具 - Tool 2"""
    
    def __init__(self):
        logger.info("景点查询工具初始化完成")
    
    def query_attractions(
        self,
        city: str,
        ticket_price_max: float = 1000,
        time_point: str = None,  # 时间点
        location_range: Dict = None,  # 位置范围
        rating_min: float = 0.0,
        preferences: List[str] = None,
        top_k: int = 10
    ) -> List[Dict]:
        """
        查询景点
        
        Args:
            city: 城市
            ticket_price_max: 最高门票价格
            time_point: 时间点
            location_range: 位置范围
            rating_min: 最低评分
            preferences: 偏好标签
            top_k: 返回数量
        
        Returns:
            景点列表
        """
        logger.info(f"查询景点: {city}, 偏好: {preferences}, topK: {top_k}")
        
        # Mock数据 - 返回杭州景点
        attractions = self._get_mock_hangzhou_attractions()
        
        # 过滤
        filtered = []
        for attr in attractions:
            # 价格过滤
            if attr.ticket_price > ticket_price_max:
                continue
            # 评分过滤
            if attr.rating < rating_min:
                continue
            # 偏好过滤
            if preferences:
                if not any(pref in attr.category for pref in preferences):
                    continue
            
            filtered.append(attr)
        
        # 按评分排序
        filtered.sort(key=lambda x: x.rating, reverse=True)
        
        return [asdict(attr) for attr in filtered[:top_k]]
    
    def _get_mock_hangzhou_attractions(self) -> List[Attraction]:
        """返回杭州的Mock景点数据"""
        return [
            Attraction(
                name="西湖",
                city="杭州",
                category=["自然风光", "历史文化"],
                rating=4.8,
                ticket_price=0,
                duration_hours=3.0,
                location={"lat": 30.2591, "lng": 120.1353, "address": "浙江省杭州市西湖区西湖风景名胜区"},
                description="西湖是杭州的标志性景点，以秀丽的湖光山色和众多的名胜古迹闻名。春季赏樱花，夏季赏荷花，秋季赏桂花，冬季赏雪景。",
                tags=["必游", "免费", "适合拍照", "世界文化遗产"],
                opening_hours="全天开放",
                best_season=["春季", "秋季"]
            ),
            Attraction(
                name="灵隐寺",
                city="杭州",
                category=["历史文化", "宗教文化"],
                rating=4.7,
                ticket_price=75,
                duration_hours=2.5,
                location={"lat": 30.2419, "lng": 120.0973, "address": "浙江省杭州市西湖区灵隐路法云弄1号"},
                description="灵隐寺是江南著名古刹之一，始建于东晋，已有约1700年历史。寺内古木参天，环境清幽。",
                tags=["必游", "历史古迹", "适合祈福"],
                opening_hours="07:00-18:00",
                best_season=["春季", "秋季"]
            ),
            Attraction(
                name="雷峰塔",
                city="杭州",
                category=["历史文化"],
                rating=4.5,
                ticket_price=40,
                duration_hours=1.5,
                location={"lat": 30.2314, "lng": 120.1489, "address": "浙江省杭州市西湖区南山路15号"},
                description="雷峰塔是西湖十景之一，因白娘子传说而闻名。登塔可俯瞰西湖美景。",
                tags=["热门景点", "适合拍照", "传说故事"],
                opening_hours="08:00-17:30",
                best_season=["全年"]
            ),
            Attraction(
                name="西溪湿地",
                city="杭州",
                category=["自然风光"],
                rating=4.6,
                ticket_price=80,
                duration_hours=4.0,
                location={"lat": 30.2710, "lng": 120.0519, "address": "浙江省杭州市西湖区天目山路518号"},
                description="西溪湿地是中国第一个国家湿地公园，生态环境优美，可乘船游览。",
                tags=["自然景观", "适合休闲", "生态旅游"],
                opening_hours="08:30-17:30",
                best_season=["春季", "秋季"]
            ),
            Attraction(
                name="千岛湖",
                city="杭州",
                category=["自然风光"],
                rating=4.7,
                ticket_price=150,
                duration_hours=6.0,
                location={"lat": 29.6047, "lng": 119.0357, "address": "浙江省杭州市淳安县千岛湖镇"},
                description="千岛湖湖水清澈，岛屿众多，是度假休闲的好去处。可乘船游湖，欣赏美景。",
                tags=["自然景观", "度假胜地", "水上活动"],
                opening_hours="08:00-17:00",
                best_season=["夏季", "秋季"]
            ),
            Attraction(
                name="宋城",
                city="杭州",
                category=["文化体验", "休闲娱乐"],
                rating=4.5,
                ticket_price=310,
                duration_hours=4.0,
                location={"lat": 30.2087, "lng": 120.1147, "address": "浙江省杭州市西湖区之江路148号"},
                description="宋城是大型文化主题公园，再现宋代都市风貌。《宋城千古情》演出非常精彩。",
                tags=["文化体验", "演出", "适合家庭"],
                opening_hours="10:00-21:00",
                best_season=["全年"]
            ),
            Attraction(
                name="河坊街",
                city="杭州",
                category=["美食", "历史文化"],
                rating=4.4,
                ticket_price=0,
                duration_hours=2.0,
                location={"lat": 30.2446, "lng": 120.1648, "address": "浙江省杭州市上城区河坊街"},
                description="河坊街是杭州历史文化街区，保留了清末民初的建筑风格，有众多特色小吃和手工艺品店。",
                tags=["免费", "美食街", "购物", "夜景"],
                opening_hours="全天开放",
                best_season=["全年"]
            ),
            Attraction(
                name="飞来峰",
                city="杭州",
                category=["自然风光", "历史文化"],
                rating=4.6,
                ticket_price=45,
                duration_hours=2.0,
                location={"lat": 30.2428, "lng": 120.0953, "address": "浙江省杭州市西湖区灵隐路"},
                description="飞来峰是灵隐景区的一部分，山上有众多石窟造像，是中国南方石窟艺术的重要遗存。",
                tags=["历史古迹", "石窟艺术", "自然景观"],
                opening_hours="07:00-18:00",
                best_season=["春季", "秋季"]
            ),
            Attraction(
                name="龙井村",
                city="杭州",
                category=["美食", "自然风光"],
                rating=4.5,
                ticket_price=0,
                duration_hours=2.5,
                location={"lat": 30.2172, "lng": 120.1189, "address": "浙江省杭州市西湖区龙井路"},
                description="龙井村是西湖龙井茶的原产地，可以品茶、欣赏茶园风光，感受茶文化。",
                tags=["免费", "茶文化", "自然风光", "品茶"],
                opening_hours="全天开放",
                best_season=["春季", "秋季"]
            ),
            Attraction(
                name="杭州博物馆",
                city="杭州",
                category=["历史文化"],
                rating=4.6,
                ticket_price=0,
                duration_hours=2.0,
                location={"lat": 30.2533, "lng": 120.1619, "address": "浙江省杭州市上城区粮道山18号"},
                description="杭州博物馆展示了杭州的历史文化，收藏有大量文物和艺术品。",
                tags=["免费", "博物馆", "历史文化", "雨天备选"],
                opening_hours="09:00-16:30（周一闭馆）",
                best_season=["全年"]
            )
        ]


# 全局单例
_attraction_tool = None

def get_attraction_tool() -> AttractionTool:
    """获取景点工具实例"""
    global _attraction_tool
    if _attraction_tool is None:
        _attraction_tool = AttractionTool()
    return _attraction_tool

