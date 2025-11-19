"""
Tool 1: 交通查询工具
查询出发地到目的地的交通方式（飞机、列车）
"""
from typing import List, Dict
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class TransportOption:
    """交通方案"""
    method: str  # "飞机" | "高铁" | "普通火车"
    duration_hours: float  # 时长（小时）
    cost_per_person: float  # 单人费用
    total_cost: float  # 总费用
    departure_time: str  # 建议出发时间
    arrival_time: str  # 预计到达时间
    description: str  # 方案描述
    recommendation_score: float  # 推荐分数 (0-1)
    details: Dict  # 详细信息


class TransportTool:
    """交通查询工具 - Tool 1"""
    
    def __init__(self):
        logger.info("交通查询工具初始化完成")
    
    def query_transport(
        self,
        departure_city: str,
        destination_city: str,
        date: str = None,
        time_period: str = None,  # 时间段（小时）
        companions_count: int = 1,
        top_k: int = 3
    ) -> List[Dict]:
        """
        查询出发地到目的地的交通方式
        
        Args:
            departure_city: 出发城市
            destination_city: 目的地城市
            date: 出发日期
            time_period: 时间段
            companions_count: 出行人数
            top_k: 返回结果数量
        
        Returns:
            交通方案列表
        """
        logger.info(f"查询交通: {departure_city} -> {destination_city}, 人数: {companions_count}")
        
        # Mock数据 - 返回到杭州的交通方案
        options = self._get_mock_hangzhou_transport(
            departure_city, destination_city, companions_count
        )
        
        return [asdict(opt) for opt in options[:top_k]]
    
    def _get_mock_hangzhou_transport(
        self,
        departure_city: str,
        destination_city: str,
        companions_count: int
    ) -> List[TransportOption]:
        """返回杭州的Mock交通数据"""
        
        # 如果目的地不是杭州，返回通用数据
        if destination_city != "杭州":
            return [
                TransportOption(
                    method="高铁",
                    duration_hours=4.0,
                    cost_per_person=350,
                    departure_time="08:30",
                    arrival_time="12:30",
                    description=f"从{departure_city}到{destination_city}的便捷高铁",
                    details={
                        "train_number": "G1234",
                        "seat_type": "二等座",
                        "total_cost": 350 * companions_count
                    }
                )
            ]
        
        # 杭州的Mock数据
        options = []
        
        # 根据出发地返回不同的交通方案
        if departure_city in ["北京", "上海", "广州", "深圳", "南京", "苏州"]:
            # 高铁方案
            base_price = {
                "北京": 538,
                "上海": 73,
                "广州": 876,
                "深圳": 920,
                "南京": 244,
                "苏州": 49
            }.get(departure_city, 300)
            
            duration = {
                "北京": 5.5,
                "上海": 1.0,
                "广州": 7.5,
                "深圳": 8.0,
                "南京": 2.0,
                "苏州": 0.5
            }.get(departure_city, 4.0)
            
            options.append(TransportOption(
                method="高铁",
                duration_hours=duration,
                cost_per_person=base_price,
                departure_time="08:30",
                arrival_time=self._calculate_arrival_time("08:30", duration),
                description=f"从{departure_city}到杭州的高铁，舒适便捷",
                details={
                    "train_number": "G1234",
                    "seat_type": "二等座",
                    "station": f"{departure_city}站 → 杭州东站",
                    "total_cost": base_price * companions_count,
                    "booking_tip": "12306官网购票，支持改签"
                }
            ))
        
        # 如果是较远的城市，添加飞机方案
        if departure_city in ["北京", "广州", "深圳"]:
            flight_price = {
                "北京": 800,
                "广州": 950,
                "深圳": 1000
            }.get(departure_city, 800)
            
            flight_duration = {
                "北京": 2.5,
                "广州": 2.0,
                "深圳": 2.5
            }.get(departure_city, 2.5)
            
            options.append(TransportOption(
                method="飞机",
                duration_hours=flight_duration,
                cost_per_person=flight_price,
                departure_time="09:00",
                arrival_time=self._calculate_arrival_time("09:00", flight_duration),
                description=f"从{departure_city}到杭州的航班，最快捷的选择",
                details={
                    "flight_number": "CA1234",
                    "airline": "国航/东航",
                    "airport": f"{departure_city}机场 → 杭州萧山国际机场",
                    "total_cost": flight_price * companions_count,
                    "booking_tip": "提前7-15天预订价格更优惠"
                }
            ))
        
        # 如果没有匹配的城市，返回默认方案
        if not options:
            options.append(TransportOption(
                method="高铁",
                duration_hours=4.0,
                cost_per_person=300,
                departure_time="08:30",
                arrival_time="12:30",
                description=f"从{departure_city}到杭州的高铁",
                details={
                    "train_number": "G1234",
                    "seat_type": "二等座",
                    "total_cost": 300 * companions_count
                }
            ))
        
        # 按性价比排序（时间*价格）
        options.sort(key=lambda x: x.duration_hours * x.cost_per_person)
        
        return options
    
    def _calculate_arrival_time(self, departure_time: str, duration_hours: float) -> str:
        """计算到达时间"""
        from datetime import datetime, timedelta
        
        try:
            dept_time = datetime.strptime(departure_time, "%H:%M")
            arrival = dept_time + timedelta(hours=duration_hours)
            return arrival.strftime("%H:%M")
        except:
            return "约到达"


# 全局单例
_transport_tool = None

def get_transport_tool() -> TransportTool:
    """获取交通工具实例"""
    global _transport_tool
    if _transport_tool is None:
        _transport_tool = TransportTool()
    return _transport_tool

