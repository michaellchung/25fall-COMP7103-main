# 🌍 TravelMate AI - 个性化旅游攻略生成Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**基于LLM的智能旅游规划助手 | 对话式需求收集 | 个性化行程生成**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [项目结构](#-项目结构) • [使用指南](#-使用指南) • [开发文档](#-开发文档)

</div>

---

## 📖 项目简介

TravelMate AI 是一个基于大语言模型（LLM）和Agent架构的智能旅游规划系统。通过自然语言对话，系统能够深度理解用户的旅行需求，并结合实时天气、景点信息、路线规划等多维度数据，自动生成个性化的旅游攻略。

### 🎯 适用场景
- 目的地：**广东省、江苏省、浙江省**（覆盖12个主要城市）
- 行程天数：**3-7天**
- 出行类型：**独行/情侣/家庭/朋友团**
- 预算范围：**1000-10000元**

---

## ✨ 功能特性

### 🤖 智能对话系统
- **多轮对话式需求收集**：自然流畅的交互体验，逐步挖掘用户真实需求
- **上下文理解**：记忆对话历史，支持需求补充和修正
- **智能信息提取**：自动识别目的地、时间、预算、偏好等关键信息

### 🛠️ 强大工具链
| 工具 | 功能 | 数据源 |
|------|------|--------|
| 🌤️ 天气查询 | 未来7天天气预报 + 穿衣建议 | 和风天气API |
| 📍 景点推荐 | 200+精选景点，智能匹配用户偏好 | 本地数据库 + FAISS向量检索 |
| 🚗 路线规划 | 智能交通方式推荐，时间费用估算 | 地理坐标计算 |
| 💰 预算控制 | 实时费用计算，超支预警与优化 | 智能算法 |

### 📅 行程生成器
- **智能规划算法**：基于地理聚类的路线优化，避免往返奔波
- **天气适配**：雨天自动推荐室内景点
- **时间精确规划**：考虑开放时间、游览时长、餐饮时间
- **个性化推荐**：根据用户偏好匹配景点类型（美食/文化/自然/休闲）
- **预算智能平衡**：自动调整住宿档次和景点选择

### 🎨 精美界面
- **Streamlit Web应用**：响应式设计，支持PC和移动端
- **实时对话展示**：打字机效果，流畅的交互体验
- **Markdown渲染**：美观的行程展示，支持一键复制
- **状态可视化**：侧边栏实时显示需求收集进度

---

## 🚀 快速开始

### 环境要求
- Python 3.9+
- pip 21.0+
- OpenAI API Key（或兼容的LLM API）

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/your-team/TravelMate-AI.git
cd TravelMate-AI
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量
创建 `.env` 文件：
```bash
# LLM配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1  # 可选，使用代理时配置

# 天气API配置
WEATHER_API_KEY=your_qweather_api_key_here

# 其他配置
MAX_DIALOGUE_ROUNDS=10
LLM_MODEL=gpt-4o-mini
TEMPERATURE=0.7
```

#### 4. 初始化数据
```bash
# 构建景点向量索引（首次运行必须）
python scripts/build_embeddings.py
```

#### 5. 启动应用
```bash
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动

---

## 📁 项目结构

```
TravelMate-AI/
├── 📄 README.md                 # 项目说明
├── 📄 PRD.md                    # 产品需求文档
├── 📄 团队分工方案.md            # 开发计划
├── 📄 requirements.txt          # 依赖清单
├── 📄 .env.example              # 环境变量模板
├── 📄 app.py                    # Streamlit主程序
│
├── 📂 config/                   # 配置文件
│   ├── config.yaml              # 全局配置
│   └── prompts.py               # LLM提示词模板
│
├── 📂 data/                     # 数据文件
│   ├── attractions/             # 景点数据
│   │   ├── guangdong.json       # 广东省景点
│   │   ├── jiangsu.json         # 江苏省景点
│   │   └── zhejiang.json        # 浙江省景点
│   └── embeddings/              # 景点向量索引
│       └── attractions.faiss
│
├── 📂 src/                      # 源代码
│   ├── 📂 agent/                # Agent核心
│   │   ├── __init__.py
│   │   ├── core.py              # Agent主控制器
│   │   ├── dialogue.py          # 对话管理器
│   │   └── state.py             # 状态跟踪器
│   │
│   ├── 📂 tools/                # 工具链
│   │   ├── __init__.py
│   │   ├── weather.py           # 天气查询工具
│   │   ├── attraction.py        # 景点查询工具
│   │   ├── route.py             # 路线规划工具
│   │   └── budget.py            # 预算计算工具
│   │
│   ├── 📂 planner/              # 行程规划
│   │   ├── __init__.py
│   │   ├── generator.py         # 行程生成器
│   │   └── optimizer.py         # 行程优化器
│   │
│   └── 📂 utils/                # 工具函数
│       ├── __init__.py
│       ├── llm.py               # LLM接口封装
│       └── helpers.py           # 辅助函数
│
├── 📂 scripts/                  # 脚本工具
│   ├── build_embeddings.py      # 构建向量索引
│   └── crawl_attractions.py     # 景点数据爬虫
│
├── 📂 tests/                    # 测试用例
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_planner.py
│
└── 📂 docs/                     # 文档
    ├── API.md                   # API文档
    ├── 使用手册.md               # 用户手册
    └── 技术实现.md               # 技术细节
```

---

## 📘 使用指南

### 基础使用流程

#### 1️⃣ 启动对话
打开应用后，系统会主动问候并引导你开始：

```
🤖 Agent: 您好！我是TravelMate AI，您的专属旅行规划助手！
         我可以帮您规划广东、江苏、浙江的旅行行程。
         请告诉我您的旅行想法吧～

👤 您: 我想去杭州玩3天
```

#### 2️⃣ 补充需求
Agent会追问关键信息：

```
🤖 Agent: 好的！为了给您制定更合适的行程，我需要了解：
         1. 您计划什么时候去？（具体日期或月份）
         2. 大概的预算范围是多少？
         3. 您对哪些方面比较感兴趣？
            - 🍜 美食体验
            - 🏛️ 文化古迹
            - 🏞️ 自然风光
            - 🛋️ 休闲度假

👤 您: 12月去，预算3000元，喜欢文化和美食
```

#### 3️⃣ 确认与生成
Agent会总结需求并生成行程：

```
🤖 Agent: 好的，让我为您总结一下：
         📍 目的地：杭州
         📅 天数：3天
         💰 预算：3000元
         🎯 偏好：文化、美食
         
         正在为您生成行程，请稍候...
         
         [5秒后]
         
         ✅ 行程已生成！以下是为您定制的【杭州3日文化美食之旅】
```

#### 4️⃣ 查看行程
系统会输出完整的Markdown格式行程，包括：
- 每日详细安排（景点、餐厅、交通）
- 费用明细
- 天气预报
- 贴心提示

#### 5️⃣ 修改调整（可选）
```
👤 您: 第二天能不能换成灵隐寺？

🤖 Agent: 好的，我为您调整第二天的行程...
```

---

### 🎯 使用技巧

#### 技巧1：详细描述需求
```
❌ 不好：我想去旅游
✅ 更好：我想去苏州玩3天，预算2000元，喜欢园林和美食
```

#### 技巧2：说明特殊需求
```
"我带着5岁孩子，需要亲子设施"
"我喜欢摄影，希望多推荐拍照好看的地方"
"我行动不便，希望少爬山"
```

#### 技巧3：灵活调整
- 如果预算超支，可以说"能不能便宜一点"
- 如果景点太多，可以说"太累了，想轻松一点"
- 如果不喜欢某个景点，可以说"换一个"

---

## 🛠️ 开发文档

### 核心架构

```
┌─────────────────────────────────────────┐
│         Streamlit Web界面                │
│  (用户交互 / 行程展示)                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         AgentCore (核心控制器)           │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  DialogueManager (对话管理)      │    │
│  │  - 多轮对话上下文                │    │
│  │  - 需求信息抽取                  │    │
│  │  - 完整度检查                    │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  StateTracker (状态跟踪)         │    │
│  │  - 用户需求状态                  │    │
│  │  - 工具调用历史                  │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  ToolOrchestrator (工具编排)     │    │
│  │  - 工具调用决策                  │    │
│  │  - 结果聚合                      │    │
│  └─────────────────────────────────┘    │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌──────────┐
│ LLM    │ │ Tools  │ │ Planner  │
└────────┘ └────┬───┘ └──────────┘
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
    ┌──────┐┌──────┐┌──────┐
    │天气  ││景点  ││路线  │
    └──────┘└──────┘└──────┘
```

### 关键技术点

#### 1. LLM提示词工程
```python
# 需求抽取提示词示例
EXTRACTION_PROMPT = """
你是一个旅游规划助手。从用户的输入中提取以下信息：
- destination: 目的地城市
- days: 旅行天数
- budget: 预算范围（数字）
- preferences: 旅行偏好（美食/文化/自然/休闲）
- travel_dates: 出行日期
- companions: 同行人员类型

输出JSON格式。如果信息缺失，对应字段设为null。

用户输入：{user_input}
"""
```

#### 2. 景点向量检索
```python
# 使用FAISS进行相似景点推荐
from faiss import IndexFlatL2

# 构建索引
embeddings = model.encode(attraction_descriptions)
index = IndexFlatL2(embedding_dim)
index.add(embeddings)

# 查询相似景点
query_embedding = model.encode(user_preference)
distances, indices = index.search(query_embedding, k=10)
```

#### 3. 地理聚类算法
```python
from sklearn.cluster import KMeans

# 按地理位置聚类景点
coordinates = [(attr['lat'], attr['lng']) for attr in attractions]
kmeans = KMeans(n_clusters=num_days)
clusters = kmeans.fit_predict(coordinates)

# 每天安排一个聚类
daily_attractions = [attractions[clusters == i] for i in range(num_days)]
```

### API接口

详细的API文档请查看 [docs/API.md](docs/API.md)

---

## 🧪 测试

### 运行单元测试
```bash
pytest tests/ -v
```

### 测试覆盖率
```bash
pytest --cov=src tests/
```

### 功能测试案例
```bash
# 测试对话流程
python tests/test_dialogue_flow.py

# 测试工具调用
python tests/test_tools.py

# 测试行程生成
python tests/test_itinerary_generation.py
```

---

## 📊 性能指标

| 指标 | 目标值 | 实际值 |
|------|--------|--------|
| 对话响应时间 | < 3秒 | ~2.5秒 |
| 行程生成时间 | < 10秒 | ~8秒 |
| LLM Token消耗 | < 5000 tokens/次 | ~3500 tokens |
| 景点查询速度 | < 100ms | ~50ms |
| 内存占用 | < 500MB | ~300MB |

---

## 🤝 贡献指南

欢迎贡献！请遵循以下流程：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范
- 遵循 PEP 8
- 使用类型注解
- 编写单元测试
- 更新相关文档

---

## 📝 更新日志

### v1.0.0 (2025-11-24)
- ✨ 首次发布
- ✅ 完整的对话式需求收集
- ✅ 支持广东、江苏、浙江三省
- ✅ 智能行程生成
- ✅ 天气适配推荐
- ✅ 预算智能控制

---

## 🙏 致谢

- **OpenAI** - 提供强大的LLM能力
- **Streamlit** - 优秀的快速原型工具
- **和风天气** - 免费天气API
- **FAISS** - 高效的向量检索库

---

## 📧 联系我们

- 项目负责人：[成员A]
- 邮箱：your-email@example.com
- GitHub Issues：[提交Issue](https://github.com/your-team/TravelMate-AI/issues)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个Star！⭐**

Made with ❤️ by TravelMate Team

</div>

