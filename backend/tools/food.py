"""
Tool 3: 美食查询工具
查询目的地的美食餐厅
"""
from typing import List, Dict
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class Restaurant:
    """餐厅信息"""
    id: str
    name: str
    city: str
    cuisine_type: str  # "杭帮菜" | "小吃" | "火锅"
    rating: float  # 评分 (0-5)
    avg_price: float  # 人均消费
    location: Dict  # {"lat": 30.25, "lng": 120.13, "address": "..."}
    distance_km: float  # 距离参考点的距离
    signature_dishes: List[str]  # 招牌菜
    description: str  # 店铺描述
    opening_hours: str  # 营业时间
    tags: List[str]  # ["必吃", "网红店", "老字号"]
    phone: str  # 联系电话


class FoodTool:
    """美食查询工具 - Tool 3"""
    
    def __init__(self):
        logger.info("美食查询工具初始化完成")
    
    def query_restaurants(
        self,
        city: str,
        category: str = None,  # 类别
        preferences: List[str] = None,  # 偏好
        price_max: float = 1000,
        rating_min: float = 0.0,
        location_range: Dict = None,  # 位置范围
        top_k: int = 5
    ) -> List[Dict]:
        """
        查询美食餐厅
        
        Args:
            city: 城市
            category: 类别（中餐、西餐、小吃等）
            preferences: 偏好
            price_max: 最高人均价格
            rating_min: 最低评分
            location_range: 位置范围
            top_k: 返回数量
        
        Returns:
            餐厅列表
        """
        logger.info(f"查询美食: {city}, 类别: {category}, topK: {top_k}")
        
        # Mock数据 - 返回杭州美食
        restaurants = self._get_mock_hangzhou_restaurants()
        
        # 过滤
        filtered = []
        for rest in restaurants:
            # 价格过滤
            if rest.avg_price > price_max:
                continue
            # 评分过滤
            if rest.rating < rating_min:
                continue
            # 类别过滤
            if category and category not in rest.cuisine_type:
                continue
            
            filtered.append(rest)
        
        # 按评分排序
        filtered.sort(key=lambda x: x.rating, reverse=True)
        
        return [asdict(rest) for rest in filtered[:top_k]]
    
    def _get_mock_hangzhou_restaurants(self) -> List[Restaurant]:
        """返回杭州的Mock美食数据"""
        return [
            Restaurant(
                name="外婆家（湖滨店）",
                city="杭州",
                cuisine_type="杭帮菜",
                rating=4.6,
                avg_price=80,
                location={"lat": 30.2547, "lng": 120.1619, "address": "浙江省杭州市上城区湖滨路53号"},
                signature_dishes=["西湖醋鱼", "龙井虾仁", "东坡肉"],
                description="杭州知名连锁餐厅，主打杭帮菜，性价比高，环境优雅。",
                opening_hours="11:00-21:30",
                tags=["必吃", "高性价比", "连锁品牌"]
            ),
            Restaurant(
                name="楼外楼（孤山路店）",
                city="杭州",
                cuisine_type="杭帮菜",
                rating=4.7,
                avg_price=150,
                location={"lat": 30.2566, "lng": 120.1421, "address": "浙江省杭州市西湖区孤山路30号"},
                signature_dishes=["西湖醋鱼", "叫化童鸡", "宋嫂鱼羹"],
                description="百年老字号，位于西湖边，是品尝正宗杭帮菜的首选之地。",
                opening_hours="11:00-14:00, 17:00-21:00",
                tags=["必吃", "老字号", "湖景餐厅"]
            ),
            Restaurant(
                name="知味观（湖滨店）",
                city="杭州",
                cuisine_type="小吃",
                rating=4.5,
                avg_price=60,
                location={"lat": 30.2541, "lng": 120.1635, "address": "浙江省杭州市上城区仁和路83号"},
                signature_dishes=["猫耳朵", "鲜肉小笼", "片儿川"],
                description="杭州著名小吃店，提供各种传统杭式点心和面食。",
                opening_hours="07:00-21:00",
                tags=["必吃", "老字号", "小吃", "早餐推荐"]
            ),
            Restaurant(
                name="绿茶餐厅（龙井店）",
                city="杭州",
                cuisine_type="创意杭帮菜",
                rating=4.6,
                avg_price=90,
                location={"lat": 30.2158, "lng": 120.1204, "address": "浙江省杭州市西湖区龙井路1号"},
                signature_dishes=["面包诱惑", "绿茶烤鱼", "石锅牛蛙"],
                description="人气网红餐厅，融合传统杭帮菜与现代创意，环境清新。",
                opening_hours="11:00-22:00",
                tags=["网红店", "创意菜", "环境好"]
            ),
            Restaurant(
                name="奎元馆（解放路店）",
                city="杭州",
                cuisine_type="面食",
                rating=4.5,
                avg_price=40,
                location={"lat": 30.2629, "lng": 120.1694, "address": "浙江省杭州市上城区解放路154号"},
                signature_dishes=["虾爆鳝面", "片儿川", "牛肉粉丝"],
                description="百年面馆，以虾爆鳝面闻名，是杭州人的最爱。",
                opening_hours="06:30-20:00",
                tags=["老字号", "面食", "早餐推荐"]
            ),
            Restaurant(
                name="新白鹿餐厅",
                city="杭州",
                cuisine_type="杭帮菜",
                rating=4.6,
                avg_price=85,
                location={"lat": 30.2473, "lng": 120.1598, "address": "浙江省杭州市上城区平海路124号"},
                signature_dishes=["酱鸭", "糖醋里脊", "油焖春笋"],
                description="杭州本地连锁品牌，菜品丰富，量大实惠，性价比高。",
                opening_hours="11:00-21:30",
                tags=["高性价比", "量大", "本地人推荐"]
            ),
            Restaurant(
                name="胡庆余堂药膳",
                city="杭州",
                cuisine_type="药膳",
                rating=4.4,
                avg_price=120,
                location={"lat": 30.2451, "lng": 120.1672, "address": "浙江省杭州市上城区大井巷95号"},
                signature_dishes=["虫草花炖鸡", "药膳排骨", "养生粥"],
                description="老字号药店开设的药膳餐厅，注重养生保健。",
                opening_hours="11:00-14:00, 17:00-20:30",
                tags=["特色餐厅", "养生", "药膳"]
            ),
            Restaurant(
                name="南宋御街小吃",
                city="杭州",
                cuisine_type="小吃",
                rating=4.3,
                avg_price=35,
                location={"lat": 30.2412, "lng": 120.1681, "address": "浙江省杭州市上城区中山中路"},
                signature_dishes=["定胜糕", "葱包桧", "臭豆腐"],
                description="汇集各种杭州传统小吃，价格实惠，适合边走边吃。",
                opening_hours="09:00-22:00",
                tags=["小吃", "街边美食", "实惠"]
            )
        ]


# 全局单例
_food_tool = None

def get_food_tool() -> FoodTool:
    """获取美食工具实例"""
    global _food_tool
    if _food_tool is None:
        _food_tool = FoodTool()
    return _food_tool

