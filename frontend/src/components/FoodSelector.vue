<template>
  <div class="food-selector">
    <h4 class="selector-title">🍜 美食推荐</h4>
    <p class="selector-prompt">{{ prompt }}</p>
    
    <!-- 预算进度条 -->
    <BudgetProgress 
      v-if="budgetTotal > 0"
      :total="budgetTotal"
      :used="budgetUsed"
      :transport="budgetTransport"
      :attractions="budgetAttractions"
      :food="previewFoodCost"
      :accommodation="budgetAccommodation"
      :show-breakdown="true"
    />
    
    <div class="daily-food">
      <div 
        v-for="(restaurants, day) in dailyRestaurants" 
        :key="day"
        class="day-section"
      >
        <div class="day-header">
          <span class="day-badge">第{{ day }}天</span>
          <span class="day-summary">{{ restaurants.length }}家餐厅</span>
        </div>
        
        <div class="restaurants-list">
          <div 
            v-for="(restaurant, index) in restaurants" 
            :key="restaurant.id || index"
            class="restaurant-card"
          >
            <div class="card-number">{{ index + 1 }}</div>
            <div class="card-content">
              <div class="restaurant-header">
                <div class="restaurant-name">{{ restaurant.name }}</div>
                <div class="restaurant-badges">
                  <el-tag v-if="restaurant.cuisine_type" type="warning" size="small">
                    {{ restaurant.cuisine_type }}
                  </el-tag>
                  <el-rate 
                    :model-value="restaurant.rating" 
                    disabled 
                    show-score 
                    text-color="#ff9900"
                    score-template="{value}分"
                    size="small"
                  />
                </div>
              </div>

              <!-- 基本信息 -->
              <div class="restaurant-info">
                <div class="info-item price">
                  <el-icon><Money /></el-icon>
                  <span>人均 ¥{{ restaurant.avg_price }}</span>
                </div>
                <div class="info-item" v-if="restaurant.distance_km">
                  <el-icon><Location /></el-icon>
                  <span>距离 {{ restaurant.distance_km }}km</span>
                </div>
                <div class="info-item" v-if="restaurant.opening_hours">
                  <el-icon><Clock /></el-icon>
                  <span>{{ restaurant.opening_hours }}</span>
                </div>
              </div>

              <!-- 详细信息 -->
              <div class="restaurant-details">
                <div v-if="restaurant.description" class="detail-row">
                  <span class="detail-label">📝 简介：</span>
                  <span class="detail-value">{{ restaurant.description }}</span>
                </div>
                <div v-if="restaurant.signature_dishes && restaurant.signature_dishes.length" class="detail-row">
                  <span class="detail-label">⭐ 招牌菜：</span>
                  <span class="detail-value">
                    <el-tag 
                      v-for="dish in restaurant.signature_dishes" 
                      :key="dish"
                      type="danger"
                      size="small"
                      style="margin-right: 5px;"
                    >
                      {{ dish }}
                    </el-tag>
                  </span>
                </div>
                <div v-if="restaurant.location && restaurant.location.address" class="detail-row">
                  <span class="detail-label">📍 地址：</span>
                  <span class="detail-value">{{ restaurant.location.address }}</span>
                </div>
                <div v-if="restaurant.location && restaurant.location.lat" class="detail-row">
                  <span class="detail-label">🗺️ 坐标：</span>
                  <span class="detail-value">
                    {{ restaurant.location.lat }}, {{ restaurant.location.lng }}
                  </span>
                </div>
                <div v-if="restaurant.phone" class="detail-row">
                  <span class="detail-label">📞 电话：</span>
                  <span class="detail-value">{{ restaurant.phone }}</span>
                </div>
                <div v-if="restaurant.tags && restaurant.tags.length" class="detail-row tags">
                  <span class="detail-label">🏷️ 标签：</span>
                  <span class="detail-value">
                    <el-tag 
                      v-for="tag in restaurant.tags" 
                      :key="tag"
                      type="success"
                      size="small"
                      effect="plain"
                      style="margin-right: 5px;"
                    >
                      {{ tag }}
                    </el-tag>
                  </span>
                </div>
              </div>

              <!-- 推荐理由 -->
              <div class="restaurant-reason" v-if="restaurant.reason">
                <el-icon><InfoFilled /></el-icon>
                <span>{{ restaurant.reason }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="selector-actions">
      <el-button type="primary" size="large" @click="confirmSelection">
        ✓ 确认推荐
      </el-button>
      <el-button size="large" @click="requestModification">
        ✏️ 我想调整
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Money, Location, Clock, InfoFilled } from '@element-plus/icons-vue'
import { useChatStore } from '@/stores/chat'
import BudgetProgress from './BudgetProgress.vue'

const chatStore = useChatStore()

const props = defineProps({
  dailyRestaurants: {
    type: Object,
    required: true
  },
  prompt: {
    type: String,
    default: '为您推荐了以下美食，请确认或调整：'
  }
})

const emit = defineEmits(['confirm', 'modify'])

// 预算相关计算
const budgetTotal = computed(() => chatStore.budgetTracking.total)
const budgetTransport = computed(() => chatStore.budgetTracking.transport)
const budgetAttractions = computed(() => chatStore.budgetTracking.attractions)
const budgetAccommodation = computed(() => chatStore.budgetTracking.accommodation)

// 计算美食总费用（人均 * 人数）
const previewFoodCost = computed(() => {
  let total = 0
  const companions = chatStore.currentRequirements.companions_count || 2
  
  Object.values(props.dailyRestaurants).forEach(restaurants => {
    restaurants.forEach(restaurant => {
      total += (restaurant.avg_price || 0) * companions
    })
  })
  return total
})

// 计算总使用
const budgetUsed = computed(() => {
  return budgetTransport.value + budgetAttractions.value + previewFoodCost.value + budgetAccommodation.value
})

const confirmSelection = () => {
  // 更新预算
  chatStore.updateBudget('food', previewFoodCost.value)
  
  emit('confirm', {
    type: 'food',
    choice: props.dailyRestaurants,
    message: '确认美食推荐'
  })
}

const requestModification = () => {
  emit('modify', {
    type: 'food',
    message: '我想调整美食推荐'
  })
}
</script>

<style scoped lang="scss">
.food-selector {
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
  
  .daily-food {
    .day-section {
      margin-bottom: 25px;
      
      .day-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 15px;
        
        .day-badge {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
      
      .restaurants-list {
        display: grid;
        gap: 15px;
        
        .restaurant-card {
          background: white;
          border: 2px solid #e4e7ed;
          border-radius: 12px;
          padding: 20px;
          display: flex;
          gap: 15px;
          transition: all 0.3s ease;
          
          &:hover {
            border-color: #f5576c;
            box-shadow: 0 4px 12px rgba(245, 87, 108, 0.15);
            transform: translateX(5px);
          }
          
          .card-number {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
            
            .restaurant-header {
              display: flex;
              align-items: center;
              justify-content: space-between;
              margin-bottom: 12px;
              flex-wrap: wrap;
              gap: 10px;
              
              .restaurant-name {
                font-size: 18px;
                font-weight: 600;
                color: #303133;
              }

              .restaurant-badges {
                display: flex;
                align-items: center;
                gap: 10px;
              }
            }
            
            .restaurant-info {
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
                  color: #f5576c;
                }

                &.price {
                  font-weight: 600;
                  color: #f56c6c;
                  font-size: 16px;
                }
              }
            }

            .restaurant-details {
              background: #fff7f0;
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

                &.tags {
                  flex-wrap: wrap;
                  gap: 5px;
                }
              }
            }
            
            .restaurant-reason {
              display: flex;
              align-items: center;
              gap: 8px;
              padding: 10px;
              background: rgba(245, 87, 108, 0.1);
              border-radius: 8px;
              color: #f5576c;
              font-size: 13px;
              border-left: 3px solid #f5576c;
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
