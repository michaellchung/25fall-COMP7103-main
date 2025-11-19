import request from './index'

/**
 * 发送消息
 */
export function sendMessage(data) {
  console.log('🌐 [API] sendMessage被调用')
  console.log('📦 [API] 发送的数据:', data)
  console.log('💬 [API] message:', data.message)
  console.log('🎁 [API] selection:', data.selection)
  
  return request({
    url: '/chat',
    method: 'post',
    data
  })
}

/**
 * 重置对话
 */
export function resetChat(sessionId) {
  return request({
    url: '/chat/reset',
    method: 'post',
    data: { session_id: sessionId }
  })
}

/**
 * 获取欢迎消息
 */
export function getWelcomeMessage() {
  return request({
    url: '/chat/welcome',
    method: 'get'
  })
}

