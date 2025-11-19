<template>
  <div class="chat-view">
    <div class="chat-header">
      <h1>🌍 TravelMate AI</h1>
      <p>智能旅游规划助手</p>
    </div>
    
    <div class="chat-container">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div class="requirements-card">
          <h3>📋 当前需求</h3>
          <div class="requirement-item">
            <span class="label">📍 目的地:</span>
            <span class="value">{{ requirements.destination || '-' }}</span>
          </div>
          <div class="requirement-item" v-if="requirements.departure_city">
            <span class="label">🚄 出发地:</span>
            <span class="value">{{ requirements.departure_city }}</span>
          </div>
          <div class="requirement-item">
            <span class="label">📅 天数:</span>
            <span class="value">{{ requirements.days || '-' }}</span>
          </div>
          <div class="requirement-item">
            <span class="label">💰 预算:</span>
            <span class="value">{{ requirements.budget ? `${requirements.budget}元` : '-' }}</span>
          </div>
          <div class="requirement-item">
            <span class="label">🎯 偏好:</span>
            <span class="value">{{ requirements.preferences?.join('、') || '-' }}</span>
          </div>
          <div class="requirement-item" v-if="requirements.companions">
            <span class="label">👥 同行:</span>
            <span class="value">{{ requirements.companions }}</span>
          </div>
          <div class="requirement-item" v-if="requirements.companions_count">
            <span class="label">🔢 人数:</span>
            <span class="value">{{ requirements.companions_count }}人</span>
          </div>
        </div>
        
        <div class="quick-start">
          <h3>📌 快速开始</h3>
          <el-button text @click="quickStart('杭州3日游')">• 3天杭州游</el-button>
          <el-button text @click="quickStart('苏州5日游')">• 5天苏州游</el-button>
          <el-button text @click="quickStart('广州周末游')">• 周末广州游</el-button>
        </div>
      </aside>
      
      <!-- 对话区域 -->
      <main class="chat-main">
        <div class="messages-container" ref="messagesContainer">
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            :class="['message', message.role]"
          >
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
                <h3>📋 行程详情</h3>
                
                <!-- 基本信息 -->
                <div class="itinerary-header">
                  <div class="info-item">
                    <span class="label">📍 目的地:</span>
                    <span class="value">{{ message.itinerary.destination }}</span>
                  </div>
                  <div class="info-item" v-if="message.itinerary.departure_city">
                    <span class="label">🚄 出发地:</span>
                    <span class="value">{{ message.itinerary.departure_city }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">⏱️ 时长:</span>
                    <span class="value">{{ message.itinerary.duration_days }}天</span>
                  </div>
                  <div class="info-item">
                    <span class="label">💰 总预算:</span>
                    <span class="value">¥{{ message.itinerary.total_budget }}</span>
                  </div>
                  <div class="info-item" v-if="message.itinerary.companions">
                    <span class="label">👥 同行:</span>
                    <span class="value">{{ message.itinerary.companions }}</span>
                  </div>
                  <div class="info-item" v-if="message.itinerary.companions_count">
                    <span class="label">🔢 人数:</span>
                    <span class="value">{{ message.itinerary.companions_count }}人</span>
                  </div>
                </div>
                
                <!-- 交通方案 -->
                <div v-if="message.itinerary.transport && message.itinerary.transport.outbound" class="transport-section">
                  <h4>🚗 交通方案</h4>
                  <div class="transport-cards">
                    <!-- 去程 -->
                    <div class="transport-card outbound">
                      <div class="transport-header">
                        <span class="direction-badge">去程</span>
                        <span class="route">{{ message.itinerary.departure_city || '出发地' }} → {{ message.itinerary.destination }}</span>
                      </div>
                      <div class="transport-details">
                        <div class="detail-item">
                          <span class="icon">🚄</span>
                          <span class="method">{{ message.itinerary.transport.outbound?.method || '未知' }}</span>
                        </div>
                        <div class="detail-item">
                          <span class="icon">💰</span>
                          <span class="cost">¥{{ message.itinerary.transport.outbound?.cost || 0 }}</span>
                        </div>
                      </div>
                      <div class="transport-reason" v-if="message.itinerary.transport.outbound?.reason">
                        <span class="icon">💡</span>
                        <span>{{ message.itinerary.transport.outbound.reason }}</span>
                      </div>
                    </div>
                    
                    <!-- 返程 -->
                    <div class="transport-card return" v-if="message.itinerary.transport.return">
                      <div class="transport-header">
                        <span class="direction-badge return-badge">返程</span>
                        <span class="route">{{ message.itinerary.destination }} → {{ message.itinerary.departure_city || '出发地' }}</span>
                      </div>
                      <div class="transport-details">
                        <div class="detail-item">
                          <span class="icon">🚄</span>
                          <span class="method">{{ message.itinerary.transport.return?.method || '未知' }}</span>
                        </div>
                        <div class="detail-item">
                          <span class="icon">💰</span>
                          <span class="cost">¥{{ message.itinerary.transport.return?.cost || 0 }}</span>
                        </div>
                      </div>
                      <div class="transport-reason" v-if="message.itinerary.transport.return?.reason">
                        <span class="icon">💡</span>
                        <span>{{ message.itinerary.transport.return.reason }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 住宿信息 -->
                <div v-if="message.itinerary.hotel && message.itinerary.hotel.name" class="hotel-section">
                  <h4>🏨 住宿安排</h4>
                  <div class="hotel-card">
                    <div class="hotel-name">{{ message.itinerary.hotel.name }}</div>
                    <div class="hotel-details">
                      <span class="detail-item">
                        <span class="icon">⭐</span>
                        <span>{{ message.itinerary.hotel.star_rating || '舒适酒店' }}</span>
                      </span>
                      <span class="detail-item">
                        <span class="icon">🛏️</span>
                        <span>{{ message.itinerary.hotel.nights || 0 }}晚</span>
                      </span>
                      <span class="detail-item">
                        <span class="icon">💰</span>
                        <span>¥{{ message.itinerary.hotel.total_cost || 0 }}</span>
                      </span>
                    </div>
                    <div class="hotel-reason" v-if="message.itinerary.hotel.reason">
                      <span class="icon">💡</span>
                      <span>{{ message.itinerary.hotel.reason }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- 每日计划 -->
                <div class="daily-plans">
                  <h4>📅 每日安排</h4>
                  <div 
                    v-for="plan in message.itinerary.daily_plans" 
                    :key="plan.day"
                    class="day-plan"
                  >
                    <div class="day-title">
                      第{{ plan.day }}天: {{ plan.theme || '精彩行程' }}
                      <span class="date-badge" v-if="plan.date">{{ plan.date }}</span>
                      <span class="cost-badge">¥{{ plan.daily_cost }}</span>
                    </div>
                    <div class="timeline">
                      <div 
                        v-for="(item, index) in plan.schedule" 
                        :key="index"
                        class="timeline-item"
                      >
                        <span class="time-badge">{{ getTimeIcon(item.type) }} {{ item.time }}</span>
                        <span class="activity">
                          <span class="activity-type">{{ item.type }}</span>
                          <span class="activity-name">{{ item.name }}</span>
                          <span class="activity-reason" v-if="item.reason">{{ item.reason }}</span>
                        </span>
                        <span class="cost">¥{{ item.cost }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 预算分配 -->
                <div class="budget-breakdown">
                  <h4>💰 预算分配</h4>
                  <div class="budget-items">
                    <div 
                      v-for="(amount, category) in message.itinerary.budget_breakdown" 
                      :key="category"
                      class="budget-item"
                      :class="{ 'total-item': category === 'total' }"
                    >
                      <span class="category">{{ getBudgetCategoryName(category) }}</span>
                      <div class="budget-bar" v-if="category !== 'total'">
                        <div 
                          class="budget-fill" 
                          :style="{ width: (amount / message.itinerary.total_budget * 100) + '%' }"
                        ></div>
                      </div>
                      <span class="amount">¥{{ amount }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- 旅行建议 -->
                <div class="tips">
                  <h4>💡 旅行建议</h4>
                  <ul>
                    <li v-for="(tip, idx) in message.itinerary.tips" :key="idx">{{ tip }}</li>
                  </ul>
                </div>
              </div>
              
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
          
          <div v-if="loading" class="message assistant">
            <div class="message-content">
              <div class="message-text">
                <el-icon class="is-loading"><Loading /></el-icon>
                正在思考...
              </div>
            </div>
          </div>
        </div>
        
        <div class="input-area">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="2"
            placeholder="请输入您的需求..."
            @keydown.enter.exact.prevent="handleSend"
          />
          <div class="input-actions">
            <el-button @click="handleReset" :disabled="loading">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
            <el-button type="primary" @click="handleSend" :loading="loading">
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'
import { Loading, Refresh, Promotion } from '@element-plus/icons-vue'
import TransportSelector from '@/components/TransportSelector.vue'
import AttractionsSelector from '@/components/AttractionsSelector.vue'
import FoodSelector from '@/components/FoodSelector.vue'
import AccommodationSelector from '@/components/AccommodationSelector.vue'

const chatStore = useChatStore()

const inputMessage = ref('')
const messagesContainer = ref(null)

const messages = computed(() => chatStore.messages)
const requirements = computed(() => chatStore.currentRequirements)
const loading = computed(() => chatStore.loading)

// 预算类别中英文映射
const budgetCategoryMap = {
  'transport': '交通',
  'attractions': '景点门票',
  'food': '餐饮',
  'accommodation': '住宿',
  'misc': '其他',
  'total': '总计'
}

// 转换预算类别为中文
const getBudgetCategoryName = (category) => {
  return budgetCategoryMap[category] || category
}

onMounted(() => {
  // 添加欢迎消息
  if (!chatStore.hasMessages) {
    chatStore.addMessage({
      role: 'assistant',
      content: '您好！我是TravelMate AI，您的专属旅行规划助手！🎉\n\n我可以帮您规划广东、江苏、浙江三省的旅行行程。\n\n请告诉我您的旅行想法吧～您可以提供：\n📍 目的地 | 🚄 出发地 | 📅 天数 | 💰 预算 | 🎯 偏好 | 👥 同行人员 | 🔢 人数\n\n💡 示例：\n"我想从上海出发去杭州玩3天，我们两个人，预算3000元，喜欢文化和美食"'
    })
  }
})

async function handleSend() {
  if (!inputMessage.value.trim()) {
    ElMessage.warning('请输入消息')
    return
  }
  
  try {
    await chatStore.sendMessage(inputMessage.value)
    inputMessage.value = ''
    scrollToBottom()
  } catch (error) {
    ElMessage.error('发送失败，请重试')
  }
}

async function handleReset() {
  try {
    await chatStore.reset()
    ElMessage.success('对话已重置')
  } catch (error) {
    ElMessage.error('重置失败')
  }
}

function getTimeIcon(type) {
  const icons = {
    '景点': '🏛️',
    '午餐': '🍜',
    '晚餐': '🍽️',
    '早餐': '🥐',
    '交通': '🚗',
    '酒店': '🏨',
    '休息': '☕'
  }
  return icons[type] || '📍'
}

function quickStart(text) {
  inputMessage.value = text
  handleSend()
}

// 处理用户选择
async function handleSelection(selectionData) {
  console.log('🎯 [ChatView] handleSelection被调用')
  console.log('📦 [ChatView] selectionData:', selectionData)
  console.log('💬 [ChatView] message:', selectionData.message)
  console.log('🎁 [ChatView] choice:', selectionData.choice)
  
  try {
    console.log('📤 [ChatView] 调用chatStore.sendMessage')
    await chatStore.sendMessage(selectionData.message, selectionData.choice)
    console.log('✅ [ChatView] sendMessage完成')
    scrollToBottom()
  } catch (error) {
    console.error('❌ [ChatView] 发送选择失败:', error)
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

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}
</script>

<style scoped lang="scss">
.chat-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  text-align: center;
  
  h1 {
    font-size: 28px;
    margin: 0;
  }
  
  p {
    margin: 5px 0 0;
    opacity: 0.9;
  }
}

.chat-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e4e7ed;
  padding: 20px;
  overflow-y: auto;
  
  h3 {
    font-size: 16px;
    margin-bottom: 15px;
  }
  
  .requirements-card {
    margin-bottom: 30px;
    
    .requirement-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;
      
      .label {
        color: #909399;
        font-size: 14px;
      }
      
      .value {
        color: #303133;
        font-weight: 500;
      }
    }
  }
  
  .quick-start {
    .el-button {
      display: block;
      width: 100%;
      text-align: left;
      margin-bottom: 8px;
    }
  }
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.messages-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.message {
  margin-bottom: 20px;
  display: flex;
  
  &.user {
    justify-content: flex-end;
    
    .message-content {
      background: #409eff;
      color: white;
    }
  }
  
  &.assistant {
    justify-content: flex-start;
    
    .message-content {
      background: #f0f0f0;
      color: #303133;
      max-width: 85%;
    }
  }
  
  .message-content {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 8px;
    
    .message-text {
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.6;
    }
    
    .message-time {
      font-size: 12px;
      opacity: 0.7;
      margin-top: 5px;
    }
    
    // 行程卡片样式
    .itinerary-card {
      margin-top: 15px;
      padding: 20px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      
      h3 {
        margin: 0 0 15px 0;
        font-size: 18px;
        color: #303133;
      }
      
      h4 {
        margin: 15px 0 10px 0;
        font-size: 16px;
        color: #606266;
      }
      
      .itinerary-header {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin-bottom: 20px;
        padding: 15px;
        background: #f5f7fa;
        border-radius: 8px;
        
        .info-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          
          .label {
            color: #909399;
            font-size: 14px;
          }
          
          .value {
            color: #303133;
            font-weight: 600;
            font-size: 15px;
          }
        }
      }
      
      .transport-section {
        margin: 20px 0;
        
        .transport-cards {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 15px;
          
          @media (max-width: 768px) {
            grid-template-columns: 1fr;
          }
          
          .transport-card {
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            
            &.return {
              background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }
            
            .transport-header {
              display: flex;
              align-items: center;
              gap: 10px;
              margin-bottom: 12px;
              
              .direction-badge {
                padding: 4px 12px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                
                &.return-badge {
                  background: rgba(255, 255, 255, 0.3);
                }
              }
              
              .route {
                font-size: 14px;
                font-weight: 600;
              }
            }
            
            .transport-details {
              display: flex;
              gap: 20px;
              margin-bottom: 10px;
              
              .detail-item {
                display: flex;
                align-items: center;
                gap: 6px;
                
                .icon {
                  font-size: 16px;
                }
                
                .method {
                  font-size: 16px;
                  font-weight: 600;
                }
                
                .cost {
                  font-size: 16px;
                  font-weight: 600;
                }
              }
            }
            
            .transport-reason {
              display: flex;
              align-items: center;
              gap: 6px;
              font-size: 12px;
              opacity: 0.9;
              padding: 8px;
              background: rgba(255, 255, 255, 0.2);
              border-radius: 6px;
              
              .icon {
                font-size: 14px;
              }
            }
          }
        }
      }
      
      .hotel-section {
        margin: 20px 0;
        
        .hotel-card {
          padding: 15px;
          background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          
          .hotel-name {
            font-size: 18px;
            font-weight: 600;
            color: #8b4513;
            margin-bottom: 10px;
          }
          
          .hotel-details {
            display: flex;
            gap: 20px;
            margin-bottom: 10px;
            
            .detail-item {
              display: flex;
              align-items: center;
              gap: 6px;
              color: #8b4513;
              font-size: 14px;
              
              .icon {
                font-size: 16px;
              }
            }
          }
          
          .hotel-reason {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: #8b4513;
            padding: 8px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 6px;
            
            .icon {
              font-size: 14px;
            }
          }
        }
      }
      
      .daily-plans {
        margin: 20px 0;
        
        .day-plan {
          margin-bottom: 15px;
          padding: 15px;
          background: #f9fafc;
          border-radius: 8px;
          border-left: 4px solid #409eff;
          
          .day-title {
            font-weight: 600;
            color: #409eff;
            margin-bottom: 10px;
            font-size: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
            
            .date-badge {
              font-size: 12px;
              color: #909399;
              background: #f0f2f5;
              padding: 2px 8px;
              border-radius: 4px;
            }
            
            .cost-badge {
              margin-left: auto;
              font-size: 14px;
              color: #f56c6c;
              font-weight: 600;
            }
          }
          
          .timeline {
            .timeline-item {
              display: flex;
              align-items: center;
              padding: 8px 0;
              border-bottom: 1px dashed #e4e7ed;
              
              &:last-child {
                border-bottom: none;
              }
              
              .time-badge {
                min-width: 150px;
                font-size: 13px;
                color: #909399;
              }
              
              .activity {
                flex: 1;
                color: #303133;
                font-size: 14px;
                display: flex;
                flex-direction: column;
                gap: 4px;
                
                .activity-type {
                  display: inline-block;
                  padding: 2px 8px;
                  background: #ecf5ff;
                  color: #409eff;
                  border-radius: 4px;
                  font-size: 12px;
                  margin-right: 8px;
                }
                
                .activity-name {
                  font-weight: 600;
                  color: #303133;
                }
                
                .activity-reason {
                  font-size: 12px;
                  color: #909399;
                  font-style: italic;
                }
              }
              
              .cost {
                color: #f56c6c;
                font-weight: 600;
                font-size: 14px;
              }
            }
          }
        }
      }
      
      .budget-breakdown {
        margin: 20px 0;
        
        .budget-items {
          .budget-item {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            
            .category {
              min-width: 100px;
              font-size: 14px;
              color: #606266;
            }
            
            .budget-bar {
              flex: 1;
              height: 20px;
              background: #e4e7ed;
              border-radius: 10px;
              overflow: hidden;
              margin: 0 10px;
              
              .budget-fill {
                height: 100%;
                background: linear-gradient(90deg, #67c23a 0%, #409eff 100%);
                transition: width 0.3s ease;
              }
            }
            
            .amount {
              min-width: 100px;
              text-align: right;
              font-weight: 600;
              color: #303133;
              font-size: 14px;
            }
            
            &.total-item {
              margin-top: 15px;
              padding-top: 15px;
              border-top: 2px solid #dcdfe6;
              
              .category {
                font-size: 16px;
                font-weight: 600;
                color: #303133;
              }
              
              .amount {
                font-size: 18px;
                color: #f56c6c;
              }
            }
          }
        }
      }
      
      .tips {
        margin: 20px 0 0 0;
        padding: 15px;
        background: #fff9e6;
        border-radius: 8px;
        border-left: 4px solid #e6a23c;
        
        ul {
          margin: 10px 0 0 0;
          padding-left: 20px;
          
          li {
            color: #606266;
            line-height: 1.8;
            font-size: 14px;
            margin-bottom: 5px;
          }
        }
      }
    }
  }
}

.input-area {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  
  .input-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 10px;
  }
}
</style>

