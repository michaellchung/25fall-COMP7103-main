import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sendMessage as sendMessageAPI, resetChat as resetChatAPI } from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const sessionId = ref(generateSessionId())
  const messages = ref([])
  const currentRequirements = ref({})
  const currentItinerary = ref(null)
  const loading = ref(false)
  const currentStage = ref('greeting')
  
  // 预算追踪
  const budgetTracking = ref({
    total: 0,           // 总预算
    used: 0,            // 已使用
    transport: 0,       // 交通费用
    attractions: 0,     // 景点费用
    food: 0,            // 餐饮费用
    accommodation: 0    // 住宿费用
  })

  // 计算属性
  const hasMessages = computed(() => messages.value.length > 0)
  
  const budgetRemaining = computed(() => budgetTracking.value.total - budgetTracking.value.used)
  
  const budgetPercentage = computed(() => {
    if (budgetTracking.value.total === 0) return 0
    return Math.min(100, (budgetTracking.value.used / budgetTracking.value.total) * 100)
  })
  
  const budgetStatus = computed(() => {
    const percentage = budgetPercentage.value
    if (percentage < 60) return 'success'
    if (percentage < 85) return 'warning'
    return 'danger'
  })

  // 方法
  function generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  function addMessage(message) {
    messages.value.push({
      ...message,
      timestamp: new Date().toISOString()
    })
  }

  async function sendMessage(content, selection = null) {
    loading.value = true
    console.log('🚀 [Store] 发送消息开始')
    console.log('📝 [Store] 内容:', content)
    console.log('📦 [Store] 选择:', selection)
    
    // 添加用户消息
    addMessage({
      role: 'user',
      content
    })
    console.log('✅ [Store] 用户消息已添加')

    try {
      const requestData = {
        session_id: sessionId.value,
        message: content
      }
      
      // 如果有selection数据，添加到请求中
      if (selection) {
        requestData.selection = selection
      }
      
      console.log('📤 [Store] 发送请求:', requestData)
      const response = await sendMessageAPI(requestData)
      console.log('📥 [Store] 收到响应:', response)
      console.log('📊 [Store] 响应数据:', response.data)

      // 添加Agent回复
      if (response.data) {
        const assistantMessage = {
          role: 'assistant',
          content: response.data.reply,
          itinerary: response.data.itinerary, // 保存行程数据
          recommendation: response.data.recommendation // 保存推荐数据
        }
        
        console.log('💬 [Store] 准备添加助手消息:', assistantMessage)
        console.log('🗺️ [Store] 是否有itinerary:', !!response.data.itinerary)
        console.log('💡 [Store] 是否有recommendation:', !!response.data.recommendation)
        
        addMessage(assistantMessage)
        console.log('✅ [Store] 助手消息已添加')
        console.log('📋 [Store] 当前消息数:', messages.value.length)

        // 更新状态
        if (response.data.stage) {
          currentStage.value = response.data.stage
          console.log('🎯 [Store] 阶段更新为:', response.data.stage)
        }
        if (response.data.requirements) {
          currentRequirements.value = response.data.requirements
          // 初始化预算
          if (response.data.requirements.budget && budgetTracking.value.total === 0) {
            budgetTracking.value.total = response.data.requirements.budget
            console.log('💰 [Store] 初始化总预算:', budgetTracking.value.total)
          }
        }
        if (response.data.itinerary) {
          currentItinerary.value = response.data.itinerary
          console.log('🎉 [Store] 行程已保存到store')
        }
      }

      return response
    } catch (error) {
      console.error('❌ [Store] 发送消息失败:', error)
      throw error
    } finally {
      loading.value = false
      console.log('🏁 [Store] Loading已清除')
    }
  }

  // 更新预算使用情况
  function updateBudget(category, amount) {
    console.log(`💰 [Store] 更新预算 - ${category}: ¥${amount}`)
    budgetTracking.value[category] = amount
    
    // 重新计算总使用
    budgetTracking.value.used = 
      budgetTracking.value.transport +
      budgetTracking.value.attractions +
      budgetTracking.value.food +
      budgetTracking.value.accommodation
    
    console.log(`💰 [Store] 已使用: ¥${budgetTracking.value.used} / ¥${budgetTracking.value.total}`)
  }

  async function reset() {
    try {
      await resetChatAPI(sessionId.value)
      
      // 重置状态
      sessionId.value = generateSessionId()
      messages.value = []
      currentRequirements.value = {}
      currentItinerary.value = null
      currentStage.value = 'greeting'
      budgetTracking.value = {
        total: 0,
        used: 0,
        transport: 0,
        attractions: 0,
        food: 0,
        accommodation: 0
      }
    } catch (error) {
      console.error('重置对话失败:', error)
      throw error
    }
  }

  return {
    sessionId,
    messages,
    currentRequirements,
    currentItinerary,
    loading,
    currentStage,
    budgetTracking,
    budgetRemaining,
    budgetPercentage,
    budgetStatus,
    hasMessages,
    addMessage,
    sendMessage,
    updateBudget,
    reset
  }
})

