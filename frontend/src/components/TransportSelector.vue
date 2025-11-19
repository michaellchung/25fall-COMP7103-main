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
    
    <div class="transport-options">
      <div 
        v-for="option in options" 
        :key="option.id || option.method"
        class="transport-card"
        :class="{ 
          'recommended': option.recommendation_score >= 0.9,
          'selected': selectedOption?.method === option.method 
        }"
        @click="selectTransport(option)"
      >
        <div class="card-header">
          <span class="transport-icon">{{ getTransportIcon(option.method) }}</span>
          <span class="transport-method">{{ option.method }}</span>
          <el-tag 
            :type="getScoreTagType(option.recommendation_score)" 
            size="small"
          >
            推荐度 {{ (option.recommendation_score * 100).toFixed(0) }}%
          </el-tag>
        </div>
        
        <div class="card-body">
          <!-- 费用信息 -->
          <div class="info-section">
            <div class="section-title">💰 费用信息</div>
            <div class="info-row">
              <span class="label">单人费用：</span>
              <span class="value">¥{{ option.cost_per_person }}</span>
            </div>
            <div class="info-row">
              <span class="label">总费用：</span>
              <span class="value cost">¥{{ option.total_cost }}</span>
            </div>
          </div>

          <!-- 时间信息 -->
          <div class="info-section">
            <div class="section-title">⏱️ 时间信息</div>
            <div class="info-row">
              <span class="label">行程时长：</span>
              <span class="value">{{ option.duration_hours }}小时</span>
            </div>
            <div class="info-row">
              <span class="label">建议出发：</span>
              <span class="value">{{ option.departure_time }}</span>
            </div>
            <div class="info-row">
              <span class="label">预计到达：</span>
              <span class="value">{{ option.arrival_time }}</span>
            </div>
          </div>

          <!-- 详细信息 -->
          <div v-if="option.details" class="info-section">
            <div class="section-title">📋 详细信息</div>
            <div v-if="option.details.train_type" class="info-row">
              <span class="label">车次类型：</span>
              <span class="value">{{ option.details.train_type }}</span>
            </div>
            <div v-if="option.details.seat_type" class="info-row">
              <span class="label">座位类型：</span>
              <span class="value">{{ option.details.seat_type }}</span>
            </div>
            <div v-if="option.details.station" class="info-row">
              <span class="label">站点：</span>
              <span class="value">{{ option.details.station }}</span>
            </div>
            <div v-if="option.details.airline" class="info-row">
              <span class="label">航空公司：</span>
              <span class="value">{{ option.details.airline }}</span>
            </div>
            <div v-if="option.details.airport" class="info-row">
              <span class="label">机场：</span>
              <span class="value">{{ option.details.airport }}</span>
            </div>
            <div v-if="option.details.distance_km" class="info-row">
              <span class="label">距离：</span>
              <span class="value">{{ option.details.distance_km }}公里</span>
            </div>
            <div v-if="option.details.fuel_cost" class="info-row">
              <span class="label">油费：</span>
              <span class="value">¥{{ option.details.fuel_cost }}</span>
            </div>
            <div v-if="option.details.toll_fee" class="info-row">
              <span class="label">过路费：</span>
              <span class="value">¥{{ option.details.toll_fee }}</span>
            </div>
            <div v-if="option.details.booking_tip" class="info-row tip">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ option.details.booking_tip }}</span>
            </div>
            <div v-if="option.details.route_tip" class="info-row tip">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ option.details.route_tip }}</span>
            </div>
          </div>

          <!-- 推荐理由 -->
          <div class="info-section reason-section">
            <div class="section-title">📝 推荐理由</div>
            <div class="reason-text">{{ option.description }}</div>
          </div>
        </div>
        
        <div class="card-footer">
          <el-button 
            v-if="selectedOption?.method === option.method"
            type="primary" 
            size="small"
            disabled
          >
            ✓ 已选择
          </el-button>
          <el-button 
            v-else
            type="default" 
            size="small"
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
import { InfoFilled } from '@element-plus/icons-vue'
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
  
  .transport-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
    
    .transport-card {
      background: white;
      border: 2px solid #e4e7ed;
      border-radius: 12px;
      padding: 20px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: #409eff;
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
        transform: translateY(-2px);
      }
      
      &.recommended {
        border-color: #67c23a;
        background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
      }
      
      &.selected {
        border-color: #409eff;
        background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
      }
      
      .card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f0f2f5;
        
        .transport-icon {
          font-size: 32px;
        }
        
        .transport-method {
          font-size: 22px;
          font-weight: 600;
          color: #303133;
          flex: 1;
        }
      }
      
      .card-body {
        margin-bottom: 15px;
        
        .info-section {
          margin-bottom: 15px;
          
          .section-title {
            font-size: 14px;
            font-weight: 600;
            color: #606266;
            margin-bottom: 10px;
            padding-left: 8px;
            border-left: 3px solid #409eff;
          }
          
          .info-row {
            display: flex;
            align-items: flex-start;
            margin-bottom: 6px;
            font-size: 13px;
            padding-left: 11px;
            
            .label {
              color: #909399;
              min-width: 85px;
              flex-shrink: 0;
            }
            
            .value {
              color: #303133;
              font-weight: 500;
              flex: 1;
              
              &.cost {
                color: #f56c6c;
                font-size: 18px;
                font-weight: 700;
              }
            }
            
            &.tip {
              margin-top: 5px;
              padding: 8px 10px;
              background: rgba(64, 158, 255, 0.08);
              border-radius: 6px;
              color: #409eff;
              font-size: 12px;
              gap: 6px;
              border-left: 3px solid #409eff;
            }
          }
          
          &.reason-section {
            .reason-text {
              padding: 12px;
              background: rgba(103, 194, 58, 0.08);
              border-radius: 8px;
              color: #67c23a;
              font-size: 13px;
              line-height: 1.6;
              border-left: 3px solid #67c23a;
            }
          }
        }
      }
      
      .card-footer {
        display: flex;
        justify-content: center;
        padding-top: 10px;
        border-top: 1px solid #f0f2f5;
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
