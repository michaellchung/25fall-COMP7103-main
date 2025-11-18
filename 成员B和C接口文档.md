# 成员B（RAG系统）和 成员C（行程规划器）接口文档

## 总览

本文档定义了 **成员B（RAG系统）** 和 **成员C（行程规划器）** 需要提供的接口，以及这些接口如何集成到成员A的Agent核心中。

目前所有接口均已基于**模拟数据**实现，可用于前后端联调和系统集成测试。

---

## 成员B：RAG 检索服务

### 位置
`/Applications/MyDocument/7103/backend/rag/retriever.py`

### 核心类
```python
class RAGRetriever:
    def retrieve_attractions(
        city: str,
        preferences: List[str] = None,
        top_k: int = 10,
        budget_min: float = 0,
        budget_max: float = 1000
    ) -> List[Attraction]
    
    def get_route_suggestions(
        city: str,
        days: int,
        preferences: List[str] = None
    ) -> Dict
```

### 数据模型

#### Attraction（景点数据模型）
```python
@dataclass
class Attraction:
    id: str                    # 景点ID
    name: str                  # 景点名称
    city: str                  # 城市
    province: str              # 省份
    category: str              # 类别（自然景观/历史文化/现代建筑/美食/购物等）
    description: str           # 描述
    address: str               # 地址
    opening_hours: str         # 开放时间
    ticket_price: float        # 门票价格
    duration_hours: float      # 建议游览时长（小时）
    rating: float              # 评分（1-5）
    best_season: str           # 最佳季节
    tips: str                  # 游览建议
```

### API 端点

#### 1. 获取景点信息

**请求**
```
GET /api/attractions/{city}?preferences=类别1,类别2&top_k=10
```

**参数**
| 参数 | 类型 | 描述 |
|-----|------|------|
| city | string | 城市名称（必需） |
| preferences | string | 偏好类别，逗号分隔，例如：`自然景观,历史文化` |
| top_k | int | 返回前k个结果，默认10 |

**响应示例**
```json
{
  "success": true,
  "data": {
    "city": "杭州",
    "attractions": [
      {
        "name": "西湖",
        "category": "自然景观",
        "description": "中国最美的湖泊...",
        "ticket_price": 0,
        "rating": 4.8,
        "duration_hours": 3,
        "opening_hours": "全天"
      },
      {
        "name": "灵隐寺",
        "category": "历史文化",
        "description": "中国最古老的佛刹...",
        "ticket_price": 30,
        "rating": 4.5,
        "duration_hours": 2,
        "opening_hours": "08:00-17:00"
      }
    ]
  },
  "error": null
}
```

#### 2. 获取路线建议

**方法**（Python内部调用）
```python
retriever = get_retriever()
route_suggestions = retriever.get_route_suggestions(
    city="杭州",
    days=3,
    preferences=["自然景观", "历史文化"]
)
```

**返回示例**
```python
{
    "city": "杭州",
    "days": 3,
    "recommended_attractions": [
        {
            "name": "西湖",
            "category": "自然景观",
            "rating": 4.8,
            "ticket_price": 0,
            "duration_hours": 3
        },
        # ... 更多景点
    ],
    "estimated_cost": 90  # 景点总门票成本
}
```

### 支持的城市和类别

#### 支持城市
- 🏯 **杭州** (浙江)
- 🏯 **南京** (江苏)  
- 🏯 **广州** (广东)

#### 支持类别
- `自然景观` - Natural Landscapes
- `历史文化` - Historical & Cultural
- `现代建筑` - Modern Architecture
- `美食` - Food & Cuisine
- `购物` - Shopping

### 模拟数据库结构

目前使用内存数据库（在 `ATTRACTIONS_DB` 中定义）：
```python
ATTRACTIONS_DB = {
    "杭州": [
        Attraction(...),  # 西湖
        Attraction(...),  # 灵隐寺
        Attraction(...),  # 茅家埠
    ],
    "南京": [...],
    "广州": [...]
}
```

### 迁移计划（成员B后续工作）

1. **数据源接入**: 
   - 爬取携程、马蜂窝景点数据
   - 调用高德地图API获取实时信息

2. **向量化处理**:
   - 使用 `text-embedding-3-small` 生成景点描述的向量
   - 使用 ChromaDB 存储向量

3. **检索优化**:
   - 实现语义检索（向量相似度）
   - 实现混合检索（关键词+语义）
   - 实现结果重排序

---

## 成员C：行程规划器

### 位置
`/Applications/MyDocument/7103/backend/planner/itinerary_generator.py`

### 核心类
```python
class ItineraryGenerator:
    def generate_itinerary(
        destination: str,
        days: int,
        budget: float,
        preferences: List[str],
        attractions: List[Dict],
        start_date: str = None
    ) -> Dict
```

### API 端点

#### 获取行程详情

**请求**
```
GET /api/itinerary/{session_id}
```

**参数**
| 参数 | 类型 | 描述 |
|-------|------|------|
| session_id | string | 会话ID（必需） |

**响应示例**
```json
{
  "success": true,
  "data": {
    "destination": "杭州",
    "duration_days": 3,
    "total_budget": 3000,
    "daily_budget": 1000,
    "daily_plans": [
      {
        "day": 1,
        "morning": {
          "activity": "游览西湖",
          "time": "08:00-12:00",
          "cost": 0
        },
        "afternoon": {
          "activity": "游览灵隐寺",
          "time": "14:00-17:00",
          "cost": 30
        },
        "evening": {
          "activity": "品尝当地美食或夜景游览",
          "time": "18:00-21:00",
          "cost": 80
        },
        "daily_cost": 110
      },
      # ... 更多天数
    ],
    "budget_breakdown": {
      "景点门票": 30,
      "餐饮": 900,
      "住宿": 1200,
      "交通": 600,
      "其他": 300
    },
    "estimated_cost": 3030,
    "tips": [
      "提前预订景点门票可以获得优惠",
      "推荐使用公共交通出行，环保且经济",
      "携带身份证和必要的证件",
      "了解当地天气，做好防晒或保暖",
      "不要错过当地特色美食，可咨询酒店前台推荐"
    ]
  },
  "error": null
}
```

### 行程生成逻辑

#### 1. 每日计划安排
- 将景点均衡分配到各天
- 为每天安排上午、下午、晚上三个时段
- 计算每天的成本

#### 2. 预算分配
按以下比例分配用户总预算：
- **景点门票**: 根据检索到的景点实际成本
- **餐饮**: 30% of total_budget
- **住宿**: 40% of total_budget
- **交通**: 20% of total_budget
- **其他**: 10% of total_budget

#### 3. 旅行建议
根据用户偏好生成个性化建议：
- 所有用户都会获得基础建议（提前预订、公共交通等）
- 美食爱好者：推荐当地特色美食咨询
- 自然景观爱好者：穿着舒适运动鞋的建议
- 历史文化爱好者：参加专业导游讲解的建议

### Python 内部调用

```python
from planner.itinerary_generator import get_itinerary_generator

generator = get_itinerary_generator()

itinerary = generator.generate_itinerary(
    destination="杭州",
    days=3,
    budget=3000,
    preferences=["自然景观", "历史文化"],
    attractions=[
        {
            "name": "西湖",
            "category": "自然景观",
            "ticket_price": 0,
            "duration_hours": 3
        },
        # ... 更多景点
    ],
    start_date="2025-12-01"
)
```

### 算法优化计划（成员C后续工作）

1. **路线优化**:
   - 使用旅行商问题(TSP)算法优化景点顺序
   - 最小化往返时间和交通成本

2. **智能分配**:
   - 基于用户评分偏好加权排序景点
   - 考虑景点开放时间和季节限制
   - 自动检测冲突和不可达情况

3. **多方案生成**:
   - 根据不同预算等级生成多个方案
   - 支持用户在方案间对比和调整

4. **实时天气集成**:
   - 调用和风天气API获取实时天气
   - 根据天气调整室内/室外活动安排

---

## 系统集成流程

### 对话流程中的接口调用

```
用户输入消息
    ↓
对话管理器提取需求
    ↓
用户确认需求
    ↓
✨ 触发行程生成 (当 stage == "generating")
    ↓
调用成员B接口（RAG检索）获取景点
    ↓
调用成员C接口（行程生成）生成行程
    ↓
返回完整行程给前端显示
```

### 代码集成点

**文件**: `/Applications/MyDocument/7103/backend/agent/core.py`

```python
def _generate_itinerary(self, state: ConversationState) -> Dict:
    # 步骤1：调用成员B的RAG检索
    attractions = self.rag_retriever.retrieve_attractions(
        city=req.destination,
        preferences=req.preferences or [],
        top_k=15,
        budget_max=req.budget or 1000
    )
    
    # 步骤2：调用成员C的行程生成
    itinerary = self.itinerary_generator.generate_itinerary(
        destination=req.destination,
        days=req.days or 3,
        budget=req.budget or 2000,
        preferences=req.preferences or [],
        attractions=attractions_dict,
        start_date=req.travel_dates
    )
    
    return itinerary
```

---

## 前后端数据流

### 前端调用对话API

```
POST /api/chat
{
    "session_id": "user_001",
    "message": "好的，就这样安排"
}
```

### 后端响应（包含行程）

```json
{
  "success": true,
  "data": {
    "reply": "✨ 已为您生成行程安排...",
    "stage": "generating",
    "itinerary": {
      "destination": "杭州",
      "duration_days": 3,
      "daily_plans": [...],
      ...
    },
    "requirements": {...}
  }
}
```

### 前端显示行程

- 在对话界面显示回复消息
- 同时以卡片/日程表形式展示`itinerary`数据
- 支持行程调整和修改

---

## 测试命令

### 测试景点检索（成员B）

```bash
curl "http://localhost:8000/api/attractions/杭州?preferences=自然景观,历史文化"
```

### 测试行程生成（成员C）

```bash
# 先通过对话API生成行程
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test_001","message":"我想去杭州玩3天，预算3000元"}'

# 然后获取完整行程
curl "http://localhost:8000/api/itinerary/test_001"
```

### 完整对话流程测试

```bash
# 见项目中的 backend/test_member_bc.py（待创建）
python backend/test_member_bc.py
```

---

## 协作规范

### 接口稳定性

- ✅ 核心接口已定义，成员B和C可基于现有接口开发
- ✅ 模拟数据已实现，前后端可进行联调
- ⚠️ 生产数据对接时，请保持接口签名不变

### 参数修改

如需修改接口参数或返回格式：
1. 与成员A沟通确认
2. 更新本文档
3. 更新测试用例

### 错误处理

所有接口应返回标准响应格式：
```json
{
  "success": false,
  "data": null,
  "error": "错误信息"
}
```

---

## 后续优化方向

### 成员B（RAG系统）

- [ ] 接入真实数据源（携程、马蜂窝）
- [ ] 实现ChromaDB向量存储
- [ ] 支持混合检索和重排序
- [ ] 添加缓存机制提升性能

### 成员C（行程规划器）

- [ ] 实现TSP路线优化算法
- [ ] 添加天气API集成
- [ ] 支持多方案生成
- [ ] 实现用户反馈机制

### 成员D（前端）

- [ ] 展示完整行程日程
- [ ] 支持行程修改交互
- [ ] 添加地图展示
- [ ] 实现分享和导出功能

---

**最后更新**: 2025-11-15  
**维护者**: 成员A

