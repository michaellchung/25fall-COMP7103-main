<template>
  <div class="budget-progress">
    <div class="budget-header">
      <div class="budget-title">
        <span class="icon">💰</span>
        <span class="text">预算使用情况</span>
      </div>
      <div class="budget-amount">
        <span class="used">¥{{ used }}</span>
        <span class="separator">/</span>
        <span class="total">¥{{ total }}</span>
      </div>
    </div>

    <el-progress 
      :percentage="percentage" 
      :status="status"
      :stroke-width="20"
      :show-text="false"
    />

    <div class="budget-details">
      <div class="detail-row">
        <span class="label">剩余预算：</span>
        <span class="value" :class="remainingClass">¥{{ remaining }}</span>
      </div>
      <div class="detail-row">
        <span class="label">使用比例：</span>
        <span class="value">{{ percentage.toFixed(1) }}%</span>
      </div>
    </div>

    <!-- 分类明细 -->
    <div class="budget-breakdown" v-if="showBreakdown">
      <div class="breakdown-title">费用明细</div>
      <div class="breakdown-items">
        <div class="breakdown-item" v-if="transport > 0">
          <span class="item-icon">🚗</span>
          <span class="item-label">交通</span>
          <span class="item-value">¥{{ transport }}</span>
        </div>
        <div class="breakdown-item" v-if="attractions > 0">
          <span class="item-icon">✨</span>
          <span class="item-label">景点</span>
          <span class="item-value">¥{{ attractions }}</span>
        </div>
        <div class="breakdown-item" v-if="food > 0">
          <span class="item-icon">🍜</span>
          <span class="item-label">美食</span>
          <span class="item-value">¥{{ food }}</span>
        </div>
        <div class="breakdown-item" v-if="accommodation > 0">
          <span class="item-icon">🏨</span>
          <span class="item-label">住宿</span>
          <span class="item-value">¥{{ accommodation }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: {
    type: Number,
    required: true
  },
  used: {
    type: Number,
    default: 0
  },
  transport: {
    type: Number,
    default: 0
  },
  attractions: {
    type: Number,
    default: 0
  },
  food: {
    type: Number,
    default: 0
  },
  accommodation: {
    type: Number,
    default: 0
  },
  showBreakdown: {
    type: Boolean,
    default: false
  }
})

const remaining = computed(() => props.total - props.used)

const percentage = computed(() => {
  if (props.total === 0) return 0
  return Math.min(100, (props.used / props.total) * 100)
})

const status = computed(() => {
  const p = percentage.value
  if (p < 60) return 'success'
  if (p < 85) return 'warning'
  return 'exception'
})

const remainingClass = computed(() => {
  if (remaining.value < 0) return 'negative'
  if (remaining.value < props.total * 0.15) return 'warning'
  return 'positive'
})
</script>

<style scoped lang="scss">
.budget-progress {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);

  .budget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;

    .budget-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;

      .icon {
        font-size: 20px;
      }
    }

    .budget-amount {
      font-size: 18px;
      font-weight: 700;

      .used {
        color: #ffd700;
      }

      .separator {
        margin: 0 5px;
        opacity: 0.7;
      }

      .total {
        opacity: 0.9;
      }
    }
  }

  :deep(.el-progress) {
    margin-bottom: 15px;

    .el-progress-bar__outer {
      background-color: rgba(255, 255, 255, 0.3);
    }

    .el-progress-bar__inner {
      transition: all 0.4s ease;
    }
  }

  .budget-details {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    margin-bottom: 15px;

    .detail-row {
      display: flex;
      align-items: center;
      gap: 5px;

      .label {
        opacity: 0.9;
      }

      .value {
        font-weight: 600;
        font-size: 16px;

        &.positive {
          color: #a8ff78;
        }

        &.warning {
          color: #ffd700;
        }

        &.negative {
          color: #ff6b6b;
        }
      }
    }
  }

  .budget-breakdown {
    border-top: 1px solid rgba(255, 255, 255, 0.3);
    padding-top: 15px;

    .breakdown-title {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 10px;
      opacity: 0.9;
    }

    .breakdown-items {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;

      .breakdown-item {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.15);
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 13px;

        .item-icon {
          font-size: 16px;
        }

        .item-label {
          flex: 1;
          opacity: 0.9;
        }

        .item-value {
          font-weight: 600;
          color: #ffd700;
        }
      }
    }
  }
}
</style>

