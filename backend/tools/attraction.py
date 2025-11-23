import json
import os
import re
import shutil
from typing import List, Dict, Union
from loguru import logger
from dataclasses import dataclass, asdict

# 延迟导入langchain相关库（避免启动时的依赖冲突）
# from langchain_community.vectorstores import Chroma
# from langchain_core.documents import Document
# from langchain_community.embeddings import HuggingFaceEmbeddings



@dataclass
class Attraction:
    """景点数据模型"""
    id: str
    name: str
    city: str
    province: str
    category: str
    description: str
    address: str
    opening_hours: str
    ticket_price: str
    duration_hours: str
    rating: str
    best_season: str
    tips: str
    location: Dict = None
    tags: List[str] = None
    
    def to_searchable_text(self) -> str:
        """将对象转换为用于Embedding的长文本"""
        return f"景点：{self.name}。类型：{self.category}。城市：{self.city}。描述：{self.description}。标签：{' '.join(self.tags if self.tags else [])}。建议：{self.tips}"

class AttractionService:
    def __init__(self, json_path: str = None):
        logger.info("正在初始化 RAG 向量服务...")
        
        # 延迟导入，避免启动时的依赖冲突
        try:
            from langchain_community.vectorstores import Chroma
            from langchain_core.documents import Document
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            # 保存到实例变量
            self.Chroma = Chroma
            self.Document = Document
            self.HuggingFaceEmbeddings = HuggingFaceEmbeddings
        except ImportError as e:
            logger.error(f"无法导入langchain库: {e}")
            logger.warning("RAG功能将不可用，请安装: pip install langchain-community langchain-core chromadb sentence-transformers")
            self.Chroma = None
            return
        
        # 使用项目根目录的相对路径
        if json_path is None:
            # 从backend/tools出发，需要回到项目根目录
            # backend/tools -> backend -> project_root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.json_path = os.path.join(project_root, "data", "attractions", "zhejiang.json")
        else:
            self.json_path = json_path
        
        logger.info(f"数据文件路径: {self.json_path}")

        self.embedding_model = self.HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # 数据库路径放在backend目录下
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        self.db_path = os.path.join(backend_dir, "chroma_db_data")
        logger.info(f"向量数据库路径: {self.db_path}")
        
        self.vector_db = self.Chroma(
            collection_name="attractions_db",
            embedding_function=self.embedding_model,
            persist_directory=self.db_path
        )
        
        db_count = self.vector_db._collection.count()
        logger.info(f"当前数据库中有 {db_count} 条数据")

        if db_count == 0:
            logger.info(f"数据库为空，准备从 {self.json_path} 加载数据...")
            self._load_json_data(self.json_path)
        else:
            logger.info("使用现有数据库数据")

    def _parse_price(self, price_input) -> float:
        """辅助函数：处理非标准的门票价格格式"""
        if isinstance(price_input, (int, float)):
            return float(price_input)
        try:
            nums = re.findall(r'\d+\.?\d*', str(price_input))
            if nums:
                return float(nums[0])
            return 0.0
        except:
            return 0.0

    def _load_json_data(self, json_path: str):
        """读取 JSON 文件并存入向量库"""
        if not os.path.exists(json_path):
            logger.error(f"❌ 错误：找不到文件 {json_path}")
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                raw_list = json.load(f)
            
            documents = []
            logger.info(f"找到 {len(raw_list)} 条原始数据，正在处理...")

            for item in raw_list:
                cat_val = item.get("category", [])
                cat_str = ",".join(cat_val) if isinstance(cat_val, list) else str(cat_val)
                
                season_val = item.get("best_season", [])
                season_str = ",".join(season_val) if isinstance(season_val, list) else str(season_val)
                
                clean_price = self._parse_price(item.get("ticket_price", 0))

                att_obj = Attraction(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    city=item.get("city", ""),
                    province=item.get("province", ""),
                    category=cat_str,
                    description=item.get("description", ""),
                    address=item.get("location", {}).get("address", ""),
                    opening_hours=item.get("opening_hours", ""),
                    ticket_price=clean_price,
                    duration_hours=float(item.get("visit_duration", 1.0)),
                    rating=float(item.get("rating", 0.0)),
                    best_season=season_str,
                    tips=item.get("tips", ""),
                    location=item.get("location", {}),
                    tags=item.get("tags", [])
                )

                meta = asdict(att_obj)
                meta['location'] = json.dumps(meta['location'], ensure_ascii=False)
                meta['tags'] = ",".join(meta['tags']) if meta['tags'] else ""
                
                doc = self.Document(
                    page_content=att_obj.to_searchable_text(),
                    metadata=meta
                )
                documents.append(doc)

            if documents:
                self.vector_db.add_documents(documents)
                logger.success(f"✅ 成功写入 {len(documents)} 条数据到向量库！")
            
        except Exception as e:
            logger.error(f"数据加载失败详情: {e}")
            import traceback
            traceback.print_exc()

    def retrieve_attractions(
        self,
        city: str,
        preferences: List[str] = None,
        top_k: int = 5,
        budget_min: float = 0,
        budget_max: float = 10000
    ) -> List[Attraction]:
        """检索景点"""
        # 检查RAG是否可用
        if self.Chroma is None:
            logger.error("RAG功能未初始化，无法检索")
            return []
        
        try:
            query_text = f"{city} 旅游景点" 
            if preferences:
                query_text += f" 适合 {' '.join(preferences)} 风格"
            
            where_clause = {
                "$and": [
                    {"city": {"$eq": city}},
                    {"ticket_price": {"$gte": budget_min}},
                    {"ticket_price": {"$lte": budget_max}}
                ]
            }

            results = self.vector_db.similarity_search(
                query=query_text,
                k=top_k,
                filter=where_clause
            )
            
            attractions = []
            for doc in results:
                data = doc.metadata
                if isinstance(data.get('location'), str):
                    data['location'] = json.loads(data['location'])
                if isinstance(data.get('tags'), str):
                    data['tags'] = data['tags'].split(',') if data['tags'] else []
                
                attractions.append(Attraction(**data))
            
            return attractions

        except Exception as e:
            logger.error(f"RAG检索出错: {e}")
            return []

# 全局单例
_attraction_service = None

def get_attraction_service() -> AttractionService:
    global _attraction_service
    if _attraction_service is None:
        _attraction_service = AttractionService()
    return _attraction_service

if __name__ == "__main__":
    if os.path.exists("./chroma_db_data"):
        try:
            shutil.rmtree("./chroma_db_data")
            print("已自动删除旧数据库，准备重新加载...")
        except:
            pass

    service = get_attraction_service()
    
    print("\n--- 测试: 获取 10 个杭州景点 ---")
    res = service.retrieve_attractions(
        city="杭州", 
        preferences=["自然", "文化", "历史"], 
        top_k=10,
        budget_max=1000
    )
    
    print(f"实际检索到: {len(res)} 条")
    for i, a in enumerate(res, 1):
        print(f"{i}. [{a.name}] ({a.category}) - {a.ticket_price}元")