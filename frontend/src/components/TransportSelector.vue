<template>
  <div class="transport-selector">
    <h4 class="selector-title">🚗 交通方案选择</h4>
    <p class="selector-prompt">{{ prompt }}</p>
    
    <!-- 预算进度条 -->
    <BudgetProgress 
      v-if="budgetTotal > 0"
      :total="budgetTotal"
      :used="budgetUsed"
      :transport="previewTransportCost"
      :attractions="budgetAttractions"
      :food="budgetFood"
      :accommodation="budgetAccommodation"
      :show-breakdown="true"
    />
    
    <!-- 超支警告 -->
    <el-alert
      v-if="selectedOption && isOverBudget"
      type="error"
      :closable="false"
      show-icon
      class="budget-warning"
    >
      <template #title>
        ⚠️ 预算超支警告
      </template>
      <template #default>
        当前选择将超支 <strong>¥{{ overBudgetAmount }}</strong>，建议选择更经济的方案或调整总预算。
      </template>
    </el-alert>
    
    <div class="transport-options">
      <div 
        v-for="(option, index) in options" 
        :key="option.id || option.method"
        class="transport-card"
        :class="{ 
          'recommended': option.recommendation_score >= 0.9,
          'selected': selectedOption?.method === option.method 
        }"
        @click="selectTransport(option)"
      >
        <div class="card-number">{{ index + 1 }}</div>
        
        <div class="card-content">
          <div class="card-header">
            <div class="header-left">
              <span class="transport-icon">{{ getTransportIcon(option.method) }}</span>
              <span class="transport-method">{{ option.method }}</span>
              <el-tag 
                :type="getScoreTagType(option.recommendation_score)" 
                size="small"
              >
                推荐度 {{ (option.recommendation_score * 100).toFixed(0) }}%
              </el-tag>
            </div>
            <div class="header-right">
              <span class="cost-label">往返费用</span>
              <span class="cost-value">¥{{ option.total_cost }}</span>
            </div>
          </div>
          
          <div class="card-info">
            <div class="info-item">
              <el-icon><Clock /></el-icon>
              <span class="label">行程时长：</span>
              <span class="value">{{ option.duration_hours }}小时</span>
            </div>
            <div class="info-item">
              <el-icon><Position /></el-icon>
              <span class="label">建议出发：</span>
              <span class="value">{{ option.departure_time }}</span>
            </div>
            <div class="info-item">
              <el-icon><Location /></el-icon>
              <span class="label">预计到达：</span>
              <span class="value">{{ option.arrival_time }}</span>
            </div>
          </div>

          <div class="card-details">
            <div class="description" v-if="option.description">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ option.description }}</span>
            </div>
            
            <div v-if="option.details" class="details-grid">
              <div class="detail-item" v-if="option.details.train_type">
                <span class="detail-label">车次类型</span>
                <span class="detail-value">{{ option.details.train_type }}</span>
              </div>
              <div class="detail-item" v-if="option.details.seat_type">
                <span class="detail-label">座位类型</span>
                <span class="detail-value">{{ option.details.seat_type }}</span>
              </div>
              <div class="detail-item" v-if="option.details.station">
                <span class="detail-label">站点</span>
                <span class="detail-value">{{ option.details.station }}</span>
              </div>
              <div class="detail-item" v-if="option.details.airline">
                <span class="detail-label">航空公司</span>
                <span class="detail-value">{{ option.details.airline }}</span>
              </div>
              <div class="detail-item" v-if="option.details.airport">
                <span class="detail-label">机场</span>
                <span class="detail-value">{{ option.details.airport }}</span>
              </div>
              <div class="detail-item" v-if="option.details.distance_km">
                <span class="detail-label">距离</span>
                <span class="detail-value">{{ option.details.distance_km }}公里</span>
              </div>
              <div class="detail-item" v-if="option.details.fuel_cost">
                <span class="detail-label">油费</span>
                <span class="detail-value">¥{{ option.details.fuel_cost }}</span>
              </div>
              <div class="detail-item" v-if="option.details.toll_fee">
                <span class="detail-label">过路费</span>
                <span class="detail-value">¥{{ option.details.toll_fee }}</span>
              </div>
              <div class="detail-item full-width" v-if="option.details.booking_tip">
                <span class="detail-label">预订提示</span>
                <span class="detail-value">{{ option.details.booking_tip }}</span>
              </div>
              <div class="detail-item full-width" v-if="option.details.route_tip">
                <span class="detail-label">路线提示</span>
                <span class="detail-value">{{ option.details.route_tip }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="card-action">
          <el-button 
            v-if="selectedOption?.method === option.method"
            type="primary" 
            size="large"
            disabled
          >
            <el-icon><Select /></el-icon>
            已选择
          </el-button>
          <el-button 
            v-else
            type="default" 
            size="large"
          >
            选择此方案
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="selector-actions" v-if="selectedOption">
      <el-button type="primary" size="large" @click="confirmSelection">
        确认选择
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { InfoFilled, Clock, Position, Location, Select } from '@element-plus/icons-vue'
import { useChatStore } from '@/stores/chat'
import BudgetProgress from './BudgetProgress.vue'

const chatStore = useChatStore()

const props = defineProps({
  options: {
    type: Array,
    required: true
  },
  prompt: {
    type: String,
    default: '请选择您的交通方式：'
  }
})

const emit = defineEmits(['select'])

const selectedOption = ref(null)

// 预算相关计算
const budgetTotal = computed(() => chatStore.budgetTracking.total)
const budgetAttractions = computed(() => chatStore.budgetTracking.attractions)
const budgetFood = computed(() => chatStore.budgetTracking.food)
const budgetAccommodation = computed(() => chatStore.budgetTracking.accommodation)

// 预览交通费用（如果选中了选项，显示选中的，否则显示当前已记录的）
const previewTransportCost = computed(() => {
  if (selectedOption.value) {
    return selectedOption.value.total_cost || 0
  }
  return chatStore.budgetTracking.transport
})

// 计算总使用（包括预览）
const budgetUsed = computed(() => {
  return previewTransportCost.value + budgetAttractions.value + budgetFood.value + budgetAccommodation.value
})

// 检查是否超支
const isOverBudget = computed(() => {
  return budgetUsed.value > budgetTotal.value
})

// 超支金额
const overBudgetAmount = computed(() => {
  if (!isOverBudget.value) return 0
  return budgetUsed.value - budgetTotal.value
})

const getTransportIcon = (method) => {
  const icons = {
    '飞机': '✈️',
    '高铁': '🚄',
    '火车': '🚂',
    '自驾': '🚗',
    '汽车': '🚌'
  }
  return icons[method] || '🚗'
}

const getScoreTagType = (score) => {
  if (score >= 0.9) return 'success'
  if (score >= 0.7) return 'warning'
  return 'info'
}

const selectTransport = (option) => {
  selectedOption.value = option
}

const confirmSelection = () => {
  if (selectedOption.value) {
    // 更新预算
    chatStore.updateBudget('transport', selectedOption.value.total_cost)
    
    emit('select', {
      type: 'transport',
      choice: {
        method: selectedOption.value.method,
        cost_per_person: selectedOption.value.cost_per_person,
        total_cost: selectedOption.value.total_cost,
        duration_hours: selectedOption.value.duration_hours,
        departure_time: selectedOption.value.departure_time,
        arrival_time: selectedOption.value.arrival_time,
        description: selectedOption.value.description,
        details: selectedOption.value.details,
        outbound: {
          method: selectedOption.value.method,
          cost: selectedOption.value.cost_per_person,
          duration: selectedOption.value.duration_hours + '小时',
          reason: selectedOption.value.description
        },
        return: {
          method: selectedOption.value.method,
          cost: selectedOption.value.cost_per_person,
          duration: selectedOption.value.duration_hours + '小时',
          reason: selectedOption.value.description
        }
      },
      message: `我选择${selectedOption.value.method}`
    })
  }
}
</script>

<style scoped lang="scss">
.transport-selector {
  padding: 20px;
  background: #f9fafc;
  border-radius: 12px;
  margin: 15px -16px;
  
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
  
  .budget-warning {
    margin: 15px 0;
    :deep(.el-alert__title) {
      font-size: 16px;
      font-weight: 600;
    }
    :deep(.el-alert__description) {
      font-size: 14px;
      line-height: 1.6;
      strong {
        color: #f56c6c;
        font-size: 16px;
      }
    }
  }
  
  .transport-options {
    display: grid;
    gap: 15px;
    margin-bottom: 20px;
    
    .transport-card {
      background: white;
      border: 2px solid #e4e7ed;
      border-radius: 12px;
      padding: 20px;
      display: flex;
      gap: 15px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: #409eff;
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
        transform: translateX(5px);
      }
      
      &.recommended {
        border-color: #67c23a;
      }
      
      &.selected {
        border-color: #409eff;
        background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
      }
      
      .card-number {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 20px;
        flex-shrink: 0;
      }
      
      .card-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 12px;
        
        .card-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 10px;
          padding-bottom: 12px;
          border-bottom: 2px solid #f0f2f5;
          
          .header-left {
            display: flex;
            align-items: center;
            gap: 10px;
          }
          
          .header-right {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            
            .cost-label {
              font-size: 12px;
              color: #909399;
            }
            
            .cost-value {
              font-size: 24px;
              font-weight: 700;
              color: #f56c6c;
            }
          }
          
          .transport-icon {
            font-size: 32px;
          }
          
          .transport-method {
            font-size: 20px;
            font-weight: 600;
            color: #303133;
          }
        }
        
        .card-info {
          display: flex;
          gap: 20px;
          flex-wrap: wrap;
          
          .info-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 13px;
            color: #606266;
            
            .el-icon {
              color: #409eff;
            }
            
            .label {
              color: #909399;
            }
            
            .value {
              color: #303133;
              font-weight: 500;
            }
          }
        }
        
        .card-details {
          background: #f5f7fa;
          border-radius: 8px;
          padding: 12px;
          
          .description {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 12px;
            padding: 10px;
            background: rgba(103, 194, 58, 0.1);
            border-radius: 6px;
            color: #67c23a;
            font-size: 13px;
            line-height: 1.6;
            border-left: 3px solid #67c23a;
            
            .el-icon {
              flex-shrink: 0;
              margin-top: 2px;
            }
          }
          
          .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 8px;
            
            .detail-item {
              display: flex;
              flex-direction: column;
              gap: 4px;
              
              &.full-width {
                grid-column: 1 / -1;
                flex-direction: row;
                align-items: center;
                padding: 8px;
                background: rgba(64, 158, 255, 0.08);
                border-radius: 4px;
                
                .detail-label {
                  min-width: 80px;
                }
              }
              
              .detail-label {
                font-size: 11px;
                color: #909399;
                font-weight: 500;
              }
              
              .detail-value {
                font-size: 13px;
                color: #303133;
                font-weight: 600;
              }
            }
          }
        }
      }
      
      .card-action {
        display: flex;
        align-items: center;
        padding-left: 15px;
        border-left: 2px solid #f0f2f5;
        
        .el-button {
          min-width: 120px;
        }
      }
    }
  }
  
  .selector-actions {
    display: flex;
    justify-content: center;
    padding-top: 10px;
  }
}
</style>
