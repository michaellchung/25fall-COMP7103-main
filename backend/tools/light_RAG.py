import os
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Any
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc, setup_logger

# 设置日志
setup_logger("lightrag", level="INFO")

# 设置并发数限制
LLM_SEMAPHORE = asyncio.Semaphore(2)

# 配置
API_KEY = "your api key"
BASE_URL = "your base url"
MODEL = "MODEL NAME"
WORKING_DIR = "../rag_storage_transport"

# 创建工作目录
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)


@dataclass
class TransportOption:
    """交通方式选项数据类"""
    method: str
    duration_hours: float
    cost_per_person: float
    departure_time: str
    arrival_time: str
    description: str
    details: Dict[str, Any]


async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    """LLM 模型函数"""
    async with LLM_SEMAPHORE:
        return await openai_complete_if_cache(
            MODEL,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=API_KEY,
            base_url=BASE_URL,
            **kwargs
        )


async def embedding_func(texts: list[str]):
    """嵌入函数"""
    async with LLM_SEMAPHORE:
        return await openai_embed(
            texts,
            # model="text-embedding-3-small",
            model="qwen/qwen3-embedding-4b",
            api_key=API_KEY,
            base_url=BASE_URL,
        )


def convert_transport_to_text(
        transport_options: List[TransportOption],
        origin_city: str,
        destination_city: str
) -> tuple[str, str]:
    """
    将交通方式列表转换为适合 LightRAG 的文本描述

    Args:
        transport_options: TransportOption 对象列表
        origin_city: 出发城市
        destination_city: 目的地城市

    Returns:
        tuple: (文本内容, 文档ID)
    """
    doc_parts = [f"# 从{origin_city}到{destination_city}的交通方式\n"]
    doc_parts.append(f"本文档包含从{origin_city}前往{destination_city}的所有可用交通方式信息。\n")

    # 按交通方式分组
    flights = []
    trains = []

    for option in transport_options:
        if '飞机' in option.method or 'flight' in option.method.lower():
            flights.append(option)
        elif '火车' in option.method or '高铁' in option.method or 'train' in option.method.lower():
            trains.append(option)

    # 统计信息
    total_options = len(transport_options)
    doc_parts.append(f"## 交通方式概览")
    doc_parts.append(f"- 出发城市: {origin_city}")
    doc_parts.append(f"- 到达城市: {destination_city}")
    doc_parts.append(f"- 可用交通方式总数: {total_options}个")
    doc_parts.append(f"- 航班数量: {len(flights)}班")
    doc_parts.append(f"- 火车/高铁数量: {len(trains)}班\n")

    if transport_options:
        min_cost = min(opt.cost_per_person for opt in transport_options)
        max_cost = max(opt.cost_per_person for opt in transport_options)
        min_duration = min(opt.duration_hours for opt in transport_options)
        max_duration = max(opt.duration_hours for opt in transport_options)

        doc_parts.append(f"- 价格区间: {min_cost}元 - {max_cost}元")
        doc_parts.append(f"- 时长区间: {format_duration(min_duration)} - {format_duration(max_duration)}\n")

    # 处理航班信息
    if flights:
        doc_parts.append(f"\n## 航班信息 (共{len(flights)}班)\n")
        doc_parts.append("航班是最快捷的交通方式，适合时间紧迫的旅客。\n")

        # 按价格排序
        flights_sorted = sorted(flights, key=lambda x: x.cost_per_person)

        for idx, flight in enumerate(flights_sorted, 1):
            doc_parts.append(f"### 航班选项 {idx}")
            doc_parts.append(f"- 交通方式: 飞机")

            # 提取航空公司和航班号
            airline = flight.details.get('airline', '未知航空')
            flight_number = flight.details.get('flight_number', '')
            airport = flight.details.get('airport', '')

            if airline:
                doc_parts.append(f"- 航空公司: {airline}")
            if flight_number:
                doc_parts.append(f"- 航班号: {flight_number}")
            if airport:
                doc_parts.append(f"- 机场信息: {airport}")

            doc_parts.append(f"- 起飞时间: {flight.departure_time}")
            doc_parts.append(f"- 到达时间: {flight.arrival_time}")
            doc_parts.append(f"- 飞行时长: {format_duration(flight.duration_hours)}")
            doc_parts.append(f"- 票价: {flight.cost_per_person}元/人")
            doc_parts.append(f"- 描述: {flight.description}\n")

    # 处理火车/高铁信息
    if trains:
        doc_parts.append(f"\n## 火车/高铁信息 (共{len(trains)}班)\n")
        doc_parts.append("火车和高铁价格实惠，运行稳定，适合预算有限或喜欢舒适旅行的旅客。\n")

        # 按价格排序
        trains_sorted = sorted(trains, key=lambda x: x.cost_per_person)

        for idx, train in enumerate(trains_sorted, 1):
            doc_parts.append(f"### 列车选项 {idx}")

            # 解析车型和座位类型
            method_info = train.method
            doc_parts.append(f"- 交通方式: {method_info}")

            # 提取列车号和座位信息
            train_number = train.details.get('train_number', '')
            seat_type = train.details.get('seat_type', '')
            station = train.details.get('station', '')

            if train_number:
                doc_parts.append(f"- 车次: {train_number}")
            if seat_type:
                doc_parts.append(f"- 座位类型: {seat_type}")
            if station:
                doc_parts.append(f"- 车站信息: {station}")

            doc_parts.append(f"- 发车时间: {train.departure_time}")
            doc_parts.append(f"- 到达时间: {train.arrival_time}")
            doc_parts.append(f"- 行程时长: {format_duration(train.duration_hours)}")
            doc_parts.append(f"- 票价: {train.cost_per_person}元/人")
            doc_parts.append(f"- 描述: {train.description}\n")

    # 添加对比分析
    doc_parts.append(f"\n## 交通方式对比分析\n")

    if flights and trains:
        cheapest_flight = min(flights, key=lambda x: x.cost_per_person)
        cheapest_train = min(trains, key=lambda x: x.cost_per_person)
        fastest_flight = min(flights, key=lambda x: x.duration_hours)
        fastest_train = min(trains, key=lambda x: x.duration_hours)

        doc_parts.append(f"### 价格对比")
        doc_parts.append(
            f"- 最便宜的航班: {cheapest_flight.cost_per_person}元 ({cheapest_flight.details.get('flight_number', '')})")
        doc_parts.append(
            f"- 最便宜的火车: {cheapest_train.cost_per_person}元 ({cheapest_train.details.get('train_number', '')})")

        doc_parts.append(f"\n### 时间对比")
        doc_parts.append(
            f"- 最快的航班: {format_duration(fastest_flight.duration_hours)} ({fastest_flight.details.get('flight_number', '')})")
        doc_parts.append(
            f"- 最快的火车: {format_duration(fastest_train.duration_hours)} ({fastest_train.details.get('train_number', '')})")

        # 性价比分析
        doc_parts.append(f"\n### 出行建议")

        if cheapest_train.cost_per_person < cheapest_flight.cost_per_person * 0.5:
            doc_parts.append(f"- 预算优先: 建议选择火车，价格仅为航班的一半左右")

        if fastest_flight.duration_hours < fastest_train.duration_hours * 0.3:
            doc_parts.append(f"- 时间优先: 建议选择飞机，可节省大量时间")

        # 计算性价比（时间/价格）
        flight_value = fastest_flight.duration_hours / cheapest_flight.cost_per_person
        train_value = fastest_train.duration_hours / cheapest_train.cost_per_person

        if flight_value < train_value:
            doc_parts.append(f"- 综合性价比: 飞机的时间价值比更高")
        else:
            doc_parts.append(f"- 综合性价比: 火车的性价比更高")

    # 关键信息总结
    doc_parts.append(f"\n## 关键信息总结")
    doc_parts.append(f"从{origin_city}到{destination_city}，您可以选择{len(flights)}个航班或{len(trains)}个火车班次。")

    if transport_options:
        cheapest = min(transport_options, key=lambda x: x.cost_per_person)
        fastest = min(transport_options, key=lambda x: x.duration_hours)

        cheapest_type = "航班" if cheapest in flights else "列车"
        fastest_type = "航班" if fastest in flights else "列车"

        doc_parts.append(f"最便宜的选择是{cheapest_type}，价格为{cheapest.cost_per_person}元。")
        doc_parts.append(f"最快的选择是{fastest_type}，只需{format_duration(fastest.duration_hours)}。")

    # 合并为完整文档
    full_text = "\n".join(doc_parts)
    doc_id = f"transport-{origin_city}-to-{destination_city}"

    return full_text, doc_id


def format_duration(hours: float) -> str:
    """将小时数转换为易读的时长格式"""
    h = int(hours)
    m = int((hours - h) * 60)

    if h > 0 and m > 0:
        return f"{h}小时{m}分钟"
    elif h > 0:
        return f"{h}小时"
    else:
        return f"{m}分钟"


async def initialize_rag():
    """初始化 LightRAG 实例"""
    from lightrag.kg.shared_storage import initialize_pipeline_status

    class SerializableTokenizer:
        def __init__(self, encoding_name="cl100k_base"):
            self.encoding_name = encoding_name
            self._encoding = None

        @property
        def encoding(self):
            if self._encoding is None:
                import tiktoken
                self._encoding = tiktoken.get_encoding(self.encoding_name)
            return self._encoding

        def encode(self, text):
            return self.encoding.encode(text)

        def decode(self, tokens):
            return self.encoding.decode(tokens)

        def __getstate__(self):
            return {'encoding_name': self.encoding_name}

        def __setstate__(self, state):
            self.encoding_name = state['encoding_name']
            self._encoding = None

    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=2560,
            func=embedding_func
        ),
        tokenizer=SerializableTokenizer(),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag

async def insert_transport_data(
        rag: LightRAG,
        transport_options: List[TransportOption],
        origin_city: str,
        destination_city: str = "杭州"
):
    """
    将交通方式数据插入 RAG 系统

    Args:
        rag: LightRAG 实例
        transport_options: TransportOption 对象列表
        origin_city: 出发城市
        destination_city: 目的地城市，默认为"杭州"
    """
    print(f"\n🚀 开始插入交通数据到 RAG 系统...")

    if not transport_options:
        print(f"⚠️  跳过 {origin_city}：无可用交通方式")
        return

    print(f"\n📝 处理 {origin_city} → {destination_city} 的交通数据...")
    print(f"   - 航班: {sum(1 for opt in transport_options if '飞机' in opt.method)}班")
    print(f"   - 火车: {sum(1 for opt in transport_options if '火车' in opt.method or '高铁' in opt.method)}班")

    # 转换为文本
    text, doc_id = convert_transport_to_text(transport_options, origin_city, destination_city)

    # 插入到 RAG
    await rag.ainsert(text, ids=[doc_id])
    print(f"   ✓ 已插入文档: {doc_id}")

    print("\n✅ 交通数据插入完成！")


async def add_options2RAG(options: List[TransportOption],departure_city, destination_city):
    # 示例数据：你的 TransportOption 列表（来自广州）
    try:
        # 初始化 RAG 系统
        print("🚀 正在初始化交通检索系统...")
        rag = await initialize_rag()

        # 分别插入不同城市的交通数据
        # await insert_transport_data(rag, guangzhou_options, "广州", "杭州")
        # await insert_transport_data(rag, beijing_options, "北京", "杭州")

        # 通用版本
        await insert_transport_data(rag, options, departure_city, destination_city)

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'rag' in locals():
            await rag.finalize_storages()
            print("\n🔒 已关闭存储连接")

async def run_batch_queries(queries):
    """
    批量或单条查询接口
    Args:
        rag: 已初始化或已加载的 LightRAG 实例
        queries: 一个字符串（单条查询）或一个字符串列表（多条查询）
    """
    rag = await initialize_rag()
    # 如果输入是单个字符串，转换为列表
    if isinstance(queries, str):
        queries = [queries]

    print("\n" + "=" * 60)
    print("🔍 开始批量查询")
    print("=" * 60)

    results = {}

    for query in queries:
        print(f"\n❓ 查询: {query}")
        print("-" * 60)

        try:
            result = await rag.aquery(
                query,
                param=QueryParam(mode="hybrid")
            )
            print(f"💡 回答: {result}")
            results[query] = result
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            results[query] = None

    print("\n✨ 批量查询完成！")
    return results