# 前端交互式推荐UI实现说明

## 📋 概述

为支持后端的分步交互式推荐流程，前端新增了4个选择器组件，并修改了ChatView和Store以支持用户在每个阶段的选择交互。

## 🎨 新增组件

### 1. TransportSelector.vue - 交通方案选择器

**位置**: `frontend/src/components/TransportSelector.vue`

**功能**:
- 展示3种交通方式（飞机、高铁、自驾）
- 显示往返费用、单程时长、推荐理由
- 支持单选，点击确认后发送选择

**Props**:
```javascript
{
  options: Array,      // 交通选项列表
  prompt: String       // 提示文字
}
```

**Events**:
```javascript
@select  // 用户确认选择时触发，传递选择数据
```

**UI特性**:
- 卡片式布局，响应式设计
- 推荐方案高亮显示（绿色边框）
- 已选方案蓝色背景
- Hover效果和动画

---

### 2. AttractionsSelector.vue - 景点安排选择器

**位置**: `frontend/src/components/AttractionsSelector.vue`

**功能**:
- 按天展示景点安排
- 显示每个景点的门票、游览时长、评分
- 显示推荐理由
- 支持确认或请求调整

**Props**:
```javascript
{
  dailyAttractions: Object,  // 按天分组的景点 {1: [...], 2: [...]}
  prompt: String             // 提示文字
}
```

**Events**:
```javascript
@confirm  // 用户确认安排时触发
@modify   // 用户要求调整时触发
```

**UI特性**:
- 每天独立展示，带彩色徽章
- 景点卡片带编号，清晰展示游览顺序
- 推荐理由用蓝色高亮框显示
- 两个操作按钮：确认/调整

---

### 3. FoodSelector.vue - 美食推荐选择器

**位置**: `frontend/src/components/FoodSelector.vue`

**功能**:
- 按天展示餐厅推荐
- 显示餐厅类型（早餐/午餐/晚餐）
- 显示菜系、人均价格、评分
- 显示推荐理由

**Props**:
```javascript
{
  dailyRestaurants: Object,  // 按天分组的餐厅 {1: [...], 2: [...]}
  prompt: String             // 提示文字
}
```

**Events**:
```javascript
@confirm  // 用户确认安排时触发
@modify   // 用户要求调整时触发
```

**UI特性**:
- 每天独立展示，粉红色渐变徽章
- 餐厅卡片带餐型图标（🥐🍱🍽️）
- 价格红色高亮显示
- 推荐理由用粉色高亮框显示

---

### 4. AccommodationSelector.vue - 住宿推荐选择器

**位置**: `frontend/src/components/AccommodationSelector.vue`

**功能**:
- 展示多个酒店选项
- 显示星级评分、位置、价格、设施
- 显示每晚价格和总价
- 支持单选

**Props**:
```javascript
{
  options: Array,      // 酒店选项列表
  prompt: String       // 提示文字
}
```

**Events**:
```javascript
@select  // 用户确认选择时触发
```

**UI特性**:
- 卡片网格布局（自适应）
- 推荐酒店黄色渐变背景
- 已选酒店蓝色背景
- 星级评分组件
- 设施标签展示

---

## 🔄 修改的文件

### 1. ChatView.vue

**修改内容**:

#### 1.1 导入新组件
```javascript
import TransportSelector from '@/components/TransportSelector.vue'
import AttractionsSelector from '@/components/AttractionsSelector.vue'
import FoodSelector from '@/components/FoodSelector.vue'
import AccommodationSelector from '@/components/AccommodationSelector.vue'
```

#### 1.2 在消息展示区域添加选择器
```vue
<template>
  <div class="message-content">
    <div class="message-text">{{ message.content }}</div>
    
    <!-- 推荐选择器 -->
    <TransportSelector 
      v-if="message.recommendation?.type === 'transport'"
      :options="message.recommendation.data.options"
      :prompt="message.recommendation.data.prompt"
      @select="handleSelection"
    />
    
    <AttractionsSelector 
      v-if="message.recommendation?.type === 'attractions'"
      :daily-attractions="message.recommendation.data.daily_attractions"
      :prompt="message.recommendation.data.prompt"
      @confirm="handleSelection"
      @modify="handleModification"
    />
    
    <FoodSelector 
      v-if="message.recommendation?.type === 'food'"
      :daily-restaurants="message.recommendation.data.daily_restaurants"
      :prompt="message.recommendation.data.prompt"
      @confirm="handleSelection"
      @modify="handleModification"
    />
    
    <AccommodationSelector 
      v-if="message.recommendation?.type === 'accommodation'"
      :options="message.recommendation.data.options"
      :prompt="message.recommendation.data.prompt"
      @select="handleSelection"
    />
    
    <!-- 行程详情展示 -->
    <div v-if="message.itinerary" class="itinerary-card">
      ...
    </div>
  </div>
</template>
```

#### 1.3 添加处理方法
```javascript
// 处理用户选择
async function handleSelection(selectionData) {
  try {
    await chatStore.sendMessage(selectionData.message, selectionData.choice)
    scrollToBottom()
  } catch (error) {
    ElMessage.error('发送选择失败，请重试')
  }
}

// 处理用户要求修改
async function handleModification(data) {
  try {
    await chatStore.sendMessage(data.message)
    scrollToBottom()
  } catch (error) {
    ElMessage.error('发送失败，请重试')
  }
}
```

---

### 2. chat.js (Pinia Store)

**修改内容**:

#### 2.1 sendMessage方法支持selection参数
```javascript
async function sendMessage(content, selection = null) {
  loading.value = true
  
  // 添加用户消息
  addMessage({
    role: 'user',
    content
  })

  try {
    const requestData = {
      session_id: sessionId.value,
      message: content
    }
    
    // 如果有selection数据，添加到请求中
    if (selection) {
      requestData.selection = selection
    }
    
    const response = await sendMessageAPI(requestData)

    // 添加Agent回复
    if (response.data) {
      addMessage({
        role: 'assistant',
        content: response.data.reply,
        itinerary: response.data.itinerary,       // 保存行程数据
        recommendation: response.data.recommendation // 保存推荐数据（新增）
      })

      // 更新状态...
    }

    return response
  } catch (error) {
    console.error('发送消息失败:', error)
    throw error
  } finally {
    loading.value = false
  }
}
```

---

## 📊 数据流

### 后端 → 前端

后端返回的推荐数据结构：

```javascript
{
  "reply": "为您推荐以下交通方式：",
  "stage": "waiting_transport_selection",
  "recommendation": {
    "type": "transport",  // 或 "attractions", "food", "accommodation"
    "data": {
      "prompt": "请选择您的交通方式：",
      "options": [
        {
          "method": "飞机",
          "cost": 800,
          "duration": "1.5小时",
          "reason": "最快捷，适合长距离",
          "recommended": true
        },
        // ... 更多选项
      ]
    }
  }
}
```

### 前端 → 后端

用户选择后发送的数据结构：

```javascript
{
  "session_id": "session_xxx",
  "message": "我选择飞机",
  "selection": {
    "type": "transport",
    "choice": {
      "method": "飞机",
      "cost": 800,
      "outbound": {...},
      "return": {...}
    }
  }
}
```

---

## 🎯 交互流程

### 完整的用户交互流程

```
1. 用户输入需求 → 后端收集信息
   ↓
2. 用户确认需求 → 后端开始推荐
   ↓
3. 【交通推荐】
   - 后端返回 recommendation.type = "transport"
   - 前端显示 TransportSelector
   - 用户选择 → 发送 selection
   ↓
4. 【景点推荐】
   - 后端返回 recommendation.type = "attractions"
   - 前端显示 AttractionsSelector
   - 用户确认/调整 → 发送 selection 或修改请求
   ↓
5. 【美食推荐】
   - 后端返回 recommendation.type = "food"
   - 前端显示 FoodSelector
   - 用户确认/调整 → 发送 selection 或修改请求
   ↓
6. 【住宿推荐】
   - 后端返回 recommendation.type = "accommodation"
   - 前端显示 AccommodationSelector
   - 用户选择 → 发送 selection
   ↓
7. 【生成最终攻略】
   - 后端返回 itinerary 数据
   - 前端显示完整行程卡片
   ↓
8. 完成 ✅
```

---

## 🎨 UI设计特点

### 1. 统一的设计语言
- 所有选择器使用相同的卡片风格
- 统一的边框、圆角、阴影效果
- 一致的hover和选中状态

### 2. 色彩系统
- **交通**: 蓝色系（#409eff）
- **景点**: 紫色系（#667eea → #764ba2）
- **美食**: 粉红色系（#f093fb → #f5576c）
- **住宿**: 黄色系（#fef9e7 → #fef5e7）

### 3. 响应式设计
- 桌面端：网格布局，多列展示
- 移动端：单列布局，自适应宽度
- 所有组件都支持触摸操作

### 4. 交互反馈
- Hover效果：边框变色 + 阴影 + 上移
- 选中状态：背景渐变 + 边框高亮
- 加载状态：按钮loading动画
- 错误提示：ElMessage组件

---

## 🔧 技术栈

- **Vue 3**: Composition API
- **Element Plus**: UI组件库
- **Pinia**: 状态管理
- **SCSS**: 样式预处理器
- **Axios**: HTTP请求

---

## 📝 使用示例

### 在其他页面中使用选择器

```vue
<template>
  <TransportSelector 
    :options="transportOptions"
    prompt="请选择交通方式"
    @select="handleTransportSelect"
  />
</template>

<script setup>
import TransportSelector from '@/components/TransportSelector.vue'

const transportOptions = [
  {
    method: '飞机',
    cost: 800,
    duration: '1.5小时',
    reason: '最快捷',
    recommended: true
  },
  // ...
]

function handleTransportSelect(data) {
  console.log('用户选择:', data)
  // 处理选择逻辑
}
</script>
```

---

## ✅ 测试清单

### 功能测试
- [ ] 交通选择器正常显示和选择
- [ ] 景点选择器按天展示，确认/调整按钮工作
- [ ] 美食选择器按天展示，确认/调整按钮工作
- [ ] 住宿选择器正常显示和选择
- [ ] 选择数据正确发送到后端
- [ ] 后端响应正确更新UI

### UI测试
- [ ] 桌面端布局正常
- [ ] 移动端布局正常
- [ ] Hover效果正常
- [ ] 选中状态正常
- [ ] 动画流畅

### 兼容性测试
- [ ] Chrome浏览器
- [ ] Safari浏览器
- [ ] Firefox浏览器
- [ ] 移动端浏览器

---

## 🚀 后续优化建议

### 1. 增强交互
- [ ] 添加景点地图展示
- [ ] 支持拖拽调整景点顺序
- [ ] 添加景点详情弹窗
- [ ] 支持多选餐厅（早中晚分别选）

### 2. 性能优化
- [ ] 图片懒加载
- [ ] 虚拟滚动（景点列表很长时）
- [ ] 组件按需加载

### 3. 用户体验
- [ ] 添加选择历史记录
- [ ] 支持收藏景点/餐厅
- [ ] 添加分享功能
- [ ] 支持导出PDF

### 4. 数据可视化
- [ ] 预算饼图
- [ ] 行程时间轴
- [ ] 景点热力图
- [ ] 路线地图

---

## 📚 相关文档

- **后端设计**: `分步交互式推荐设计方案.md`
- **后端实现**: `分步交互式推荐实现完成报告.md`
- **API文档**: `backend/api/chat.py`
- **组件源码**: `frontend/src/components/`

---

**更新时间**: 2025-11-18  
**版本**: v2.0  
**状态**: ✅ 已完成

