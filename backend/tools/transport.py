"""
Tool 1: 交通查询工具
查询出发地到目的地的交通方式（飞机、列车）
"""
from loguru import logger
import requests
import json
from urllib.parse import quote
from datetime import datetime, timedelta
from backend.tools.light_RAG import *

@dataclass
class TransportOption:
    """交通方案"""
    method: str  # "飞机" | "高铁" | "普通火车"
    duration_hours: float  # 时长（小时）
    cost_per_person: float  # 单人费用
    departure_time: str  # 建议出发时间
    arrival_time: str  # 预计到达时间
    description: str  # 方案描述
    details: Dict  # 详细信息

class TransportTool:
    """交通查询工具 - Tool 1"""
    
    def __init__(self,
                 departure_city: str,
                 destination_city: str,
                 user_preference: str,
                 date: str = None,
                 time_period: str = None,  # 时间段（小时）
                 companions_count: int = 1,
                 top_k: int = 3):

        self.departure_city = departure_city
        self.destination_city = destination_city
        self.date = date
        self.time_period = time_period
        self.companions_count = companions_count
        self.top_k = top_k
        self.train_cookies = None
        self.train_headers = None
        self.train_inf_url = None
        self.train_price_url = None
        self.train_price_data = None
        self.init_train_query_data()
        # 传入的用户交通出行偏好（预算、时间）
        self.user_preference = user_preference
        logger.info("交通查询工具初始化完成")

    def init_train_query_data(self):
        file = open('../../data/train_robots_json/city.json', encoding='utf-8')  # 12306中城市用字母指代，存储在city.json文件中
        json_data = json.loads(file.read())
        from_station = self.departure_city
        to_station = self.destination_city
        encoded_from_station = quote(from_station)
        encoded_to_station = quote(to_station)
        self.train_inf_url = f"https://kyfw.12306.cn/otn/leftTicket/queryG?leftTicketDTO.train_date={self.date}&leftTicketDTO.from_station={json_data[from_station]}&leftTicketDTO.to_station={json_data[to_station]}&purpose_codes=ADULT"
        self.train_price_url = f"https://kyfw.12306.cn/otn/leftTicketPrice/queryAllPublicPrice?leftTicketDTO.train_date={self.date}&leftTicketDTO.from_station={json_data[from_station]}&leftTicketDTO.to_station={json_data[to_station]}&purpose_codes=ADULT"
        # 这里注意cookies写自己的
        self.train_cookies = {
            "_jc_save_fromDate": "2025-11-26",
            "_jc_save_fromStation": f"{encoded_from_station},{json_data[from_station]}",  # 使用编码后的中文字符
            "_jc_save_toDate": "2025-11-18",
            "_jc_save_toStation": f"{encoded_to_station},{json_data[to_station]}",  # 使用编码后的中文字符
            "_jc_save_wfdc_flag": "dc",
            "_uab_collina": "",
            "BIGipServerotn": "",
            "BIGipServerpassport": "",
            "BIGipServerportal": "",
            "cursorStatus": "off",
            "guidesStatus": "off",
            "highContrastMode": "defaltMode",
            "JSESSIONID": "your JSESSIONID",
            "route": "your route",
            "tk": "your tk",
            "uKey": "your ukey"
        }
        self.train_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0"
        }
        price_res = requests.get(url=self.train_price_url, headers=self.train_headers, cookies=self.train_cookies)
        self.train_price_data = price_res.json()['data']

    def query_transport(self) -> List[Dict]:
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
        logger.info(f"查询交通: {self.departure_city} -> {self.destination_city}, 人数: {self.companions_count}")
        
        # 高铁+飞机，所有的出行方式得到options
        options = self.transport_data()
        # 旧方案：直接返回top k个方案的list
        # return [asdict(opt) for opt in options[:self.top_k]]
        return options

    def get_train_inf(self):
        train_inf = {
            "highspeed": [],
            "normal": [],
            "hs_bed": [],
                     }

        t2c = open('../../data/train_robots_json/telecode2city.json', encoding='utf-8')
        t2c_data = json.loads(t2c.read())

        from_station = self.departure_city
        to_station = self.destination_city

        url = self.train_inf_url
        cookies = self.train_cookies
        headers = self.train_headers

        response = requests.get(url=url, headers=headers, cookies=cookies)
        rj = response.json()['data']['result']
        type_train = {"highspeed": ['D', 'G', 'C'], 'normal': ['K', 'T', 'Z']}
        index = 1
        highspeed_index = 1
        for i in rj:
            info = i.split('|')
            num = info[3]
            start_station = info[6]
            end_station = info[7]
            start = info[8]
            end = info[9]
            time = info[10]
            softbed = info[23]
            nonseat = info[26]
            hardbed = info[28]
            hardseat = info[29]
            shangwu = info[32]
            first = info[31]
            second = info[30]
            if num[0] in type_train['highspeed'] and softbed == '':
                dit = {"序号": highspeed_index, "车次": num, "出发车站": t2c_data[start_station],
                       "到达车站": t2c_data[end_station], "出发时间": start, "到达时间": end, "历时": time,
                       "typelist": {"商务座": shangwu, "一等座": first, "二等座": second, "无座": nonseat}}
                train_inf['highspeed'].append(dit)
                highspeed_index += 1
            else:
                if num[0] in type_train['highspeed']:
                    dit = {"序号": index, "车次": num + "（高铁）", "出发车站": t2c_data[start_station],
                           "到达车站": t2c_data[end_station], "出发时间": start, "到达时间": end, "历时": time,
                           "typelist": {"软卧": softbed, "硬卧": hardbed, "硬座": second, "无座": nonseat}}
                    train_inf['hs_bed'].append(dit)
                else:
                    dit = {"序号": index, "车次": num, "出发车站": t2c_data[start_station],
                           "到达车站": t2c_data[end_station], "出发时间": start, "到达时间": end, "历时": time,
                           "typelist": {"软卧": softbed, "硬卧": hardbed, "硬座": hardseat, "无座": nonseat}}
                    train_inf['normal'].append(dit)
                index += 1
        return json.dumps(train_inf,ensure_ascii=False,indent=4)

    def search_train_price(self, train_num, seat_type):
        # 三种映射表
        # 因为12306用的key五花八门，所以需要不同的车型对应不同的map
        MAP_HIGH_SPEED = {
            "商务座": "swz_price",
            "一等座": "zy_price",
            "二等座": "ze_price",
            "无座": "ze_price",
        }

        MAP_NORMAL = {
            "软卧": "rw_price",
            "硬卧": "yw_price",
            "硬座": "yz_price",
            "无座":"yz_price",
        }

        MAP_SUFFIX_GT = {
            "软卧": "rw_price",
            "硬卧": "yw_price",
            "硬座": "ze_price",
            "无座": "ze_price",
        }

        # 是否带（高铁）
        suffix_gt = False
        if train_num.endswith("（高铁）"):
            suffix_gt = True
            train_num = train_num[:-4]

        for train in self.train_price_data:
            try:
                dto = train.get('queryLeftNewDTO', {})
                if dto.get('station_train_code') != train_num:
                    continue
                if dto.get('srrb_price',0)!=0:
                    # 某些车型的软卧被称为商务软包，用srrb_price
                    MAP_SUFFIX_GT['软卧']='srrb_price'
                # 判断用哪张映射表
                if suffix_gt:
                    seat_map = MAP_SUFFIX_GT
                elif dto.get("zy_price",0)!=0 and dto.get("ze_price",0)!=0 and dto.get("swz_price",0)==0:
                    seat_map = MAP_HIGH_SPEED
                elif dto.get("train_class_name") == "高速" or (dto.get("train_class_name") == "动车" and dto.get("swz_price",0)!=0):
                    seat_map = MAP_HIGH_SPEED
                else:
                    seat_map = MAP_NORMAL

                price_code = seat_map.get(seat_type)
                if not price_code:
                    return None
                # 注意！：这里得到的价格其实不是最终价格，实际上12306会有不定的折扣优惠，然而实在没时间找了
                price = int(dto.get(price_code, 0)) // 10
                return price

            except Exception as e:
                print(f"{train_num} 查询价格时出现问题: {e}")

    def transport_data(self) -> List[TransportOption]:
        """返回杭州的交通数据"""
        destination_city = self.destination_city
        departure_city = self.departure_city
        companions_count = self.companions_count
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

        #可选方案list
        options = []
        train_data = json.loads(self.get_train_inf())
        highspeed = train_data['highspeed']
        normal = train_data['normal']
        hs_bed = train_data['hs_bed']
        trains = [highspeed, normal, hs_bed]
        for idx,train_type in enumerate(trains):
            if idx==0:
                method = "高铁"
            elif idx==1:
                method = "火车"
            else:
                method = "高铁（过夜卧铺）"
            for train in train_type:
                for seat_type, leftTicket in train["typelist"].items():
                    # 拆分小时和分钟
                    if leftTicket != "有":
                        # 没票、为空的垃圾数据、票数少于出行人数的都跳过
                        if leftTicket=="无" or leftTicket=='' or int(leftTicket) < self.companions_count:
                            continue
                    duration = train['历时']
                    hours, minutes = map(int, duration.split(':'))
                    duration = round(hours + minutes / 60,2)
                    train_number = train['车次']
                    #获取车票价格
                    base_price = self.search_train_price(train_number, seat_type)
                    # base_price = 500

                    departure_time = train['出发时间']
                    arrival_time = train['到达时间']
                    departure_station = train['出发车站']
                    arrival_station = train['到达车站']
                    try:
                        # 高铁方案
                        options.append(TransportOption(
                            method=f"车型：{method} 座位类型：{seat_type} 剩余数量：{leftTicket}",
                            duration_hours=duration,
                            cost_per_person=base_price,
                            departure_time=departure_time,
                            arrival_time=arrival_time,
                            description=f"从{departure_city}到杭州的高铁，舒适便捷",
                            details={
                                "train_number": train_number,
                                "seat_type": seat_type,
                                "station": f"{departure_station}站 → {arrival_station}站",
                                "total_cost": base_price * companions_count,
                                # "booking_tip": "12306官网购票，支持改签"
                            }
                        ))
                    except Exception as e:
                        print(f"{train_number}发生问题：{e}")
        
        # 如果是较远的城市，添加飞机方案，目前只支持北京、广州、深圳
        if departure_city in ["北京", "广州", "深圳"]:
            with open("../../data/flight_data/flight_data.json", 'r', encoding='utf-8') as f:
                flight_json = json.load(f)[departure_city]
            for flight in flight_json:
                flight_duration = flight['duration']
                flight_price = flight['price']
                airline = flight['airline']
                flight_number = flight['flight_number']
                departure_time = flight['departure_time']

                options.append(TransportOption(
                    method="飞机",
                    duration_hours=flight_duration,
                    cost_per_person=flight_price,
                    departure_time="09:00",
                    arrival_time=self._calculate_arrival_time(departure_time, flight_duration),
                    description=f"从{departure_city}到杭州的航班，最快捷的选择",
                    details={
                        "flight_number": "CA1234",
                        "airline": airline,
                        "airport": f"{departure_city}机场 → 杭州萧山国际机场",
                        "total_cost": flight_price * companions_count,
                        # "booking_tip": "提前7-15天预订价格更优惠"
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
        
        # 旧方案：按性价比排序（时间*价格）考虑因素太少
        # options.sort(key=lambda x: x.duration_hours * x.cost_per_person)

        # 新方案：RAG排序，能够直接接受传递来的用户的一句话需求，返回
        result = asyncio.run(run_batch_queries(self.user_preference))
        return result
    
    def _calculate_arrival_time(self, departure_time: str, duration_hours: float) -> str:
        """计算到达时间"""
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
        _transport_tool = TransportTool(
            departure_city="广州",
            destination_city="杭州",
            date = "2025-11-26",     # 格式为XXXX-xx-xx
            user_preference="去杭州能坐火车吗？我想睡卧铺，推荐一下？"
        )
    return _transport_tool

if __name__ == "__main__":
    tool = get_transport_tool()
    print(tool.query_transport())
