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
                
                <!-- 每日计划 -->
                <div class="daily-plans">
                  <h4>📅 每日安排</h4>
                  <div 
                    v-for="plan in message.itinerary.daily_plans" 
                    :key="plan.day"
                    class="day-plan"
                  >
                    <div class="day-title">第{{ plan.day }}天 (¥{{ plan.daily_cost }})</div>
                    <div class="timeline">
                      <div class="timeline-item">
                        <span class="time-badge">🌅 {{ plan.morning.time }}</span>
                        <span class="activity">{{ plan.morning.activity }}</span>
                        <span class="cost">¥{{ plan.morning.cost }}</span>
                      </div>
                      <div class="timeline-item">
                        <span class="time-badge">☀️ {{ plan.afternoon.time }}</span>
                        <span class="activity">{{ plan.afternoon.activity }}</span>
                        <span class="cost">¥{{ plan.afternoon.cost }}</span>
                      </div>
                      <div class="timeline-item">
                        <span class="time-badge">🌙 {{ plan.evening.time }}</span>
                        <span class="activity">{{ plan.evening.activity }}</span>
                        <span class="cost">¥{{ plan.evening.cost }}</span>
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
                    >
                      <span class="category">{{ category }}</span>
                      <div class="budget-bar">
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

const chatStore = useChatStore()

const inputMessage = ref('')
const messagesContainer = ref(null)

const messages = computed(() => chatStore.messages)
const requirements = computed(() => chatStore.currentRequirements)
const loading = computed(() => chatStore.loading)

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

function quickStart(text) {
  inputMessage.value = text
  handleSend()
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
              min-width: 80px;
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
              min-width: 80px;
              text-align: right;
              font-weight: 600;
              color: #303133;
              font-size: 14px;
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

