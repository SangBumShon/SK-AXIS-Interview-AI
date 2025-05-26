import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import InterviewView from './components/InterviewView.vue'
import InterviewResult from './components/InterviewResult.vue'
import InterviewAdminDashboard from './components/InterviewAdminDashboard.vue'
import './assets/main.css'

// Font Awesome
import '@fortawesome/fontawesome-free/css/all.min.css'

// Tailwind CSS
import './assets/tailwind.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/interview'
    },
    {
      path: '/interview',
      name: 'interview',
      component: InterviewView
    },
    {
      path: '/result',
      name: 'result',
      component: InterviewResult,
      props: true
    },
    {
      path: '/admin',
      name: 'admin',
      component: InterviewAdminDashboard
    }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app') 