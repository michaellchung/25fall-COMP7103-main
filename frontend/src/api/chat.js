import request from './index'

/**
 * 发送消息
 */
export function sendMessage(data) {
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

