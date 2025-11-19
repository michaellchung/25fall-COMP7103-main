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
    
    <div class="hotels-grid">
      <div 
        v-for="option in options" 
        :key="option.id"
        class="hotel-card"
        :class="{ 
          'premium': option.hotel_type === '高档型',
          'selected': selectedOption?.id === option.id 
        }"
        @click="selectHotel(option)"
      >
        <div class="card-header">
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

        <div class="card-body">
          <!-- 价格信息 -->
          <div class="price-section">
            <div class="price-row">
              <span class="label">💰 每晚价格：</span>
              <span class="value price">¥{{ option.price_per_night }}</span>
            </div>
            <div class="price-row">
              <span class="label">🛏️ 住宿天数：</span>
              <span class="value">{{ option.nights }}晚</span>
            </div>
            <div class="price-row total">
              <span class="label">💵 总费用：</span>
              <span class="value total-price">¥{{ option.total_cost || (option.price_per_night * option.nights) }}</span>
            </div>
          </div>

          <!-- 房型信息 -->
          <div class="room-section" v-if="option.room_type">
            <div class="section-title">🚪 房型信息</div>
            <div class="info-text">{{ option.room_type }}</div>
          </div>

          <!-- 设施信息 -->
          <div class="facilities-section" v-if="option.facilities && option.facilities.length">
            <div class="section-title">✨ 酒店设施</div>
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

          <!-- 详细信息 -->
          <div class="details-section">
            <div v-if="option.description" class="detail-row">
              <span class="detail-label">📝 简介：</span>
              <span class="detail-value">{{ option.description }}</span>
            </div>
            <div v-if="option.location && option.location.address" class="detail-row">
              <span class="detail-label">📍 地址：</span>
              <span class="detail-value">{{ option.location.address }}</span>
            </div>
            <div v-if="option.distance_to_center !== undefined" class="detail-row">
              <span class="detail-label">📏 距中心：</span>
              <span class="detail-value">{{ option.distance_to_center.toFixed(2) }}km</span>
            </div>
            <div v-if="option.location && option.location.lat" class="detail-row">
              <span class="detail-label">🗺️ 坐标：</span>
              <span class="detail-value">
                {{ option.location.lat }}, {{ option.location.lng }}
              </span>
            </div>
            <div v-if="option.phone" class="detail-row">
              <span class="detail-label">📞 电话：</span>
              <span class="detail-value">{{ option.phone }}</span>
            </div>
            <div v-if="option.tags && option.tags.length" class="detail-row tags">
              <span class="detail-label">🏷️ 标签：</span>
              <span class="detail-value">
                <el-tag 
                  v-for="tag in option.tags" 
                  :key="tag"
                  type="info"
                  size="small"
                  effect="plain"
                >
                  {{ tag }}
                </el-tag>
              </span>
            </div>
          </div>

          <!-- 推荐理由 -->
          <div class="reason-section" v-if="option.reason">
            <div class="section-title">📝 推荐理由</div>
            <div class="reason-text">{{ option.reason }}</div>
          </div>
        </div>

        <div class="card-footer">
          <el-button 
            v-if="selectedOption?.id === option.id"
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
  
  .hotels-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
    
    .hotel-card {
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
      
      &.premium {
        border-color: #f56c6c;
        background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);
      }
      
      &.selected {
        border-color: #409eff;
        background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
      }
      
      .card-header {
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f0f2f5;
        
        .hotel-name {
          font-size: 20px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 10px;
        }

        .hotel-badges {
          display: flex;
          align-items: center;
          gap: 10px;
          flex-wrap: wrap;
        }
      }
      
      .card-body {
        margin-bottom: 15px;
        
        .price-section {
          background: #fff9f0;
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 15px;

          .price-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-size: 14px;

            &:last-child {
              margin-bottom: 0;
            }

            .label {
              color: #909399;
              font-weight: 500;
            }

            .value {
              color: #303133;
              font-weight: 600;

              &.price {
                color: #f56c6c;
                font-size: 18px;
              }

              &.total-price {
                color: #e6a23c;
                font-size: 20px;
              }
            }

            &.total {
              margin-top: 8px;
              padding-top: 8px;
              border-top: 1px dashed #e4e7ed;
            }
          }
        }

        .room-section,
        .facilities-section,
        .details-section,
        .reason-section {
          margin-bottom: 15px;

          .section-title {
            font-size: 14px;
            font-weight: 600;
            color: #606266;
            margin-bottom: 10px;
            padding-left: 8px;
            border-left: 3px solid #409eff;
          }

          .info-text {
            padding: 8px 12px;
            background: #f5f7fa;
            border-radius: 6px;
            color: #303133;
            font-size: 13px;
          }

          .facilities-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
          }

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

        .details-section {
          background: #f5f7fa;
          border-radius: 8px;
          padding: 12px;

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
              min-width: 80px;
              flex-shrink: 0;
              font-weight: 500;
            }

            .detail-value {
              color: #303133;
              flex: 1;
            }

            &.tags {
              flex-wrap: wrap;
              gap: 5px;

              .detail-value {
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
              }
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
