<!-- src/components/Login.vue -->
<template>
    <div class="min-h-screen bg-white flex justify-center items-center relative">
      <button 
        @click="showAdminLogin = true"
        class="absolute top-4 right-4 text-gray-600 hover:text-gray-800 transition-colors cursor-pointer"
      >
        <i class="fas fa-cog text-2xl"></i>
      </button>
      
      <div class="w-full max-w-md bg-white rounded-lg shadow-lg p-8">
        <div class="text-center mb-8">
          <h1 class="text-4xl font-bold">
            <span class="text-red-600">SK</span><span class="text-orange-500">AXIS</span>
          </h1>
        </div>
        <div class="text-center mb-6">
          <h2 class="text-2xl font-bold mb-2 text-gray-800">AI 면접 시스템</h2>
          <p class="text-gray-600">면접관 로그인</p>
        </div>
        
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">아이디</label>
            <input
              type="text"
              v-model="loginForm.username"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">비밀번호</label>
            <input
              type="password"
              v-model="loginForm.password"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              required
            />
          </div>
          <div v-if="loginError" class="text-red-600 text-sm text-center">
            {{ loginError }}
          </div>
          <button
            type="submit"
            class="w-full bg-red-600 text-white py-3 rounded-md font-medium hover:bg-red-700 transition-colors"
          >
            로그인
          </button>
        </form>
        
        <div class="mt-6 text-center text-xs text-gray-500">
          <p>© 2025 SK AXIS. All rights reserved.</p>
          <p>2025년 6월 16일 최신 기준</p>
        </div>
      </div>
      
      <!-- Admin Login Modal -->
      <AdminLoginModal 
        v-if="showAdminLogin"
        @close="showAdminLogin = false"
        @login="handleAdminLogin"
      />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import AdminLoginModal from './AdminLoginModal.vue'
  
  const router = useRouter()
  
  const loginForm = ref({
    username: '',
    password: ''
  })
  
  const loginError = ref('')
  const showAdminLogin = ref(false)
  
  const handleLogin = async () => {
    try {
      // 데모 계정 체크
      if (loginForm.value.username === '123' && loginForm.value.password === '123') {
        // 로그인 성공 시 InterviewSetup으로 이동
        router.push('/setup')
      } else {
        loginError.value = '아이디 또는 비밀번호가 올바르지 않습니다.'
      }
    } catch (error) {
      loginError.value = '로그인 중 오류가 발생했습니다.'
    }
  }
  
  const handleAdminLogin = () => {
    router.push('/admin')
  }
  </script>