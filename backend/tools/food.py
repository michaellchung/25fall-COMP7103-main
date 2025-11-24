"""
美食查询工具 - 使用RAG方法实现
基于向量数据库查询杭州餐厅信息
"""
import json
import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class Restaurant:
    """餐厅数据模型"""
    id: str
    name: str
    city: str
    cuisine_type: str
    rating: float
    avg_price: float
    location: Dict
    signature_dishes: List[str]
    description: str
    opening_hours: str
    tags: List[str]
    phone: str = ""
    
    def to_searchable_text(self) -> str:
        """将对象转换为用于Embedding的长文本"""
        dishes_text = " ".join(self.signature_dishes) if self.signature_dishes else ""
        tags_text = " ".join(self.tags) if self.tags else ""
        return f"餐厅：{self.name}。菜系：{self.cuisine_type}。城市：{self.city}。招牌菜：{dishes_text}。描述：{self.description}。标签：{tags_text}"


class FoodTool:
    """美食查询工具 - RAG实现"""
    
    def __init__(self, json_path: str = None):
        logger.info("正在初始化美食查询 RAG 服务...")
        
        # 延迟导入langchain相关库
        try:
            from langchain_community.vectorstores import Chroma
            from langchain_core.documents import Document
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            self.Chroma = Chroma
            self.Document = Document
            self.HuggingFaceEmbeddings = HuggingFaceEmbeddings
        except ImportError as e:
            logger.error(f"无法导入langchain库: {e}")
            logger.warning("RAG功能将不可用，请安装: pip install langchain-community langchain-core chromadb sentence-transformers")
            self.Chroma = None
            return
        
        # 设置数据文件路径
        if json_path is None:
            # 从backend/tools出发，回到项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            restaurants_dir = os.path.join(project_root, "data", "restaurants")

            # 智能查找餐厅数据文件（优先使用100家餐厅数据）
            possible_files = [
                "hangzhou_restaurants_100.json",
                "hangzhou_restaurants.json"
            ]

            self.json_path = None
            for filename in possible_files:
                file_path = os.path.join(restaurants_dir, filename)
                if os.path.exists(file_path):
                    self.json_path = file_path
                    logger.info(f"✅ 找到餐厅数据文件: {filename}")
                    break

            if self.json_path is None:
                # 如果都找不到，使用默认路径（会在后面报错）
                self.json_path = os.path.join(restaurants_dir, "hangzhou_restaurants_100.json")
                logger.warning(f"⚠️ 未找到餐厅数据文件，将尝试使用: {self.json_path}")
        else:
            self.json_path = json_path

        logger.info(f"餐厅数据文件路径: {self.json_path}")

        # 存储原始餐厅数据（用于 get_all_restaurants 方法）
        self._raw_restaurants = []

        # 初始化Embedding模型（使用与attraction相同的模型）
        try:
            logger.info("正在加载 Embedding 模型...")
            self.embedding_model = self.HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            logger.success("✅ Embedding 模型加载成功")
        except Exception as e:
            logger.error(f"❌ Embedding 模型加载失败: {e}")
            logger.warning("可能是首次运行，正在下载模型（约90MB）...")
            logger.warning("如果下载失败，请检查网络连接或使用镜像：")
            logger.warning("export HF_ENDPOINT=https://hf-mirror.com")
            self.embedding_model = None
            return

        # 向量数据库路径
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        self.db_path = os.path.join(backend_dir, "chroma_db_restaurants")
        logger.info(f"向量数据库路径: {self.db_path}")

        # 初始化向量数据库（添加错误处理）
        try:
            self.vector_db = self.Chroma(
                collection_name="restaurants_db",
                embedding_function=self.embedding_model,
                persist_directory=self.db_path
            )
            logger.success("✅ 向量数据库初始化成功")
        except Exception as e:
            logger.error(f"❌ 向量数据库初始化失败: {e}")
            logger.warning("将使用降级方案（不使用RAG）")
            self.vector_db = None
            return

        # 检查数据库是否为空
        try:
            db_count = self.vector_db._collection.count()
            logger.info(f"当前数据库中有 {db_count} 条餐厅数据")

            if db_count == 0:
                logger.info(f"数据库为空，准备从 {self.json_path} 加载数据...")
                self._load_json_data(self.json_path)
            else:
                logger.info("使用现有数据库数据")
                # 即使数据库已存在，也需要加载原始数据供 get_all_restaurants 使用
                self._load_raw_data(self.json_path)
        except Exception as e:
            logger.error(f"❌ 检查数据库状态失败: {e}")
            logger.warning("将尝试加载数据...")

    def _load_raw_data(self, json_path: str):
        """只加载原始数据，不写入向量库"""
        if not os.path.exists(json_path):
            logger.warning(f"⚠️ 找不到数据文件 {json_path}")
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self._raw_restaurants = json.load(f)
            logger.info(f"✅ 已加载 {len(self._raw_restaurants)} 条原始餐厅数据")
        except Exception as e:
            logger.error(f"❌ 加载原始数据失败: {e}")
            self._raw_restaurants = []

    def _load_json_data(self, json_path: str):
        """读取JSON文件并存入向量库"""
        if not os.path.exists(json_path):
            logger.error(f"❌ 错误：找不到文件 {json_path}")
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                raw_list = json.load(f)

            # 保存原始数据
            self._raw_restaurants = raw_list

            documents = []
            logger.info(f"找到 {len(raw_list)} 条餐厅数据，正在处理...")

            for item in raw_list:
                # 处理数据
                restaurant = Restaurant(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    city=item.get("city", ""),
                    cuisine_type=item.get("cuisine_type", ""),
                    rating=float(item.get("rating", 0.0)),
                    avg_price=float(item.get("avg_price", 0)),
                    location=item.get("location", {}),
                    signature_dishes=item.get("signature_dishes", []),
                    description=item.get("description", ""),
                    opening_hours=item.get("opening_hours", ""),
                    tags=item.get("tags", []),
                    phone=item.get("phone", "")
                )

                # 准备metadata
                meta = asdict(restaurant)
                meta['location'] = json.dumps(meta['location'], ensure_ascii=False)
                meta['signature_dishes'] = json.dumps(meta['signature_dishes'], ensure_ascii=False)
                meta['tags'] = json.dumps(meta['tags'], ensure_ascii=False)

                # 创建Document
                doc = self.Document(
                    page_content=restaurant.to_searchable_text(),
                    metadata=meta
                )
                documents.append(doc)

            if documents:
                self.vector_db.add_documents(documents)
                logger.success(f"✅ 成功写入 {len(documents)} 条餐厅数据到向量库！")

        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            import traceback
            traceback.print_exc()

    def query_restaurants(
        self,
        city: str,
        category: str = None,
        preferences: List[str] = None,
        price_max: float = 1000,
        rating_min: float = 0.0,
        location_range: Dict = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        查询餐厅（符合README.md接口规范）

        Args:
            city: 城市名称
            category: 菜系类别
            preferences: 用户偏好（预留）
            price_max: 最高人均价格
            rating_min: 最低评分
            location_range: 位置范围（预留）
            top_k: 返回结果数量

        Returns:
            餐厅信息列表
        """
        # 检查RAG是否可用
        if self.Chroma is None:
            logger.error("❌ RAG功能未初始化（langchain库未安装）")
            return []

        if self.vector_db is None:
            logger.error("❌ 向量数据库未初始化")
            return []

        if self.embedding_model is None:
            logger.error("❌ Embedding模型未加载")
            return []

        try:
            # 构建查询文本
            query_text = f"{city} 餐厅"
            if category:
                query_text += f" {category}"
            if preferences:
                query_text += f" {' '.join(preferences)}"

            logger.info(f"查询文本: {query_text}")

            # 构建过滤条件
            where_clause = {
                "$and": [
                    {"city": {"$eq": city}},
                    {"avg_price": {"$lte": price_max}},
                    {"rating": {"$gte": rating_min}}
                ]
            }

            # 如果指定了菜系类别，添加过滤条件
            if category:
                where_clause["$and"].append(
                    {"cuisine_type": {"$eq": category}}
                )

            # 执行相似度搜索
            results = self.vector_db.similarity_search(
                query=query_text,
                k=top_k * 2,  # 多获取一些，然后再过滤
                filter=where_clause
            )

            # 处理结果
            restaurants = []
            for doc in results[:top_k]:
                data = doc.metadata

                # 解析JSON字段
                if isinstance(data.get('location'), str):
                    data['location'] = json.loads(data['location'])
                if isinstance(data.get('signature_dishes'), str):
                    data['signature_dishes'] = json.loads(data['signature_dishes'])
                if isinstance(data.get('tags'), str):
                    data['tags'] = json.loads(data['tags'])

                # 按照README.md接口规范返回数据
                restaurant_info = {
                    "name": data.get("name"),
                    "city": data.get("city"),
                    "cuisine_type": data.get("cuisine_type"),
                    "rating": data.get("rating"),
                    "avg_price": data.get("avg_price"),
                    "location": data.get("location"),
                    "signature_dishes": data.get("signature_dishes"),
                    "description": data.get("description"),
                    "opening_hours": data.get("opening_hours"),
                    "tags": data.get("tags")
                }

                restaurants.append(restaurant_info)

            logger.info(f"检索到 {len(restaurants)} 家餐厅")
            return restaurants

        except Exception as e:
            logger.error(f"RAG检索出错: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_all_restaurants(self) -> List[Dict]:
        """
        获取所有餐厅数据

        Returns:
            所有餐厅的列表
        """
        return self._raw_restaurants

    @property
    def restaurants_db(self) -> List[Dict]:
        """
        为了向后兼容，提供 restaurants_db 属性
        返回所有餐厅数据
        """
        return self._raw_restaurants


# 全局单例
_food_tool = None
_init_failed = False

def get_food_tool() -> FoodTool:
    """获取美食工具单例"""
    global _food_tool, _init_failed

    # 如果之前初始化失败，直接返回None
    if _init_failed:
        return None

    if _food_tool is None:
        try:
            _food_tool = FoodTool()
            # 检查是否初始化成功
            if _food_tool.vector_db is None or _food_tool.embedding_model is None:
                logger.error("❌ 美食查询工具初始化失败")
                _init_failed = True
                _food_tool = None
        except Exception as e:
            logger.error(f"❌ 创建美食查询工具失败: {e}")
            _init_failed = True
            _food_tool = None

    return _food_tool


# 为兼容性提供别名
def get_food_service() -> FoodTool:
    """获取美食服务（get_food_tool的别名）"""
    return get_food_tool()


if __name__ == "__main__":
    import shutil

    # 测试时删除旧数据库
    db_path = "./chroma_db_restaurants"
    if os.path.exists(db_path):
        try:
            shutil.rmtree(db_path)
            print("已删除旧数据库")
        except:
            pass

    # 创建工具实例
    tool = get_food_tool()

    # 测试1: 查询杭帮菜
    print("\n=== 测试1: 查询杭帮菜 ===")
    results = tool.query_restaurants(
        city="杭州",
        category="杭帮菜",
        price_max=200,
        rating_min=4.0,
        top_k=5
    )
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['name']} - {r['cuisine_type']} - ¥{r['avg_price']} - ⭐{r['rating']}")
        print(f"   招牌菜: {', '.join(r['signature_dishes'][:3])}")

    # 测试2: 查询小吃
    print("\n=== 测试2: 查询小吃 ===")
    results = tool.query_restaurants(
        city="杭州",
        category="小吃",
        price_max=50,
        top_k=5
    )
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['name']} - {r['cuisine_type']} - ¥{r['avg_price']}")

    # 测试3: 查询高评分餐厅
    print("\n=== 测试3: 查询高评分餐厅 ===")
    results = tool.query_restaurants(
        city="杭州",
        rating_min=4.5,
        price_max=150,
        top_k=5
    )
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['name']} - ⭐{r['rating']} - ¥{r['avg_price']}")
