"""
美食推荐工具
根据景点位置查询附近美食店铺
"""
from typing import List, Dict
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class Restaurant:
    """餐厅信息"""
    id: str
    name: str
    cuisine_type: str  # "杭帮菜" | "小吃" | "火锅" | "西餐"
    rating: float  # 评分 (0-5)
    avg_price: float  # 人均消费
    location: Dict  # {"lat": 30.25, "lng": 120.13, "address": "..."}
    distance_km: float  # 距离参考点的距离
    signature_dishes: List[str]  # 招牌菜
    description: str  # 店铺描述
    opening_hours: str  # 营业时间
    tags: List[str]  # ["必吃", "网红店", "老字号"]
    phone: str  # 联系电话


class FoodRecommendationService:
    """美食推荐服务"""
    
    def __init__(self):
        logger.info("美食推荐服务初始化完成")
        # Mock数据库
        self.restaurants_db = self._init_mock_data()
    
    def get_restaurants_for_attractions(
        self,
        attractions: List[Dict],
        top_k_per_attraction: int = 2
    ) -> Dict[str, List[Dict]]:
        """
        为每个景点推荐附近餐厅
        
        Args:
            attractions: 景点列表
            top_k_per_attraction: 每个景点推荐餐厅数量
        
        Returns:
            {景点名称: [餐厅列表]}
        """
        logger.info(f"为 {len(attractions)} 个景点推荐餐厅")
        
        result = {}
        for attraction in attractions:
            attraction_name = attraction.get("name", "")
            # 根据景点名称返回附近餐厅
            nearby_restaurants = self._get_nearby_restaurants(
                attraction_name, 
                top_k_per_attraction
            )
            result[attraction_name] = [asdict(r) for r in nearby_restaurants]
        
        return result
    
    def _get_nearby_restaurants(
        self, 
        attraction_name: str, 
        top_k: int
    ) -> List[Restaurant]:
        """获取景点附近餐厅（Mock）"""
        
        # 根据景点返回对应的餐厅
        attraction_restaurants = {
            "西湖": ["外婆家(湖滨店)", "楼外楼(孤山店)", "知味观(湖滨店)"],
            "灵隐寺": ["灵隐寺素斋", "龙井茶室", "山外山"],
            "雷峰塔": "西湖周边餐厅",
            "河坊街": ["状元馆", "咬不得生煎", "新丰小吃"],
            "宋城": ["宋城千古情餐厅", "杭州酒家", "外婆家(宋城店)"],
            "西溪湿地": ["西溪湿地餐厅", "绿茶餐厅", "炉鱼"],
            "千岛湖": ["千岛湖鱼头", "农家菜", "湖鲜馆"],
            "南浔古镇": ["南浔特色菜", "古镇小吃", "江南菜馆"]
        }
        
        # 获取餐厅名称列表
        restaurant_names = attraction_restaurants.get(attraction_name, [])
        if isinstance(restaurant_names, str):
            # 如果是字符串，使用西湖的餐厅作为默认
            restaurant_names = attraction_restaurants["西湖"]
        
        # 返回Top K
        restaurants = []
        for name in restaurant_names[:top_k]:
            restaurant = self.restaurants_db.get(name)
            if restaurant:
                restaurants.append(restaurant)
        
        return restaurants
    
    def _init_mock_data(self) -> Dict[str, Restaurant]:
        """初始化Mock餐厅数据"""
        restaurants = [
            # 西湖周边
            Restaurant(
                id="hz_food_001",
                name="外婆家(湖滨店)",
                cuisine_type="杭帮菜",
                rating=4.5,
                avg_price=80,
                location={"lat": 30.2591, "lng": 120.1653, "address": "杭州市上城区平海路124号"},
                distance_km=0.5,
                signature_dishes=["西湖醋鱼", "东坡肉", "龙井虾仁"],
                description="杭州知名连锁餐厅，主打杭帮菜，性价比高",
                opening_hours="10:30-21:30",
                tags=["必吃", "网红店", "排队"],
                phone="0571-87777777"
            ),
            Restaurant(
                id="hz_food_002",
                name="楼外楼(孤山店)",
                cuisine_type="杭帮菜",
                rating=4.7,
                avg_price=150,
                location={"lat": 30.2611, "lng": 120.1423, "address": "杭州市西湖区孤山路30号"},
                distance_km=0.8,
                signature_dishes=["叫化鸡", "西湖醋鱼", "龙井虾仁", "宋嫂鱼羹"],
                description="百年老字号，西湖边最有名的餐厅，杭帮菜代表",
                opening_hours="11:00-21:00",
                tags=["老字号", "必吃", "景观好"],
                phone="0571-87969682"
            ),
            Restaurant(
                id="hz_food_003",
                name="知味观(湖滨店)",
                cuisine_type="杭帮菜/小吃",
                rating=4.4,
                avg_price=60,
                location={"lat": 30.2571, "lng": 120.1643, "address": "杭州市上城区仁和路83号"},
                distance_km=0.6,
                signature_dishes=["猫耳朵", "片儿川", "小笼包", "虾爆鳝面"],
                description="杭州老字号小吃店，早餐和小吃很受欢迎",
                opening_hours="06:30-21:00",
                tags=["老字号", "小吃", "早餐"],
                phone="0571-87065921"
            ),
            
            # 灵隐寺周边
            Restaurant(
                id="hz_food_004",
                name="灵隐寺素斋",
                cuisine_type="素食",
                rating=4.6,
                avg_price=100,
                location={"lat": 30.2411, "lng": 120.0967, "address": "杭州市西湖区灵隐路法云弄16号"},
                distance_km=0.2,
                signature_dishes=["罗汉斋", "素鹅", "素鸡", "笋干老鸭煲"],
                description="寺庙素斋，环境清幽，菜品精致",
                opening_hours="10:30-20:00",
                tags=["素食", "特色", "环境好"],
                phone="0571-87968665"
            ),
            Restaurant(
                id="hz_food_005",
                name="龙井茶室",
                cuisine_type="茶餐厅",
                rating=4.5,
                avg_price=80,
                location={"lat": 30.2381, "lng": 120.1087, "address": "杭州市西湖区龙井路1号"},
                distance_km=1.5,
                signature_dishes=["龙井虾仁", "龙井茶", "茶香鸡", "茶叶蛋"],
                description="龙井茶园旁，可以品茶用餐，环境优美",
                opening_hours="09:00-21:00",
                tags=["特色", "茶文化", "环境好"],
                phone="0571-87964221"
            ),
            Restaurant(
                id="hz_food_006",
                name="山外山",
                cuisine_type="杭帮菜",
                rating=4.6,
                avg_price=120,
                location={"lat": 30.2421, "lng": 120.1007, "address": "杭州市西湖区玉古路5号"},
                distance_km=0.8,
                signature_dishes=["西湖醋鱼", "东坡肉", "叫化鸡"],
                description="西湖边老牌餐厅，环境好，菜品正宗",
                opening_hours="11:00-21:00",
                tags=["老字号", "环境好"],
                phone="0571-87977688"
            ),
            
            # 河坊街周边
            Restaurant(
                id="hz_food_007",
                name="状元馆",
                cuisine_type="杭帮菜",
                rating=4.3,
                avg_price=70,
                location={"lat": 30.2451, "lng": 120.1701, "address": "杭州市上城区河坊街85号"},
                distance_km=0.1,
                signature_dishes=["状元蹄", "叫化鸡", "西湖醋鱼"],
                description="河坊街老店，环境古色古香",
                opening_hours="10:30-21:30",
                tags=["老字号", "特色"],
                phone="0571-87813777"
            ),
            Restaurant(
                id="hz_food_008",
                name="咬不得生煎",
                cuisine_type="小吃",
                rating=4.5,
                avg_price=30,
                location={"lat": 30.2461, "lng": 120.1691, "address": "杭州市上城区河坊街158号"},
                distance_km=0.05,
                signature_dishes=["生煎包", "小笼包", "馄饨"],
                description="河坊街网红小吃店，生煎很有特色",
                opening_hours="08:00-20:00",
                tags=["网红店", "小吃", "排队"],
                phone="0571-87065432"
            ),
            Restaurant(
                id="hz_food_009",
                name="新丰小吃",
                cuisine_type="小吃",
                rating=4.4,
                avg_price=25,
                location={"lat": 30.2471, "lng": 120.1681, "address": "杭州市上城区中山中路123号"},
                distance_km=0.3,
                signature_dishes=["虾肉小笼", "牛肉粉丝", "馄饨"],
                description="杭州本地连锁小吃店，价格实惠",
                opening_hours="06:30-21:00",
                tags=["小吃", "实惠", "早餐"],
                phone="0571-87023456"
            ),
            
            # 宋城周边
            Restaurant(
                id="hz_food_010",
                name="外婆家(宋城店)",
                cuisine_type="杭帮菜",
                rating=4.4,
                avg_price=75,
                location={"lat": 30.2121, "lng": 120.1143, "address": "杭州市西湖区之江路148号"},
                distance_km=0.5,
                signature_dishes=["茶香鸡", "麻婆豆腐", "青豆泥"],
                description="外婆家连锁店，宋城附近用餐方便",
                opening_hours="10:30-21:30",
                tags=["连锁", "性价比高"],
                phone="0571-87333333"
            ),
            
            # 西溪湿地周边
            Restaurant(
                id="hz_food_011",
                name="绿茶餐厅",
                cuisine_type="创意杭帮菜",
                rating=4.6,
                avg_price=90,
                location={"lat": 30.2691, "lng": 120.0753, "address": "杭州市西湖区文二西路551号"},
                distance_km=1.0,
                signature_dishes=["面包诱惑", "绿茶烤鱼", "石锅牛蛙"],
                description="网红餐厅，环境好，菜品创新",
                opening_hours="10:30-22:00",
                tags=["网红店", "环境好", "排队"],
                phone="0571-88812345"
            ),
        ]
        
        # 转换为字典
        return {r.name: r for r in restaurants}


# 单例
_food_service = None

def get_food_service() -> FoodRecommendationService:
    """获取美食服务单例"""
    global _food_service
    if _food_service is None:
        _food_service = FoodRecommendationService()
    return _food_service

