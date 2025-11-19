"""
住宿推荐工具
根据景点位置推荐区域内酒店
"""
from typing import List, Dict
from dataclasses import dataclass, asdict
from loguru import logger
import math


@dataclass
class Hotel:
    """酒店信息"""
    id: str
    name: str
    hotel_type: str  # "经济型" | "舒适型" | "高档型"
    rating: float  # 评分 (0-5)
    price_per_night: float  # 每晚价格
    location: Dict  # {"lat": 30.25, "lng": 120.13, "address": "..."}
    distance_to_center: float  # 距离POI中心的距离（km）
    facilities: List[str]  # ["WiFi", "早餐", "停车场", "健身房"]
    room_type: str  # "标准间" | "大床房" | "套房"
    description: str  # 酒店描述
    tags: List[str]  # ["近地铁", "景区附近", "商圈"]
    phone: str  # 联系电话


class AccommodationService:
    """住宿推荐服务"""
    
    def __init__(self):
        logger.info("住宿推荐服务初始化完成")
        # Mock数据库
        self.hotels_db = self._init_mock_data()
    
    def get_hotels_in_area(
        self,
        city: str,
        attractions: List[Dict],
        budget_per_night: float,
        nights: int,
        companions_count: int = 1,
        top_k: int = 5
    ) -> List[Dict]:
        """
        查询区域内酒店
        
        Args:
            city: 城市
            attractions: 景点列表（用于计算中心点）
            budget_per_night: 每晚预算
            nights: 住宿天数
            companions_count: 入住人数
            top_k: 返回数量
        
        Returns:
            酒店列表，按推荐度排序
        """
        logger.info(f"查询{city}酒店: 预算{budget_per_night}元/晚, {nights}晚, {companions_count}人")
        
        # 1. 计算景点中心点
        center = self._calculate_center([a.get("location", {}) for a in attractions if a.get("location")])
        
        # 2. 确定酒店档次
        hotel_level = self._determine_hotel_level(budget_per_night)
        
        # 3. 获取该城市该档次的酒店
        if city == "杭州":
            candidates = self.hotels_db.get(hotel_level, [])
        else:
            candidates = []
        
        # 4. 计算距离中心点的距离
        for hotel in candidates:
            hotel.distance_to_center = self._calculate_distance(
                center, 
                hotel.location
            )
        
        # 5. 排序（评分 + 距离 + 价格匹配度）
        ranked = self._rank_hotels(candidates, budget_per_night)
        
        # 6. 计算总费用
        result = []
        for hotel in ranked[:top_k]:
            hotel_dict = asdict(hotel)
            hotel_dict["total_cost"] = hotel.price_per_night * nights
            hotel_dict["nights"] = nights
            result.append(hotel_dict)
        
        return result
    
    def _calculate_center(self, locations: List[Dict]) -> Dict:
        """计算POI中心点"""
        valid_locs = [loc for loc in locations if loc.get("lat") and loc.get("lng")]
        
        if not valid_locs:
            # 默认返回杭州市中心
            return {"lat": 30.2741, "lng": 120.1551}
        
        avg_lat = sum(loc["lat"] for loc in valid_locs) / len(valid_locs)
        avg_lng = sum(loc["lng"] for loc in valid_locs) / len(valid_locs)
        
        return {"lat": avg_lat, "lng": avg_lng}
    
    def _determine_hotel_level(self, budget: float) -> str:
        """确定酒店档次"""
        if budget < 250:
            return "economic"
        elif budget < 500:
            return "standard"
        else:
            return "premium"
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """计算两点距离（Haversine公式）"""
        lat1, lng1 = loc1.get("lat", 0), loc1.get("lng", 0)
        lat2, lng2 = loc2.get("lat", 0), loc2.get("lng", 0)
        
        R = 6371  # 地球半径（公里）
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _rank_hotels(self, hotels: List[Hotel], budget: float) -> List[Hotel]:
        """酒店排序"""
        def score(h: Hotel) -> float:
            # 评分权重
            rating_score = h.rating / 5.0 * 0.3
            
            # 价格匹配度
            price_diff = abs(h.price_per_night - budget) / budget if budget > 0 else 1
            price_score = (1 - min(price_diff, 1)) * 0.3
            
            # 距离权重（越近越好）
            distance_score = (1 / (h.distance_to_center + 0.5)) * 0.25
            
            # 设施完善度
            facility_score = len(h.facilities) / 10 * 0.15
            
            return rating_score + price_score + distance_score + facility_score
        
        hotels.sort(key=score, reverse=True)
        return hotels
    
    def _init_mock_data(self) -> Dict[str, List[Hotel]]:
        """初始化Mock酒店数据"""
        hotels = {
            # 经济型酒店
            "economic": [
                Hotel(
                    id="hz_hotel_001",
                    name="如家酒店(西湖店)",
                    hotel_type="经济型",
                    rating=4.3,
                    price_per_night=220,
                    location={"lat": 30.2641, "lng": 120.1551, "address": "杭州市西湖区体育场路178号"},
                    distance_to_center=0.0,  # 会动态计算
                    facilities=["WiFi", "空调", "热水", "电视"],
                    room_type="标准间",
                    description="连锁经济型酒店，干净卫生，性价比高",
                    tags=["近地铁", "西湖附近"],
                    phone="0571-87654321"
                ),
                Hotel(
                    id="hz_hotel_002",
                    name="7天酒店(武林广场店)",
                    hotel_type="经济型",
                    rating=4.1,
                    price_per_night=180,
                    location={"lat": 30.2791, "lng": 120.1651, "address": "杭州市下城区武林路123号"},
                    distance_to_center=0.0,
                    facilities=["WiFi", "空调", "热水"],
                    room_type="标准间",
                    description="经济实惠，位置便利",
                    tags=["近地铁", "商圈"],
                    phone="0571-87123456"
                ),
                Hotel(
                    id="hz_hotel_003",
                    name="汉庭酒店(河坊街店)",
                    hotel_type="经济型",
                    rating=4.2,
                    price_per_night=200,
                    location={"lat": 30.2451, "lng": 120.1701, "address": "杭州市上城区河坊街188号"},
                    distance_to_center=0.0,
                    facilities=["WiFi", "空调", "热水", "早餐"],
                    room_type="标准间",
                    description="河坊街旁，交通便利，含早餐",
                    tags=["景区附近", "早餐"],
                    phone="0571-87234567"
                ),
            ],
            
            # 舒适型酒店
            "standard": [
                Hotel(
                    id="hz_hotel_004",
                    name="维也纳酒店(西湖文化广场店)",
                    hotel_type="舒适型",
                    rating=4.5,
                    price_per_night=350,
                    location={"lat": 30.2841, "lng": 120.1701, "address": "杭州市下城区中山北路198号"},
                    distance_to_center=0.0,
                    facilities=["WiFi", "空调", "热水", "早餐", "健身房", "停车场"],
                    room_type="大床房",
                    description="舒适型商务酒店，设施齐全",
                    tags=["近地铁", "商圈", "停车场"],
                    phone="0571-87345678"
                ),
                Hotel(
                    id="hz_hotel_005",
                    name="全季酒店(西湖店)",
                    hotel_type="舒适型",
                    rating=4.6,
                    price_per_night=380,
                    location={"lat": 30.2591, "lng": 120.1453, "address": "杭州市西湖区北山路88号"},
                    distance_to_center=0.0,
                    facilities=["WiFi", "空调", "热水", "早餐", "停车场", "洗衣服务"],
                    room_type="大床房",
                    description="西湖边，环境优美，服务好",
                    tags=["西湖边", "环境好", "早餐"],
                    phone="0571-87456789"
                ),
                Hotel(
                    id="hz_hotel_006",
                    name="亚朵酒店(武林广场店)",
                    hotel_type="舒适型",
                    rating=4.7,
                    price_per_night=420,
                    location={"lat": 30.2791, "lng": 120.1651, "address": "杭州市下城区延安路528号"},
                    distance_to_center=0.0,
                    facilities=["WiFi", "空调", "热水", "早餐", "健身房", "图书馆", "停车场"],
                    room_type="大床房",
                    description="人文酒店，设计感强，服务贴心",
                    tags=["近地铁", "设计感", "图书馆"],
                    phone="0571-87567890"
                ),
            ],
            
            # 高档型酒店
            "premium": [
                Hotel(
                    id="hz_hotel_007",
                    name="西湖国宾馆",
                    hotel_type="高档型",
                    rating=4.9,
                    price_per_night=1200,
                    location={"lat": 30.2511, "lng": 120.1353, "address": "杭州市西湖区杨公堤18号"},
                    distance_to_center=0.0,
                    facilities=["WiFi", "空调", "热水", "早餐", "健身房", "游泳池", "SPA", "停车场", "管家服务"],
                    room_type="套房",
                    description="西湖边顶级酒店，环境一流，服务完美",
                    tags=["西湖边", "奢华", "环境绝佳"],
                    phone="0571-87979889"
                ),
                Hotel(
                    id="hz_hotel_008",
                    name="杭州西子湖四季酒店",
                    hotel_type="高档型",
                    rating=4.8,
                    price_per_night=1500,
                    location={"lat": 30.2471, "lng": 120.1393, "address": "杭州市西湖区灵隐路5号"},
                    distance_to_center=0.0,
                    facilities=["WiFi", "空调", "热水", "早餐", "健身房", "游泳池", "SPA", "停车场", "米其林餐厅"],
                    room_type="豪华套房",
                    description="国际五星级酒店，奢华体验",
                    tags=["五星级", "奢华", "米其林"],
                    phone="0571-88299988"
                ),
                Hotel(
                    id="hz_hotel_009",
                    name="杭州凯悦酒店",
                    hotel_type="高档型",
                    rating=4.7,
                    price_per_night=900,
                    location={"lat": 30.2891, "lng": 120.1751, "address": "杭州市江干区解放东路2号"},
                    distance_to_center=0.0,
                    facilities=["WiFi", "空调", "热水", "早餐", "健身房", "游泳池", "停车场", "行政酒廊"],
                    room_type="豪华房",
                    description="钱江新城核心，商务首选",
                    tags=["五星级", "商务", "新城区"],
                    phone="0571-86688888"
                ),
            ]
        }
        
        return hotels


# 单例
_accommodation_service = None

def get_accommodation_service() -> AccommodationService:
    """获取住宿服务单例"""
    global _accommodation_service
    if _accommodation_service is None:
        _accommodation_service = AccommodationService()
    return _accommodation_service

