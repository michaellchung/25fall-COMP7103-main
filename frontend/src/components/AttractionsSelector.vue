<template>
  <div class="attractions-selector">
    <h4 class="selector-title">✨ 景点安排</h4>
    <p class="selector-prompt">{{ prompt }}</p>
    
    <!-- 预算进度条 -->
    <BudgetProgress 
      v-if="budgetTotal > 0"
      :total="budgetTotal"
      :used="budgetUsed"
      :transport="budgetTransport"
      :attractions="previewAttractionsCost"
      :food="budgetFood"
      :accommodation="budgetAccommodation"
      :show-breakdown="true"
    />
    
    <div class="daily-attractions">
      <div 
        v-for="(attractions, day) in dailyAttractions" 
        :key="day"
        class="day-section"
      >
        <div class="day-header">
          <span class="day-badge">第{{ day }}天</span>
          <span class="day-summary">{{ attractions.length }}个景点</span>
        </div>
        
        <div class="attractions-list">
          <div 
            v-for="(attraction, index) in attractions" 
            :key="attraction.id || index"
            class="attraction-card"
          >
            <div class="card-number">{{ index + 1 }}</div>
            <div class="card-content">
              <div class="attraction-header">
                <div class="attraction-name">{{ attraction.name }}</div>
                <el-tag v-if="attraction.category" type="info" size="small">
                  {{ attraction.category }}
                </el-tag>
              </div>

              <!-- 基本信息 -->
              <div class="attraction-info">
                <div class="info-item">
                  <el-icon><Ticket /></el-icon>
                  <span>门票：¥{{ attraction.ticket_price || 0 }}</span>
                </div>
                <div class="info-item">
                  <el-icon><Clock /></el-icon>
                  <span>时长：{{ attraction.visit_duration || attraction.duration_hours + '小时' }}</span>
                </div>
                <div class="info-item" v-if="attraction.rating">
                  <el-icon><Star /></el-icon>
                  <span>评分：{{ attraction.rating }}分</span>
                </div>
              </div>

              <!-- 详细信息 -->
              <div class="attraction-details">
                <div v-if="attraction.description" class="detail-row">
                  <span class="detail-label">📝 简介：</span>
                  <span class="detail-value">{{ attraction.description }}</span>
                </div>
                <div v-if="attraction.address" class="detail-row">
                  <span class="detail-label">📍 地址：</span>
                  <span class="detail-value">{{ attraction.address }}</span>
                </div>
                <div v-if="attraction.opening_hours" class="detail-row">
                  <span class="detail-label">🕐 开放时间：</span>
                  <span class="detail-value">{{ attraction.opening_hours }}</span>
                </div>
                <div v-if="attraction.best_season" class="detail-row">
                  <span class="detail-label">🌸 最佳季节：</span>
                  <span class="detail-value">{{ attraction.best_season }}</span>
                </div>
                <div v-if="attraction.tips" class="detail-row tip">
                  <span class="detail-label">💡 游玩提示：</span>
                  <span class="detail-value">{{ attraction.tips }}</span>
                </div>
                <div v-if="attraction.location" class="detail-row">
                  <span class="detail-label">🗺️ 坐标：</span>
                  <span class="detail-value">
                    {{ attraction.location.lat }}, {{ attraction.location.lng }}
                  </span>
                </div>
              </div>

              <!-- 推荐理由 -->
              <div class="attraction-reason" v-if="attraction.reason">
                <el-icon><InfoFilled /></el-icon>
                <span>{{ attraction.reason }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="selector-actions">
      <el-button type="primary" size="large" @click="confirmSelection">
        ✓ 确认安排
      </el-button>
      <el-button size="large" @click="requestModification">
        ✏️ 我想调整
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Ticket, Clock, Star, InfoFilled } from '@element-plus/icons-vue'
import { useChatStore } from '@/stores/chat'
import BudgetProgress from './BudgetProgress.vue'

const chatStore = useChatStore()

const props = defineProps({
  dailyAttractions: {
    type: Object,
    required: true
  },
  prompt: {
    type: String,
    default: '为您安排了以下景点行程，请确认或调整：'
  }
})

const emit = defineEmits(['confirm', 'modify'])

// 预算相关计算
const budgetTotal = computed(() => chatStore.budgetTracking.total)
const budgetTransport = computed(() => chatStore.budgetTracking.transport)
const budgetFood = computed(() => chatStore.budgetTracking.food)
const budgetAccommodation = computed(() => chatStore.budgetTracking.accommodation)

// 计算景点总费用
const previewAttractionsCost = computed(() => {
  let total = 0
  Object.values(props.dailyAttractions).forEach(attractions => {
    attractions.forEach(attraction => {
      total += attraction.ticket_price || 0
    })
  })
  return total
})

// 计算总使用
const budgetUsed = computed(() => {
  return budgetTransport.value + previewAttractionsCost.value + budgetFood.value + budgetAccommodation.value
})

const confirmSelection = () => {
  // 更新预算
  chatStore.updateBudget('attractions', previewAttractionsCost.value)
  
  emit('confirm', {
    type: 'attractions',
    choice: props.dailyAttractions,
    message: '确认景点安排'
  })
}

const requestModification = () => {
  emit('modify', {
    type: 'attractions',
    message: '我想调整景点安排'
  })
}
</script>

<style scoped lang="scss">
.attractions-selector {
  padding: 20px;
  background: #f9fafc;
  border-radius: 12px;
  margin: 15px 0;
  
  .selector-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 10px;
  }
  
  .selector-prompt {
    font-size: 14px;
    color: #606266;
    margin-bottom: 20px;
  }
  
  .daily-attractions {
    .day-section {
      margin-bottom: 25px;
      
      .day-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 15px;
        
        .day-badge {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 8px 20px;
          border-radius: 20px;
          font-weight: 600;
          font-size: 16px;
        }
        
        .day-summary {
          color: #909399;
          font-size: 14px;
        }
      }
      
      .attractions-list {
        display: grid;
        gap: 15px;
        
        .attraction-card {
          background: white;
          border: 2px solid #e4e7ed;
          border-radius: 12px;
          padding: 20px;
          display: flex;
          gap: 15px;
          transition: all 0.3s ease;
          
          &:hover {
            border-color: #409eff;
            box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
            transform: translateX(5px);
          }
          
          .card-number {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 18px;
            flex-shrink: 0;
          }
          
          .card-content {
            flex: 1;
            
            .attraction-header {
              display: flex;
              align-items: center;
              justify-content: space-between;
              margin-bottom: 12px;
              
              .attraction-name {
                font-size: 18px;
                font-weight: 600;
                color: #303133;
              }
            }
            
            .attraction-info {
              display: flex;
              gap: 20px;
              margin-bottom: 15px;
              flex-wrap: wrap;
              
              .info-item {
                display: flex;
                align-items: center;
                gap: 5px;
                font-size: 14px;
                color: #606266;
                
                .el-icon {
                  color: #409eff;
                }
              }
            }

            .attraction-details {
              background: #f5f7fa;
              border-radius: 8px;
              padding: 12px;
              margin-bottom: 12px;

              .detail-row {
                display: flex;
                margin-bottom: 8px;
                font-size: 13px;
                line-height: 1.6;

                &:last-child {
                  margin-bottom: 0;
                }

                .detail-label {
                  color: #909399;
                  min-width: 90px;
                  flex-shrink: 0;
                  font-weight: 500;
                }

                .detail-value {
                  color: #303133;
                  flex: 1;
                }

                &.tip {
                  background: rgba(64, 158, 255, 0.08);
                  padding: 8px;
                  border-radius: 6px;
                  border-left: 3px solid #409eff;
                  margin-top: 5px;

                  .detail-label {
                    color: #409eff;
                  }

                  .detail-value {
                    color: #409eff;
                  }
                }
              }
            }
            
            .attraction-reason {
              display: flex;
              align-items: center;
              gap: 8px;
              padding: 10px;
              background: rgba(103, 194, 58, 0.1);
              border-radius: 8px;
              color: #67c23a;
              font-size: 13px;
              border-left: 3px solid #67c23a;
            }
          }
        }
      }
    }
  }
  
  .selector-actions {
    display: flex;
    justify-content: center;
    gap: 15px;
    padding-top: 20px;
    border-top: 2px solid #e4e7ed;
    margin-top: 20px;
  }
}
</style>
