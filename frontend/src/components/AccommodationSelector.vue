<template>
  <div class="accommodation-selector">
    <h4 class="selector-title">🏨 住宿推荐</h4>
    <p class="selector-prompt">{{ prompt }}</p>
    
    <!-- 预算进度条 -->
    <BudgetProgress 
      v-if="budgetTotal > 0"
      :total="budgetTotal"
      :used="budgetUsed"
      :transport="budgetTransport"
      :attractions="budgetAttractions"
      :food="budgetFood"
      :accommodation="previewAccommodationCost"
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
        当前住宿选择将超支 <strong>¥{{ overBudgetAmount }}</strong>，建议选择更经济的酒店或调整总预算。
      </template>
    </el-alert>
    
    <div class="hotels-list">
      <div 
        v-for="(option, index) in options" 
        :key="option.id"
        class="hotel-card"
        :class="{ 
          'premium': option.hotel_type === '高档型',
          'selected': selectedOption?.id === option.id 
        }"
        @click="selectHotel(option)"
      >
        <div class="card-number">{{ index + 1 }}</div>
        
        <div class="card-content">
          <div class="card-header">
            <div class="header-left">
              <div class="hotel-name">{{ option.name }}</div>
              <div class="hotel-badges">
                <el-tag 
                  :type="getHotelTypeTag(option.hotel_type)" 
                  size="small"
                >
                  {{ option.hotel_type }}
                </el-tag>
                <el-rate 
                  :model-value="option.star_rating || option.rating" 
                  disabled 
                  show-score 
                  text-color="#ff9900"
                  score-template="{value}分"
                  size="small"
                />
              </div>
            </div>
            <div class="header-right">
              <span class="cost-label">总费用</span>
              <span class="cost-value">¥{{ option.total_cost || (option.price_per_night * option.nights) }}</span>
              <span class="nights-info">{{ option.nights }}晚 × ¥{{ option.price_per_night }}/晚</span>
            </div>
          </div>

          <div class="card-info">
            <div class="info-item" v-if="option.room_type">
              <el-icon><House /></el-icon>
              <span class="label">房型：</span>
              <span class="value">{{ option.room_type }}</span>
            </div>
            <div class="info-item" v-if="option.distance_to_center !== undefined">
              <el-icon><Location /></el-icon>
              <span class="label">距中心：</span>
              <span class="value">{{ option.distance_to_center.toFixed(2) }}km</span>
            </div>
            <div class="info-item" v-if="option.phone">
              <el-icon><Phone /></el-icon>
              <span class="label">电话：</span>
              <span class="value">{{ option.phone }}</span>
            </div>
          </div>

          <div class="card-details">
            <!-- 设施信息 -->
            <div class="facilities-section" v-if="option.facilities && option.facilities.length">
              <span class="section-label">设施：</span>
              <div class="facilities-tags">
                <el-tag 
                  v-for="facility in option.facilities" 
                  :key="facility"
                  type="success"
                  size="small"
                  effect="plain"
                >
                  {{ getFacilityIcon(facility) }} {{ facility }}
                </el-tag>
              </div>
            </div>

            <!-- 标签信息 -->
            <div class="tags-section" v-if="option.tags && option.tags.length">
              <span class="section-label">标签：</span>
              <div class="tags-list">
                <el-tag 
                  v-for="tag in option.tags" 
                  :key="tag"
                  type="info"
                  size="small"
                  effect="plain"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </div>

            <!-- 详细信息 -->
            <div class="info-details">
              <div v-if="option.description" class="detail-item">
                <span class="detail-label">简介：</span>
                <span class="detail-value">{{ option.description }}</span>
              </div>
              <div v-if="option.location && option.location.address" class="detail-item">
                <span class="detail-label">地址：</span>
                <span class="detail-value">{{ option.location.address }}</span>
              </div>
              <div v-if="option.location && option.location.lat" class="detail-item">
                <span class="detail-label">坐标：</span>
                <span class="detail-value">{{ option.location.lat }}, {{ option.location.lng }}</span>
              </div>
            </div>

            <!-- 推荐理由 -->
            <div class="reason-box" v-if="option.reason">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ option.reason }}</span>
            </div>
          </div>
        </div>

        <div class="card-action">
          <el-button 
            v-if="selectedOption?.id === option.id"
            type="primary" 
            size="large"
            disabled
            style="width: 100%;"
          >
            <el-icon><Select /></el-icon>
            已选择
          </el-button>
          <el-button 
            v-else
            type="default" 
            size="large"
            style="width: 100%;"
          >
            选择此酒店
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
import { useChatStore } from '@/stores/chat'
import BudgetProgress from './BudgetProgress.vue'
import { InfoFilled, House, Location, Phone, Select } from '@element-plus/icons-vue'

const chatStore = useChatStore()

const props = defineProps({
  options: {
    type: Array,
    required: true
  },
  prompt: {
    type: String,
    default: '请选择您的住宿：'
  }
})

const emit = defineEmits(['select'])

const selectedOption = ref(null)

// 预算相关计算
const budgetTotal = computed(() => chatStore.budgetTracking.total)
const budgetTransport = computed(() => chatStore.budgetTracking.transport)
const budgetAttractions = computed(() => chatStore.budgetTracking.attractions)
const budgetFood = computed(() => chatStore.budgetTracking.food)

// 预览住宿费用
const previewAccommodationCost = computed(() => {
  if (selectedOption.value) {
    return selectedOption.value.total_cost || (selectedOption.value.price_per_night * selectedOption.value.nights)
  }
  return chatStore.budgetTracking.accommodation
})

// 计算总使用
const budgetUsed = computed(() => {
  return budgetTransport.value + budgetAttractions.value + budgetFood.value + previewAccommodationCost.value
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

const getHotelTypeTag = (type) => {
  const typeMap = {
    '经济型': 'info',
    '舒适型': 'warning',
    '高档型': 'danger'
  }
  return typeMap[type] || 'info'
}

const getFacilityIcon = (facility) => {
  const iconMap = {
    'WiFi': '📶',
    '早餐': '🍳',
    '停车场': '🅿️',
    '健身房': '💪',
    '游泳池': '🏊',
    '餐厅': '🍽️',
    '会议室': '👔',
    '洗衣服务': '👕',
    '24小时前台': '🔔',
    '空调': '❄️'
  }
  return iconMap[facility] || '✓'
}

const selectHotel = (option) => {
  selectedOption.value = option
}

const confirmSelection = () => {
  if (!selectedOption.value) {
    console.warn('⚠️ 未选择酒店')
    return
  }
  
  const totalCost = selectedOption.value.total_cost || (selectedOption.value.price_per_night * selectedOption.value.nights)
  
  // 更新预算
  chatStore.updateBudget('accommodation', totalCost)
  
  console.log('🏨 发送住宿选择:', selectedOption.value)
  emit('select', {
    type: 'accommodation',
    choice: {
      id: selectedOption.value.id,
      name: selectedOption.value.name,
      hotel_type: selectedOption.value.hotel_type,
      rating: selectedOption.value.rating || selectedOption.value.star_rating,
      price_per_night: selectedOption.value.price_per_night,
      nights: selectedOption.value.nights,
      total_cost: totalCost,
      room_type: selectedOption.value.room_type,
      facilities: selectedOption.value.facilities,
      location: selectedOption.value.location,
      distance_to_center: selectedOption.value.distance_to_center,
      tags: selectedOption.value.tags,
      phone: selectedOption.value.phone,
      description: selectedOption.value.description,
      reason: selectedOption.value.reason
    },
    message: `我选择${selectedOption.value.name}`
  })
}
</script>

<style scoped lang="scss">
.accommodation-selector {
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
  
  .hotels-list {
    display: grid;
    gap: 15px;
    margin-bottom: 20px;
    
    .hotel-card {
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
      
      &.premium {
        border-color: #f56c6c;
      }
      
      &.selected {
        border-color: #409eff;
        background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
      }
      
      .card-number {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
          padding-bottom: 12px;
          border-bottom: 2px solid #f0f2f5;
          
          .header-left {
            flex: 1;
            
            .hotel-name {
              font-size: 20px;
              font-weight: 600;
              color: #303133;
              margin-bottom: 8px;
            }

            .hotel-badges {
              display: flex;
              align-items: center;
              gap: 10px;
              flex-wrap: wrap;
            }
          }
          
          .header-right {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            padding-left: 20px;
            
            .cost-label {
              font-size: 12px;
              color: #909399;
            }
            
            .cost-value {
              font-size: 24px;
              font-weight: 700;
              color: #f56c6c;
            }
            
            .nights-info {
              font-size: 11px;
              color: #909399;
              margin-top: 2px;
            }
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
          
          .facilities-section,
          .tags-section {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 12px;
            
            .section-label {
              font-size: 13px;
              color: #606266;
              font-weight: 600;
              min-width: 50px;
              flex-shrink: 0;
            }
            
            .facilities-tags,
            .tags-list {
              display: flex;
              flex-wrap: wrap;
              gap: 5px;
            }
          }
          
          .info-details {
            .detail-item {
              display: flex;
              margin-bottom: 6px;
              font-size: 13px;
              line-height: 1.6;
              
              .detail-label {
                color: #909399;
                min-width: 50px;
                flex-shrink: 0;
              }
              
              .detail-value {
                color: #303133;
                flex: 1;
              }
            }
          }
          
          .reason-box {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            margin-top: 12px;
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
