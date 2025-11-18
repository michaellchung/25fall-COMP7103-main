import request from './index'

/**
 * 生成行程
 */
export function generateItinerary(data) {
  return request({
    url: '/itinerary/generate',
    method: 'post',
    data
  })
}

/**
 * 获取行程详情
 */
export function getItinerary(itineraryId) {
  return request({
    url: `/itinerary/${itineraryId}`,
    method: 'get'
  })
}

/**
 * 更新行程
 */
export function updateItinerary(itineraryId, data) {
  return request({
    url: `/itinerary/${itineraryId}`,
    method: 'put',
    data
  })
}

