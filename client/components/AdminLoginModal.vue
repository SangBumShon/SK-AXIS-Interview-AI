<template>
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4 relative animate-fadeIn">
        <button @click="emitClose" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <i class="fas fa-times"></i>
        </button>
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold mb-2">
            <span class="text-red-600">SK</span><span class="text-orange-500">AXIS</span>
          </h2>
          <p class="text-gray-600">관리자 로그인</p>
        </div>
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">아이디</label>
            <input
              type="text"
              v-model="username"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">비밀번호</label>
            <input
              type="password"
              v-model="password"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              required
            />
          </div>
          <div v-if="error" class="text-red-600 text-sm text-center">{{ error }}</div>
          <button
            type="submit"
            class="w-full bg-red-600 text-white py-2 rounded-md hover:bg-red-700 transition-colors !rounded-button whitespace-nowrap"
          >
            로그인
          </button>
        </form>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  
  const router = useRouter();
  const emit = defineEmits(['close', 'login']);
  const username = ref('');
  const password = ref('');
  const error = ref('');
  
  const handleLogin = async () => {
  try {
    fetch('http://sk-axis-springboot:8080/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        userName: username.value,
        password: password.value
      })
    })
    router.push('/admin');
    emit('login');
  } catch (error) {
    console.error('로그인 중 오류 발생:', error);
    error = '로그인에 실패했습니다. 다시 시도해주세요.';
    return;
  }
}
  function emitClose() {
    emit('close');
    username.value = '';
    password.value = '';
    error.value = '';
  }
  </script>
  
  <style scoped>
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  .animate-fadeIn {
    animation: fadeIn 0.3s ease-in-out;
  }
  </style>
  