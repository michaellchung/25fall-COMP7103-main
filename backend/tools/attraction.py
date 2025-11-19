"""
成员B：RAG检索服务
负责从知识库中检索相关景点、路线和旅游信息
"""
from typing import List, Dict
from loguru import logger
from dataclasses import dataclass


@dataclass
class Attraction:
    """景点数据模型"""
    id: str
    name: str
    city: str
    province: str
    category: str  # 自然景观/历史文化/现代建筑/美食/购物等
    description: str
    address: str
    opening_hours: str
    ticket_price: float
    duration_hours: float
    rating: float  # 1-5分
    best_season: str
    tips: str
    location: Dict = None  # 位置信息 {"lat": 纬度, "lng": 经度, "address": "详细地址"}
    tags: List[str] = None  # 标签列表
    
    def __post_init__(self):
        """初始化后处理"""
        if self.tags is None:
            # 根据category自动生成tags
            self.tags = [self.category]
        
        if self.location is None:
            # 如果没有提供location，根据address生成默认位置
            # 这里使用Mock数据，实际应该调用地图API
            self.location = {
                "lat": 30.25,  # 杭州大致纬度
                "lng": 120.15,  # 杭州大致经度
                "address": self.address
            }


class AttractionService:
    """RAG检索器 - 模拟向量数据库检索"""
    
    # 模拟知识库数据
    ATTRACTIONS_DB = {
        "杭州": [
            Attraction(
                id="hz001",
                name="西湖",
                city="杭州",
                province="浙江",
                category="自然景观",
                description="中国最美的湖泊，有'人间天堂'之称，拥有十景各具特色",
                address="浙江省杭州市西湖区",
                opening_hours="全天",
                ticket_price=0,
                duration_hours=3,
                rating=4.8,
                best_season="春秋两季",
                tips="建议清晨或傍晚游览，避开人流高峰",
                location={"lat": 30.2547, "lng": 120.1487, "address": "浙江省杭州市西湖区"}
            ),
            Attraction(
                id="hz002",
                name="灵隐寺",
                city="杭州",
                province="浙江",
                category="历史文化",
                description="中国最古老的佛刹，距今已有1700多年历史，雕刻精美",
                address="浙江省杭州市西湖区灵隐路1号",
                opening_hours="08:00-17:00",
                ticket_price=30,
                duration_hours=2,
                rating=4.5,
                best_season="全年",
                tips="穿着得体，尊重宗教信仰",
                location={"lat": 30.2415, "lng": 120.0985, "address": "浙江省杭州市西湖区灵隐路1号"}
            ),
            Attraction(
                id="hz003",
                name="茅家埠",
                city="杭州",
                province="浙江",
                category="美食",
                description="杭州特色美食街，汇集了龙井虾仁、东坡肉等名菜",
                address="浙江省杭州市西湖区南山路48号",
                opening_hours="10:00-22:00",
                ticket_price=0,
                duration_hours=1.5,
                rating=4.3,
                best_season="全年",
                tips="周末人多，建议工作日前往",
                location={"lat": 30.2358, "lng": 120.1298, "address": "浙江省杭州市西湖区南山路48号"}
            ),
        ],
        "南京": [
            Attraction(
                id="nj001",
                name="中山陵",
                city="南京",
                province="江苏",
                category="历史文化",
                description="孙中山先生的陵墓，宏伟壮观，是南京最著名景点",
                address="江苏省南京市玄武区石象路7号",
                opening_hours="08:00-17:00",
                ticket_price=0,
                duration_hours=2,
                rating=4.6,
                best_season="春秋",
                tips="需爬390级台阶，穿着舒适的鞋子",
                location={"lat": 32.0589, "lng": 118.8486, "address": "江苏省南京市玄武区石象路7号"}
            ),
            Attraction(
                id="nj002",
                name="夫子庙",
                city="南京",
                province="江苏",
                category="历史文化",
                description="中国最大的孔庙，拥有2500年历史，夜景特别美",
                address="江苏省南京市秦淮区平江府路1号",
                opening_hours="09:30-22:00",
                ticket_price=25,
                duration_hours=1.5,
                rating=4.4,
                best_season="全年",
                tips="晚上夜景迷人，建议7点后前往",
                location={"lat": 32.0186, "lng": 118.7938, "address": "江苏省南京市秦淮区平江府路1号"}
            ),
        ],
        "广州": [
            Attraction(
                id="gz001",
                name="广州塔",
                city="广州",
                province="广东",
                category="现代建筑",
                description="广州地标，高600米，可俯瞰整个珠江",
                address="广东省广州市海珠区阅江中路222号",
                opening_hours="09:00-23:00",
                ticket_price=150,
                duration_hours=2,
                rating=4.5,
                best_season="全年",
                tips="预订可享受优惠，高空旋转餐厅体验绝佳",
                location={"lat": 23.1088, "lng": 113.3191, "address": "广东省广州市海珠区阅江中路222号"}
            ),
            Attraction(
                id="gz002",
                name="陈家祠",
                city="广州",
                province="广东",
                category="历史文化",
                description="清代建筑艺术的典范，木雕石雕精美绝伦",
                address="广东省广州市荔湾区中山七路恩宁路34号",
                opening_hours="10:00-17:30",
                ticket_price=10,
                duration_hours=1.5,
                rating=4.3,
                best_season="全年",
                tips="免费讲解服务，建议跟随讲解员",
                location={"lat": 23.1258, "lng": 113.2438, "address": "广东省广州市荔湾区中山七路恩宁路34号"}
            ),
        ]
    }
    
    def __init__(self):
        logger.info("RAG检索器初始化完成")
    
    def retrieve_attractions(
        self,
        city: str,
        preferences: List[str] = None,
        top_k: int = 10,
        budget_min: float = 0,
        budget_max: float = 1000
    ) -> List[Attraction]:
        """
        检索景点信息
        
        Args:
            city: 城市名称
            preferences: 偏好类别列表
            top_k: 返回前k个结果
            budget_min: 预算最小值
            budget_max: 预算最大值
        
        Returns:
            景点列表
        """
        try:
            attractions = self.ATTRACTIONS_DB.get(city, [])
            logger.info(f"城市 {city} 共有 {len(attractions)} 个景点")
            
            # 按偏好过滤（如果有偏好，优先推荐匹配的，但不完全排除其他）
            if preferences:
                matched = [
                    a for a in attractions 
                    if any(pref in a.category or pref in str(a.tags) for pref in preferences)
                ]
                unmatched = [
                    a for a in attractions 
                    if not any(pref in a.category or pref in str(a.tags) for pref in preferences)
                ]
                # 匹配的排在前面，未匹配的排在后面
                attractions = matched + unmatched
                logger.info(f"偏好匹配: {len(matched)} 个，其他: {len(unmatched)} 个")
            
            # 按价格过滤
            attractions = [
                a for a in attractions 
                if budget_min <= a.ticket_price <= budget_max
            ]
            logger.info(f"价格过滤后: {len(attractions)} 个")
            
            # 按评分排序
            attractions = sorted(attractions, key=lambda x: x.rating, reverse=True)
            
            # 返回前k个
            result = attractions[:top_k]
            logger.info(f"检索到 {len(result)} 个景点 (城市: {city})")
            
            return result
        
        except Exception as e:
            logger.error(f"检索景点时出错: {e}")
            return []
    
    def get_route_suggestions(
        self,
        city: str,
        days: int,
        preferences: List[str] = None
    ) -> Dict:
        """
        获取推荐路线
        
        Args:
            city: 城市名称
            days: 天数
            preferences: 偏好类别
        
        Returns:
            路线建议字典
        """
        attractions = self.retrieve_attractions(city, preferences, top_k=min(5 * days, 15))
        
        return {
            "city": city,
            "days": days,
            "recommended_attractions": [
                {
                    "name": a.name,
                    "category": a.category,
                    "rating": a.rating,
                    "ticket_price": a.ticket_price,
                    "duration_hours": a.duration_hours
                }
                for a in attractions
            ],
            "estimated_cost": sum(a.ticket_price for a in attractions)
        }


# 全局RAG检索器实例
_attraction_service = None

def get_attraction_service() -> AttractionService:
    """获取全局RAG检索器实例"""
    global _attraction_service
    if _attraction_service is None:
        _attraction_service = AttractionService()
    return _attraction_service

