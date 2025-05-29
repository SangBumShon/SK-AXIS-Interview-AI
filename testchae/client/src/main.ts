import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import InterviewSetup from './components/InterviewSetup.vue'
import Interview from './components/Interview.vue'

// Tailwind CSS
import './assets/tailwind.css'
import './assets/main.css'

// Font Awesome
import '@fortawesome/fontawesome-free/css/all.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'setup',
      component: InterviewSetup
    },
    {
      path: '/interview',
      name: 'interview',
      component: Interview,
      props: (route) => ({
        roomName: route.query.roomName as string,
        timeRange: route.query.timeRange as string,
        interviewers: route.query.interviewers as string,
        candidates: JSON.parse(route.query.candidates as string || '[]'),
        candidateIds: JSON.parse(route.query.candidateIds as string || '[]')
      })
    }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app') 