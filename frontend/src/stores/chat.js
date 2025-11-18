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

  // 计算属性
  const hasMessages = computed(() => messages.value.length > 0)

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

  async function sendMessage(content) {
    loading.value = true
    
    // 添加用户消息
    addMessage({
      role: 'user',
      content
    })

    try {
      const response = await sendMessageAPI({
        session_id: sessionId.value,
        message: content
      })

      // 添加Agent回复
      if (response.data) {
        addMessage({
          role: 'assistant',
          content: response.data.reply,
          itinerary: response.data.itinerary // 保存行程数据
        })

        // 更新状态
        if (response.data.stage) {
          currentStage.value = response.data.stage
        }
        if (response.data.requirements) {
          currentRequirements.value = response.data.requirements
        }
        if (response.data.itinerary) {
          currentItinerary.value = response.data.itinerary
        }
      }

      return response
    } catch (error) {
      console.error('发送消息失败:', error)
      throw error
    } finally {
      loading.value = false
    }
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
    hasMessages,
    addMessage,
    sendMessage,
    reset
  }
})

