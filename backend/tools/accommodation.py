"""
Tool 4: 住宿查询工具
查询目的地的酒店住宿
"""
from typing import List, Dict
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class Hotel:
    """酒店信息"""
    id: str
    name: str
    city: str
    hotel_type: str  # "经济型" | "舒适型" | "高档型"
    rating: float  # 评分 (0-5)
    price_per_night: float  # 每晚价格
    location: Dict  # {"lat": 30.25, "lng": 120.13, "address": "..."}
    facilities: List[str]  # ["WiFi", "早餐", "停车场", "健身房"]
    room_type: str  # "标准间" | "大床房" | "套房"
    description: str  # 酒店描述
    tags: List[str]  # ["近地铁", "景区附近", "商圈"]
    phone: str  # 联系电话


class AccommodationTool:
    """住宿查询工具 - Tool 4"""
    
    def __init__(self):
        logger.info("住宿查询工具初始化完成")
    
    def query_hotels(
        self,
        city: str,
        companions_count: int = 1,
        price_max: float = 1000,
        location_range: Dict = None,  # 位置范围
        rating_min: float = 0.0,
        top_k: int = 5
    ) -> List[Dict]:
        """
        查询酒店
        
        Args:
            city: 城市
            companions_count: 入住人数
            price_max: 最高每晚价格
            location_range: 位置范围
            rating_min: 最低评分
            top_k: 返回数量
        
        Returns:
            酒店列表
        """
        logger.info(f"查询酒店: {city}, 人数: {companions_count}, topK: {top_k}")
        
        # Mock数据 - 返回杭州酒店
        hotels = self._get_mock_hangzhou_hotels()
        
        # 过滤
        filtered = []
        for hotel in hotels:
            # 价格过滤
            if hotel.price_per_night > price_max:
                continue
            # 评分过滤
            if hotel.rating < rating_min:
                continue
            
            filtered.append(hotel)
        
        # 按评分和价格综合排序
        filtered.sort(key=lambda x: (x.rating, -x.price_per_night), reverse=True)
        
        return [asdict(hotel) for hotel in filtered[:top_k]]
    
    def _get_mock_hangzhou_hotels(self) -> List[Hotel]:
        """返回杭州的Mock酒店数据"""
        return [
            Hotel(
                name="杭州西湖国宾馆",
                city="杭州",
                hotel_type="高档型",
                rating=4.8,
                price_per_night=980,
                location={"lat": 30.2471, "lng": 120.1359, "address": "浙江省杭州市西湖区杨公堤18号"},
                facilities=["WiFi", "早餐", "停车场", "健身房", "游泳池", "spa"],
                room_type="高级大床房",
                description="位于西湖边的五星级酒店，环境优雅，服务一流，是政要接待的首选。",
                tags=["五星级", "西湖景观", "高端商务"]
            ),
            Hotel(
                name="杭州西湖柳莺里酒店",
                city="杭州",
                hotel_type="高档型",
                rating=4.7,
                price_per_night=750,
                location={"lat": 30.2513, "lng": 120.1387, "address": "浙江省杭州市西湖区北山街107号"},
                facilities=["WiFi", "早餐", "停车场", "健身房"],
                room_type="湖景大床房",
                description="精品酒店，紧邻西湖，房间设计雅致，可欣赏湖景。",
                tags=["精品酒店", "西湖景观", "设计感"]
            ),
            Hotel(
                name="杭州开元名都大酒店",
                city="杭州",
                hotel_type="舒适型",
                rating=4.6,
                price_per_night=480,
                location={"lat": 30.2591, "lng": 120.1619, "address": "浙江省杭州市上城区庆春路78号"},
                facilities=["WiFi", "早餐", "停车场", "健身房", "会议室"],
                room_type="商务标准间",
                description="四星级商务酒店，位于市中心，交通便利，性价比高。",
                tags=["商务酒店", "市中心", "交通便利"]
            ),
            Hotel(
                name="如家酒店（西湖店）",
                city="杭州",
                hotel_type="经济型",
                rating=4.3,
                price_per_night=220,
                location={"lat": 30.2534, "lng": 120.1501, "address": "浙江省杭州市西湖区体育场路178号"},
                facilities=["WiFi", "早餐"],
                room_type="标准间",
                description="经济型连锁酒店，干净整洁，距离西湖步行可达。",
                tags=["经济实惠", "连锁品牌", "近西湖"]
            ),
            Hotel(
                name="汉庭酒店（武林广场店）",
                city="杭州",
                hotel_type="经济型",
                rating=4.2,
                price_per_night=200,
                location={"lat": 30.2792, "lng": 120.1619, "address": "浙江省杭州市下城区武林路123号"},
                facilities=["WiFi", "早餐"],
                room_type="标准间",
                description="经济型酒店，位于武林商圈，购物方便。",
                tags=["经济实惠", "商圈", "购物方便"]
            ),
            Hotel(
                name="全季酒店（西湖文化广场店）",
                city="杭州",
                hotel_type="舒适型",
                rating=4.5,
                price_per_night=350,
                location={"lat": 30.2871, "lng": 120.1647, "address": "浙江省杭州市下城区中山北路318号"},
                facilities=["WiFi", "早餐", "健身房"],
                room_type="大床房",
                description="中档连锁酒店，设计简约现代，近地铁站。",
                tags=["近地铁", "设计感", "性价比高"]
            ),
            Hotel(
                name="锦江之星（河坊街店）",
                city="杭州",
                hotel_type="经济型",
                rating=4.1,
                price_per_night=180,
                location={"lat": 30.2443, "lng": 120.1701, "address": "浙江省杭州市上城区河坊街267号"},
                description="经济型酒店，位于河坊街，逛街方便，周边美食多。",
                facilities=["WiFi"],
                room_type="标准间",
                tags=["经济实惠", "古街旁", "美食多"]
            ),
            Hotel(
                name="亚朵酒店（西湖店）",
                city="杭州",
                hotel_type="舒适型",
                rating=4.6,
                price_per_night=420,
                location={"lat": 30.2518, "lng": 120.1448, "address": "浙江省杭州市西湖区北山街58号"},
                facilities=["WiFi", "早餐", "健身房", "图书馆", "下午茶"],
                room_type="舒适大床房",
                description="新型人文酒店，提供免费图书和下午茶，服务贴心。",
                tags=["人文酒店", "服务好", "近西湖"]
            )
        ]


# 全局单例
_accommodation_tool = None

def get_accommodation_tool() -> AccommodationTool:
    """获取住宿工具实例"""
    global _accommodation_tool
    if _accommodation_tool is None:
        _accommodation_tool = AccommodationTool()
    return _accommodation_tool

