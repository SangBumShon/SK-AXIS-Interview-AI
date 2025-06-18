<!-- src/components/InterviewerLogin.vue -->
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
        <p class="text-gray-600">{{ showRegistration ? '회원가입' : '면접관 로그인' }}</p>
      </div>
      
      <!-- 로그인 폼 -->
      <form v-if="!showRegistration" @submit.prevent="handleLogin" class="space-y-4">
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
        <div class="text-center mt-4">
          <button
            @click.prevent="showRegistration = true"
            class="text-gray-500 hover:text-gray-700 text-sm underline"
          >
            회원가입
          </button>
        </div>
      </form>

      <!-- 회원가입 폼 -->
      <form v-else @submit.prevent="handleRegistration" class="space-y-4">
        <div class="mb-6 flex items-center">
          <button 
            @click.prevent="showRegistration = false" 
            class="text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <i class="fas fa-arrow-left text-sm"></i>
            <span class="text-sm">로그인으로 돌아가기</span>
          </button>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">이름</label>
          <input
            type="text"
            v-model="registrationForm.name"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">아이디</label>
          <input
            type="text"
            v-model="registrationForm.username"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">이메일</label>
          <input
            type="email"
            v-model="registrationForm.email"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">비밀번호</label>
          <input
            type="password"
            v-model="registrationForm.password"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">비밀번호 확인</label>
          <input
            type="password"
            v-model="registrationForm.confirmPassword"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">부서</label>
          <select
            v-model="registrationForm.department"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          >
            <option value="">부서 선택</option>
            <option value="IT">IT 개발부</option>
            <option value="HR">인사부</option>
            <option value="Marketing">마케팅부</option>
            <option value="Sales">영업부</option>
            <option value="Finance">재무부</option>
            <option value="Design">디자인팀</option>
            <option value="Data">데이터팀</option>
          </select>
        </div>
        <div v-if="registrationError" class="text-red-600 text-sm text-center">
          {{ registrationError }}
        </div>
        <button
          type="submit"
          class="w-full bg-red-600 text-white py-3 rounded-md font-medium hover:bg-red-700 transition-colors"
        >
          회원가입
        </button>
      </form>
      
      <div class="mt-6 text-center text-xs text-gray-500">
        <p>© 2025 SK AXIS. All rights reserved.</p>
        <p>2025년 6월 17일 최신 기준</p>
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

// 로그인 폼 데이터
const loginForm = ref({
  username: '',
  password: ''
})

// 회원가입 폼 데이터
const registrationForm = ref({
  name: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  department: ''
})

// 상태 관리
const loginError = ref('')
const registrationError = ref('')
const showAdminLogin = ref(false)
const showRegistration = ref(false)

// 로그인 처리
const handleLogin = async () => {
  try {
    loginError.value = '';
    
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        userName: loginForm.value.username,
        password: loginForm.value.password
      })
    });

    if (response.ok) {
      // JWT 토큰을 헤더에서 추출
      const authHeader = response.headers.get('Authorization');
      if (authHeader && authHeader.startsWith('Bearer ')) {
        const token = authHeader.substring(7);
        // 토큰을 localStorage에 저장
        localStorage.setItem('accessToken', token);
        console.log('로그인 성공, 토큰 저장됨');
      }
      
      // 로그인 성공 시 면접 설정 페이지로 이동
      router.push('/setup');
    } else {
      let errorMessage = '로그인에 실패했습니다.';
      try {
        const errorData = await response.json();
        errorMessage = errorData.message || errorMessage;
      } catch (e) {
        // JSON 파싱 실패 시 기본 메시지 사용
      }
      loginError.value = errorMessage;
    }
  } catch (error) {
    console.error('로그인 중 오류:', error);
    loginError.value = '네트워크 오류가 발생했습니다. 서버 연결을 확인해주세요.';
  }
}

// 회원가입 처리
const handleRegistration = async () => {
  // 에러 메시지 초기화
  registrationError.value = '';
  
  // 폼 검증
  if (!registrationForm.value.name.trim()) {
    registrationError.value = '이름을 입력해주세요.';
    return;
  }
  
  if (!registrationForm.value.username.trim()) {
    registrationError.value = '아이디를 입력해주세요.';
    return;
  }
  
  if (registrationForm.value.username.length < 3) {
    registrationError.value = '아이디는 3자 이상이어야 합니다.';
    return;
  }
  
  if (!registrationForm.value.email.trim()) {
    registrationError.value = '이메일을 입력해주세요.';
    return;
  }
  
  // 이메일 형식 검증
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(registrationForm.value.email)) {
    registrationError.value = '올바른 이메일 형식을 입력해주세요.';
    return;
  }
  
  if (!registrationForm.value.password) {
    registrationError.value = '비밀번호를 입력해주세요.';
    return;
  }
  
  if (registrationForm.value.password.length < 6) {
    registrationError.value = '비밀번호는 6자 이상이어야 합니다.';
    return;
  }
  
  if (registrationForm.value.password !== registrationForm.value.confirmPassword) {
    registrationError.value = '비밀번호가 일치하지 않습니다.';
    return;
  }
  
  if (!registrationForm.value.department) {
    registrationError.value = '부서를 선택해주세요.';
    return;
  }
  
  // 회원가입 API 호출
  try {
    const response = await fetch('/api/v1/auth/signup/interviewer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        userName: registrationForm.value.username,
        name: registrationForm.value.name,
        password: registrationForm.value.password
      })
    });

    if (response.ok) {
      // 회원가입 성공 처리
      showSuccessModal();
    } else {
      let errorMessage = '회원가입에 실패했습니다.';
      try {
        const errorData = await response.json();
        errorMessage = errorData.message || errorMessage;
      } catch (e) {
        // JSON 파싱 실패 시 기본 메시지 사용
      }
      registrationError.value = errorMessage;
    }
  } catch (error) {
    console.error('회원가입 중 오류:', error);
    registrationError.value = '네트워크 오류가 발생했습니다. 서버 연결을 확인해주세요.';
  }
}

// 성공 모달 표시
const showSuccessModal = () => {
  const successModal = document.createElement('div')
  successModal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'
  successModal.innerHTML = `
    <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center animate-fadeIn">
      <div class="mb-6">
        <div class="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
          <i class="fas fa-check text-green-500 text-3xl"></i>
        </div>
        <h3 class="text-xl font-bold text-gray-900 mb-2">회원가입 완료</h3>
        <p class="text-gray-600">회원가입이 성공적으로 완료되었습니다.<br>이제 로그인하여 면접 시스템을 이용하실 수 있습니다.</p>
      </div>
      <button class="w-full bg-red-600 text-white py-2 rounded-md font-medium hover:bg-red-700 transition-colors cursor-pointer">
        로그인으로 이동
      </button>
    </div>
  `
  
  // 애니메이션을 위한 스타일 추가
  const style = document.createElement('style')
  style.textContent = `
    @keyframes fadeIn {
      from { opacity: 0; transform: scale(0.9); }
      to { opacity: 1; transform: scale(1); }
    }
    .animate-fadeIn {
      animation: fadeIn 0.3s ease-out;
    }
  `
  document.head.appendChild(style)
  document.body.appendChild(successModal)
  
  // 확인 버튼 클릭 이벤트
  const closeButton = successModal.querySelector('button')
  if (closeButton) {
    closeButton.addEventListener('click', () => {
      document.body.removeChild(successModal)
      document.head.removeChild(style)
      
      // 폼 초기화 및 로그인 화면으로 전환
      registrationForm.value = {
        name: '',
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        department: ''
      }
      showRegistration.value = false
      registrationError.value = ''
      loginError.value = ''
      
      // 로그인 폼도 초기화
      loginForm.value = {
        username: '',
        password: ''
      }
    })
  }
}

// 관리자 로그인 처리
const handleAdminLogin = () => {
  router.push('/admin')
}
</script>

<style scoped>
/* 추가 스타일이 필요한 경우 여기에 작성 */
</style>