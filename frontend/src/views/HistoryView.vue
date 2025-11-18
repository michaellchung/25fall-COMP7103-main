<template>
  <div class="history-view">
    <h1>历史记录</h1>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="histories.length === 0" class="empty">
      <p>暂无历史记录</p>
      <button @click="$router.push('/')">开始规划</button>
    </div>

    <div v-else class="history-list">
      <div 
        v-for="item in histories" 
        :key="item.id" 
        class="history-card"
        @click="viewItinerary(item.id)"
      >
        <div class="card-header">
          <h3>{{ item.destination }} - {{ item.days }}日游</h3>
          <span class="date">{{ formatDate(item.created_at) }}</span>
        </div>
        <div class="card-body">
          <p>💰 预算: ¥{{ item.budget }}</p>
          <p v-if="item.preferences">🎯 偏好: {{ item.preferences.join('、') }}</p>
        </div>
        <div class="card-actions">
          <button @click.stop="deleteHistory(item.id)" class="btn-delete">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HistoryView',
  data() {
    return {
      histories: [],
      loading: false
    }
  },
  mounted() {
    this.loadHistories()
  },
  methods: {
    loadHistories() {
      this.loading = true
      
      // TODO: 从API加载历史记录
      // 暂时使用模拟数据
      setTimeout(() => {
        this.histories = [
          {
            id: '1',
            destination: '杭州',
            days: 3,
            budget: 3000,
            preferences: ['文化', '美食'],
            created_at: new Date().toISOString()
          }
        ]
        this.loading = false
      }, 500)
    },
    viewItinerary(id) {
      this.$router.push(`/itinerary/${id}`)
    },
    deleteHistory(id) {
      if (confirm('确定要删除这条记录吗？')) {
        this.histories = this.histories.filter(item => item.id !== id)
        // TODO: 调用API删除
      }
    },
    formatDate(dateStr) {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.history-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  font-size: 28px;
  margin-bottom: 30px;
}

.loading, .empty {
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

.empty button {
  margin-top: 20px;
  padding: 12px 30px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.empty button:hover {
  background: #35a072;
}

.history-list {
  display: grid;
  gap: 20px;
}

.history-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.history-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.card-header h3 {
  font-size: 20px;
  color: #333;
}

.date {
  color: #999;
  font-size: 14px;
}

.card-body {
  margin-bottom: 15px;
}

.card-body p {
  margin: 5px 0;
  color: #666;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-delete {
  padding: 6px 16px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-delete:hover {
  background: #e34e4e;
}
</style>

