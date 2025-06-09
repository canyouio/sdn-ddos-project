import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import WhitelistBlacklistView from '../views/WhitelistBlacklistView.vue'
const routes = [
  { path: '/', name: 'Dashboard', component: DashboardView },
  { path: '/lists', name: 'Lists', component: WhitelistBlacklistView },
]
const router = createRouter({ history: createWebHistory(), routes })
export default router
