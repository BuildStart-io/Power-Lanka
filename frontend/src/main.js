import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Import views
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import ProductsView from './views/ProductsView.vue'
import CustomersView from './views/CustomersView.vue'
import UsersView from './views/UsersView.vue'
import ChatHistoryView from './views/ChatHistoryView.vue'

import WhatsAppView from './views/WhatsAppView.vue'
import OrdersView from './views/OrdersView.vue'

// Router configuration
const routes = [
    { path: '/login', name: 'Login', component: LoginView },
    { path: '/', name: 'Dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/products', name: 'Products', component: ProductsView, meta: { requiresAuth: true } },
    { path: '/admins', name: 'Admins', component: UsersView, meta: { requiresAuth: true } },
    { path: '/orders', name: 'Orders', component: OrdersView, meta: { requiresAuth: true } },
    { path: '/whatsapp', name: 'WhatsApp', component: WhatsAppView, meta: { requiresAuth: true } },
    { path: '/customers', name: 'Customers', component: CustomersView, meta: { requiresAuth: true } },
    { path: '/chat/:phone', name: 'ChatHistory', component: ChatHistoryView, meta: { requiresAuth: true } },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('admin_token')
    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.path === '/login' && token) {
        next('/')
    } else {
        next()
    }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
