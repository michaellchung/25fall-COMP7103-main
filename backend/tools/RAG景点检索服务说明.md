# RAG景点检索服务使用说明

## 📋 概述

已成功将景点检索服务升级为基于RAG（Retrieval Augmented Generation）的向量检索系统，使用`zhejiang.json`数据集。

---

## ✅ 已完成的工作

### 1. 数据加载
- ✅ 数据文件：`/Applications/MyDocument/7103/data/attractions/zhejiang.json`
- ✅ 向量数据库：`/Applications/MyDocument/7103/backend/chroma_db_data/`
- ✅ 加载景点数：**17个杭州景点**

### 2. 向量化
- ✅ Embedding模型：`sentence-transformers/all-MiniLM-L6-v2`
- ✅ 向量数据库：ChromaDB
- ✅ 检索方式：语义相似度搜索

### 3. Agent集成
- ✅ 服务路径：`backend/tools/attraction.py`
- ✅ 单例模式：`get_attraction_service()`
- ✅ 已在`backend/agent/core.py`中集成

---

## 🔧 核心功能

### 检索接口

```python
def retrieve_attractions(
    city: str,                  # 城市名称
    preferences: List[str] = None,  # 偏好标签
    top_k: int = 5,              # 返回数量
    budget_min: float = 0,       # 最低预算
    budget_max: float = 10000   # 最高预算
) -> List[Attraction]:
    """
    使用语义搜索+过滤器检索景点
    """
```

### 数据模型

```python
@dataclass
class Attraction:
    id: str                   # 景点ID
    name: str                 # 景点名称
    city: str                 # 城市
    province: str             # 省份
    category: str             # 分类（可能是逗号分隔的字符串）
    description: str          # 描述
    address: str              # 地址
    opening_hours: str        # 开放时间
    ticket_price: float       # 门票价格
    duration_hours: float     # 建议游玩时长
    rating: float             # 评分
    best_season: str          # 最佳季节
    tips: str                 # 游玩提示
    location: Dict            # 位置信息 {lat, lng, address}
    tags: List[str]           # 标签列表
```

---

## 🚀 使用方法

### 1. 在Agent中使用

```python
from tools.attraction import get_attraction_service

# 获取服务实例
attraction_service = get_attraction_service()

# 检索景点
results = attraction_service.retrieve_attractions(
    city="杭州",
    preferences=["自然风光", "文化"],
    top_k=5,
    budget_max=100
)

# 处理结果
for attraction in results:
    print(f"{attraction.name} - ¥{attraction.ticket_price}")
```

### 2. 测试服务

```bash
cd /Applications/MyDocument/7103/backend
source venv/bin/activate
python test_rag_attraction.py
```

### 3. 独立测试

```bash
cd /Applications/MyDocument/7103/backend
source venv/bin/activate
python tools/attraction.py
```

---

## 📊 测试结果

### 测试1: 基本检索
- 输入：city="杭州", top_k=5
- 结果：成功返回5个景点

### 测试2: 偏好过滤
- 输入：preferences=["自然风光", "文化"]
- 结果：优先返回匹配偏好的景点

### 测试3: 预算过滤
- 输入：budget_max=0（免费景点）
- 结果：成功过滤出免费景点

### 测试4: Agent集成
- 场景：用户偏好"自然风光"，预算500元
- 结果：
  1. 十里琅珰 - ¥0（免费徒步）
  2. 千岛湖景区 - ¥45.5
  3. 西湖 - ¥0（免费）
  4. 西溪湿地 - ¥80
  5. 钱塘江夜游 - ¥0（免费）

---

## 🔍 检索机制

### 1. 语义检索
```python
query_text = f"{city} 旅游景点"
if preferences:
    query_text += f" 适合 {' '.join(preferences)} 风格"
```

- 将城市和偏好组合成查询文本
- 使用Embedding模型转换为向量
- 在向量数据库中进行相似度搜索

### 2. 过滤器
```python
where_clause = {
    "$and": [
        {"city": {"$eq": city}},
        {"ticket_price": {"$gte": budget_min}},
        {"ticket_price": {"$lte": budget_max}}
    ]
}
```

- 精确匹配城市
- 价格范围过滤
- 与语义检索结合使用

---

## 📂 文件结构

```
7103/
├── data/
│   └── attractions/
│       └── zhejiang.json          # 景点数据源（17个景点）
├── backend/
│   ├── tools/
│   │   └── attraction.py          # RAG服务实现
│   ├── agent/
│   │   └── core.py                # Agent核心（已集成）
│   ├── chroma_db_data/            # 向量数据库
│   └── test_rag_attraction.py     # 测试脚本
```

---

## 🎯 Agent集成状态

### 已集成位置

**文件**: `backend/agent/core.py`

```python
class AgentCore:
    def __init__(self):
        ...
        self.attraction_service = get_attraction_service()  # ✅ 已集成
        ...
    
    def _start_attractions_recommendation(self, state):
        # 获取景点数据
        attractions = self.attraction_service.retrieve_attractions(
            city=req.destination,
            preferences=req.preferences or [],
            top_k=20,
            budget_max=req.budget or 5000
        )
```

### 使用场景

1. **需求收集阶段**：用户指定目的地、偏好、预算
2. **景点推荐阶段**：调用RAG服务检索匹配景点
3. **行程生成阶段**：将景点分配到每天的行程中

---

## 🐛 常见问题

### 1. 数据库为空

**问题**: 首次运行时提示"数据库为空"

**解决**: 这是正常的，系统会自动加载数据。等待向量化完成（约10-20秒）。

### 2. 检索结果为空

**问题**: 检索返回空列表

**原因**:
- 城市名称不匹配（当前只有"杭州"）
- 预算过滤太严格
- 数据库未正确加载

**解决**:
```python
# 检查数据库
service = get_attraction_service()
print(f"数据库记录数: {service.vector_db._collection.count()}")
```

### 3. 导入错误

**问题**: `ModuleNotFoundError: No module named 'langchain_community'`

**解决**:
```bash
cd backend
source venv/bin/activate
pip install --upgrade langchain langchain-community chromadb sentence-transformers
```

---

## 📈 性能指标

- **向量化时间**: ~15秒（17个景点）
- **首次检索**: ~1-2秒（包括模型加载）
- **后续检索**: ~0.1-0.3秒
- **向量维度**: 384维（all-MiniLM-L6-v2）
- **数据库大小**: ~2MB

---

## 🔄 数据更新

### 方法1: 删除数据库重新加载

```bash
cd /Applications/MyDocument/7103/backend
rm -rf chroma_db_data
python tools/attraction.py
```

### 方法2: 程序化更新

```python
import shutil
from tools.attraction import AttractionService

# 删除旧数据库
if os.path.exists("./chroma_db_data"):
    shutil.rmtree("./chroma_db_data")

# 重新初始化（会自动加载数据）
service = AttractionService()
```

---

## ✅ 验证清单

- [x] 数据文件正确加载（zhejiang.json）
- [x] 向量数据库正常工作（17条记录）
- [x] 检索功能正常（返回结果）
- [x] 偏好过滤有效
- [x] 预算过滤有效
- [x] Agent集成完成
- [x] 测试脚本通过

---

## 📝 下一步扩展

### 1. 添加更多城市数据
- 当前：仅杭州（17个景点）
- 计划：南京、广州、苏州等

### 2. 优化检索算法
- 添加重排序（Reranking）
- 混合检索（BM25 + 向量检索）
- 多轮对话上下文

### 3. 增强数据
- 添加图片URL
- 添加用户评论
- 添加实时数据（天气、拥挤度）

---

**更新时间**: 2025-11-22  
**版本**: v1.0  
**状态**: ✅ 已集成并测试通过

