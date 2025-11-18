import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'chat',
      component: ChatView,
      meta: { title: '对话' }
    },
    {
      path: '/itinerary/:id?',
      name: 'itinerary',
      component: () => import('../views/ItineraryView.vue'),
      meta: { title: '行程' }
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('../views/HistoryView.vue'),
      meta: { title: '历史记录' }
    }
  ]
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || ''} - TravelMate AI`
  next()
})

export default router

