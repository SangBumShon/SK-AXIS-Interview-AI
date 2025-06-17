import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import InterviewerLogin from './components/InterviewerLogin.vue' // Login 컴포넌트 추가
import InterviewSetup from './components/InterviewSetup.vue'
import Interview from './components/Interview.vue'
import InterviewResult from './components/InterviewResult.vue'
import AdminDashboard from './components/AdminDashboard.vue'

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
      name: 'login',
      component: InterviewerLogin // 메인 페이지를 InterviewerLogin으로 변경
    },
    {
      path: '/setup',
      name: 'setup',
      component: InterviewSetup // InterviewSetup을 /setup 경로로 이동
    },
    {
      path: '/interview',
      name: 'interview',
      component: Interview,
      props: (route) => ({
        roomName: route.query.roomName as string,
        timeRange: route.query.timeRange as string,
        interviewers: route.query.interviewers as string,
        interviewerIds: JSON.parse(route.query.interviewerIds as string || '[]'),
        candidates: JSON.parse(route.query.candidates as string || '[]'),
        candidateIds: JSON.parse(route.query.candidateIds as string || '[]')
      })
    },
    {
      path: '/result',
      name: 'result',
      component: InterviewResult,
      props: (route) => ({
        interviewResults: JSON.parse(route.query.results as string || '[]'),
        selectedCandidates: JSON.parse(route.query.candidates as string || '[]'),
        initialTab: parseInt(route.query.tab as string || '0')
      })
    },
    {
      path: '/admin',
      name: 'AdminDashboard',
      component: AdminDashboard
    }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app')