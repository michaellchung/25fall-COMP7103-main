"""
跨城交通查询工具
提供出发地到目的地的交通方案（飞机、火车、自驾）
"""
from typing import List, Dict
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class TransportOption:
    """交通方案"""
    method: str  # "飞机" | "高铁" | "自驾"
    duration_hours: float  # 时长（小时）
    cost_per_person: float  # 单人费用
    total_cost: float  # 总费用
    departure_time: str  # 建议出发时间
    arrival_time: str  # 预计到达时间
    description: str  # 方案描述
    recommendation_score: float  # 推荐分数 (0-1)
    details: Dict  # 详细信息


class InterCityTransportService:
    """跨城交通服务"""
    
    def __init__(self):
        logger.info("跨城交通服务初始化完成")
    
    def get_transport_options(
        self,
        departure_city: str,
        destination_city: str,
        travel_date: str = None,
        companions_count: int = 1
    ) -> List[Dict]:
        """
        获取跨城交通方案
        
        Args:
            departure_city: 出发城市
            destination_city: 目的地城市
            travel_date: 出行日期 (可选)
            companions_count: 出行人数
        
        Returns:
            交通方案列表，按推荐度排序
        """
        logger.info(f"查询交通方案: {departure_city} → {destination_city}, {companions_count}人")
        
        # Mock数据：北京到杭州的三种交通方案
        if destination_city == "杭州":
            options = self._get_mock_hangzhou_transport(departure_city, companions_count)
        else:
            # 其他城市返回通用方案
            options = self._get_generic_transport(departure_city, destination_city, companions_count)
        
        # 转换为字典列表
        return [asdict(opt) for opt in options]
    
    def _get_mock_hangzhou_transport(
        self, 
        departure_city: str, 
        companions_count: int
    ) -> List[TransportOption]:
        """返回到杭州的Mock交通数据"""
        
        # 方案1: 高铁（推荐）
        high_speed_train = TransportOption(
            method="高铁",
            duration_hours=5.0,
            cost_per_person=553,
            total_cost=553 * companions_count,
            departure_time="建议早班 08:00-10:00",
            arrival_time="约5小时后到达",
            description="舒适便捷，性价比高，适合1200km的中长途旅行",
            recommendation_score=0.95,
            details={
                "train_type": "G字头高铁",
                "seat_type": "二等座",
                "station": f"{departure_city}站 → 杭州东站",
                "booking_tip": "12306官网/App购票，支持改签",
                "distance_km": 1200
            }
        )
        
        # 方案2: 飞机
        flight = TransportOption(
            method="飞机",
            duration_hours=2.5,
            cost_per_person=850,
            total_cost=850 * companions_count,
            departure_time="建议早班机 08:00-10:00",
            arrival_time="约2.5小时后到达（含值机候机时间）",
            description="最快捷的方式，适合1200km的长途旅行",
            recommendation_score=0.85,
            details={
                "airline": "参考航班: 国航/东航/南航",
                "airport": f"{departure_city}首都机场 → 杭州萧山机场",
                "booking_tip": "建议提前7-15天预订，价格更优惠",
                "distance_km": 1200
            }
        )
        
        # 方案3: 自驾
        self_drive = TransportOption(
            method="自驾",
            duration_hours=12.0,
            cost_per_person=500,
            total_cost=1000,  # 总费用固定（油费+过路费）
            departure_time="建议早晨出发 07:00-08:00",
            arrival_time="约12小时后到达",
            description=f"自由灵活，适合{companions_count}人同行，1200km路程",
            recommendation_score=0.60,
            details={
                "distance_km": 1200,
                "fuel_cost": 600,
                "toll_fee": 400,
                "route_tip": "建议使用高德/百度地图导航",
                "rest_tip": "每2小时休息一次，注意安全"
            }
        )
        
        # 按推荐度排序
        return sorted(
            [high_speed_train, flight, self_drive],
            key=lambda x: x.recommendation_score,
            reverse=True
        )
    
    def _get_generic_transport(
        self,
        departure_city: str,
        destination_city: str,
        companions_count: int
    ) -> List[TransportOption]:
        """返回通用交通方案"""
        # 简化版，返回基本方案
        return [
            TransportOption(
                method="高铁",
                duration_hours=4.0,
                cost_per_person=400,
                total_cost=400 * companions_count,
                departure_time="建议早班",
                arrival_time="约4小时后到达",
                description="推荐方案",
                recommendation_score=0.9,
                details={}
            )
        ]


# 单例
_transport_service = None

def get_transport_service() -> InterCityTransportService:
    """获取交通服务单例"""
    global _transport_service
    if _transport_service is None:
        _transport_service = InterCityTransportService()
    return _transport_service

