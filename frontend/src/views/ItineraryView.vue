<template>
  <div class="itinerary-view">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>正在加载行程...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="$router.push('/')">返回首页</button>
    </div>

    <div v-else-if="itinerary" class="itinerary-content">
      <!-- 行程头部 -->
      <div class="itinerary-header">
        <h1>{{ itinerary.destination }} - {{ itinerary.days }}日游</h1>
        <div class="meta">
          <span>💰 预算: ¥{{ itinerary.budget }}</span>
          <span v-if="itinerary.preferences">🎯 偏好: {{ itinerary.preferences.join('、') }}</span>
        </div>
      </div>

      <!-- 行程详情 -->
      <div class="itinerary-days">
        <div v-for="(day, index) in itinerary.schedule" :key="index" class="day-card">
          <h2>Day {{ index + 1 }}</h2>
          <div class="activities">
            <div v-for="(activity, idx) in day.activities" :key="idx" class="activity">
              <span class="time">{{ activity.time }}</span>
              <div class="activity-info">
                <h3>{{ activity.name }}</h3>
                <p>{{ activity.description }}</p>
                <span v-if="activity.cost" class="cost">💵 约 ¥{{ activity.cost }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <button @click="adjustItinerary" class="btn-secondary">调整行程</button>
        <button @click="saveItinerary" class="btn-primary">保存行程</button>
      </div>
    </div>

    <div v-else class="empty">
      <p>暂无行程数据</p>
      <button @click="$router.push('/')">开始规划</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ItineraryView',
  data() {
    return {
      itinerary: null,
      loading: false,
      error: null
    }
  },
  mounted() {
    this.loadItinerary()
  },
  methods: {
    loadItinerary() {
      const id = this.$route.params.id
      
      // TODO: 从API加载行程
      // 暂时使用模拟数据
      this.itinerary = {
        destination: '杭州',
        days: 3,
        budget: 3000,
        preferences: ['文化', '美食'],
        schedule: [
          {
            activities: [
              {
                time: '09:00',
                name: '西湖',
                description: '游览西湖十景，感受江南美景',
                cost: 0
              },
              {
                time: '12:00',
                name: '楼外楼',
                description: '品尝正宗杭帮菜',
                cost: 150
              }
            ]
          }
        ]
      }
    },
    adjustItinerary() {
      this.$router.push('/')
    },
    saveItinerary() {
      alert('保存功能开发中...')
    }
  }
}
</script>

<style scoped>
.itinerary-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.loading, .error, .empty {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.itinerary-header {
  margin-bottom: 30px;
}

.itinerary-header h1 {
  font-size: 28px;
  margin-bottom: 10px;
}

.meta {
  display: flex;
  gap: 20px;
  color: #666;
}

.day-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.day-card h2 {
  font-size: 20px;
  color: #42b983;
  margin-bottom: 15px;
}

.activity {
  display: flex;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.activity:last-child {
  border-bottom: none;
}

.time {
  font-weight: bold;
  color: #666;
  min-width: 60px;
}

.activity-info h3 {
  font-size: 16px;
  margin-bottom: 5px;
}

.activity-info p {
  color: #666;
  margin-bottom: 5px;
}

.cost {
  color: #f56c6c;
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
}

button {
  padding: 12px 30px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #42b983;
  color: white;
}

.btn-primary:hover {
  background: #35a072;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.error button, .empty button {
  background: #42b983;
  color: white;
  margin-top: 20px;
}
</style>

