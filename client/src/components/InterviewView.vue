<!-- 제공된 템플릿 코드를 그대로 사용 -->
<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-white py-12 px-4 sm:px-6 lg:px-8 relative">
    <!-- Admin Settings Button - 면접 시작 전에만 표시 -->
    <div v-if="!hasStarted" class="absolute top-8 right-8">
      <router-link
        to="/admin"
        class="!rounded-button whitespace-nowrap text-gray-600 hover:text-gray-800 transition-duration-200 p-3 bg-white rounded-full shadow-md hover:shadow-lg"
        title="관리자 설정"
      >
        <i class="fas fa-cog text-xl"></i>
      </router-link>
    </div>

    <div v-if="!hasStarted" class="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-lg">
      <!-- Logo -->
      <div class="flex justify-center">
        <div class="w-64 h-32 relative">
          <div class="absolute inset-0 flex items-center justify-center">
            <h1 class="text-4xl font-bold">
              <span class="text-[#E60012]">SK</span>
              <span class="text-[#FF7A00]">AXIS</span>
            </h1>
          </div>
        </div>
      </div>

      <!-- Title -->
      <div class="text-center">
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">AI 면접 시스템</h2>
        <p class="mt-2 text-sm text-gray-600">
          지원자 정보를 입력하고 면접을 시작하세요
        </p>
      </div>

      <!-- Form -->
      <form class="mt-8 space-y-6" @submit.prevent="startInterview">
        <div class="rounded-md shadow-sm space-y-4">
          <div>
            <label for="candidateName" class="block text-sm font-medium text-gray-700 mb-1">지원자 이름</label>
            <input
              id="candidateName"
              v-model="candidateName"
              name="candidateName"
              type="text"
              required
              class="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7A00] focus:border-[#FF7A00] focus:z-10 sm:text-sm"
              placeholder="이름을 입력해주세요"
              :disabled="interviewStarted"
            />
          </div>
          <div>
            <label for="applicationNumber" class="block text-sm font-medium text-gray-700 mb-1">지원 번호</label>
            <input
              id="applicationNumber"
              v-model="applicationNumber"
              name="applicationNumber"
              type="text"
              required
              class="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7A00] focus:border-[#FF7A00] focus:z-10 sm:text-sm"
              placeholder="지원번호를 입력해주세요"
              :disabled="interviewStarted"
            />
          </div>
        </div>
        <div>
          <button
            type="submit"
            class="!rounded-button whitespace-nowrap group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-[#E60012] hover:bg-[#cc0010] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#E60012] transition-all duration-200 cursor-pointer"
            :disabled="!candidateName.trim() || !applicationNumber.trim() || isLoading"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <i class="fas fa-circle-notch fa-spin"></i>
            </span>
            {{ isLoading ? '처리 중...' : '면접 시작하기' }}
          </button>
        </div>
      </form>

      <!-- Footer -->
      <div class="mt-6 text-center text-xs text-gray-500">
        <p>© {{ currentYear }} SK AXIS. All rights reserved.</p>
        <p class="mt-1">{{ todayDate }} 기준</p>
      </div>
    </div>

    <!-- Interview in Progress -->
    <div v-else class="flex-1 flex flex-col w-full bg-white">
      <!-- Candidate Info Bar -->
      <div class="flex justify-between items-center mb-8">
        <div class="flex items-center space-x-4">
          <img 
            src="/src/assets/skaxis_logo.png" 
            alt="SK AXIS 로고" 
            class="h-12 w-auto"
          />
          <div>
            <h2 class="text-2xl font-bold text-gray-800">{{ candidateName }}님과의 면접</h2>
            <p class="text-gray-600">시작 시간: {{ startTime }}</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <span class="flex items-center">
            <span class="h-2 w-2 rounded-full bg-green-500 mr-2"></span>
            <span class="text-sm text-gray-600">연결됨</span>
          </span>
          <span v-if="isRecording" class="flex items-center">
            <span class="h-2 w-2 rounded-full bg-[#E60012] mr-2 animate-pulse"></span>
            <span class="text-sm text-gray-600">녹화 중</span>
          </span>
        </div>
      </div>

      <!-- Questions Section -->
      <div class="flex-1 mb-8">
        <h3 class="text-xl font-semibold mb-4 text-gray-800">면접 질문</h3>
        <div class="space-y-4">
          <div 
            v-for="(question, index) in questions" 
            :key="index"
            class="bg-gray-100/80 p-5 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-300"
          >
            <div class="flex">
              <div class="w-8 h-8 rounded-full bg-[#FF7A00] text-white flex items-center justify-center mr-4">
                {{ index + 1 }}
              </div>
              <div class="flex-1">
                <p class="text-lg text-gray-800">{{ question }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Controls -->
      <div class="flex justify-center space-x-6 mb-8">
        <button 
          v-if="currentQuestionIndex < questions.length"
          @click="nextQuestion" 
          class="!rounded-button whitespace-nowrap bg-[#FF7A00] text-white px-8 py-3 font-semibold cursor-pointer hover:bg-[#e66e00] transition-colors duration-300"
        >
          <i class="fas fa-play-circle mr-2"></i> 면접 시작
        </button>
        <button 
          @click="endInterview" 
          class="!rounded-button whitespace-nowrap border-2 border-[#E60012] text-[#E60012] px-8 py-3 font-semibold cursor-pointer hover:bg-red-50 transition-colors duration-300"
        >
          <i class="fas fa-stop-circle mr-2"></i> 면접 종료
        </button>
      </div>
    </div>

    <!-- Video Feed - 면접 화면에서만 표시 -->
    <div 
      v-if="hasStarted"
      class="fixed bottom-8 right-8 w-80 shadow-lg rounded-lg overflow-hidden border-2 border-[#FF7A00] bg-gray-100"
    >
      <div class="relative">
        <!-- Video Feed or Placeholder -->
        <div v-if="cameraOn" class="relative w-full aspect-video bg-black">
          <img 
            :src="webcamPlaceholder" 
            alt="웹캠 화면" 
            class="w-full h-full object-cover object-top"
          />
          <div class="absolute top-2 right-2 flex items-center space-x-2">
            <span class="flex items-center px-2 py-1 bg-black/50 rounded-full text-white text-xs">
              <i class="fas fa-signal mr-1"></i> 실시간
            </span>
          </div>
        </div>
        <div v-else class="w-full aspect-video bg-gray-200 flex items-center justify-center">
          <i class="fas fa-video-slash text-gray-400 text-4xl"></i>
        </div>

        <!-- Video Controls -->
        <div class="flex justify-between items-center p-3 bg-white">
          <div class="text-sm font-medium">{{ candidateName || '지원자' }}</div>
          <div class="flex space-x-3">
            <button 
              @click="toggleMicrophone" 
              class="!rounded-button whitespace-nowrap w-8 h-8 rounded-full flex items-center justify-center cursor-pointer hover:bg-gray-100"
              :class="micOn ? 'text-[#FF7A00]' : 'text-gray-400'"
              :title="micOn ? '마이크 끄기' : '마이크 켜기'"
            >
              <i :class="micOn ? 'fas fa-microphone' : 'fas fa-microphone-slash'"></i>
            </button>
            <button 
              @click="toggleCamera" 
              class="!rounded-button whitespace-nowrap w-8 h-8 rounded-full flex items-center justify-center cursor-pointer hover:bg-gray-100"
              :class="cameraOn ? 'text-[#FF7A00]' : 'text-gray-400'"
              :title="cameraOn ? '카메라 끄기' : '카메라 켜기'"
            >
              <i :class="cameraOn ? 'fas fa-video' : 'fas fa-video-slash'"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 면접 종료 확인 모달 -->
    <div v-if="showEndConfirmation" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 max-w-md w-full shadow-2xl">
        <!-- 첫 번째 단계: 종료 확인 -->
        <div v-if="!isEnding">
          <h3 class="text-xl font-bold mb-4 text-gray-800">면접을 종료하시겠습니까?</h3>
          <p class="text-gray-600 mb-6">
            면접 세션을 종료하시겠습니까? 모든 녹화 내용이 저장됩니다.
          </p>
          <div class="flex justify-end space-x-4">
            <button 
              @click="showEndConfirmation = false" 
              class="!rounded-button whitespace-nowrap px-6 py-2 border border-gray-300 text-gray-700 cursor-pointer hover:bg-gray-50"
            >
              취소
            </button>
            <button 
              @click="startEndingProcess" 
              class="!rounded-button whitespace-nowrap px-6 py-2 bg-[#E60012] text-white cursor-pointer hover:bg-[#cc0010]"
            >
              면접 종료
            </button>
          </div>
        </div>
        <!-- 두 번째 단계: 평가 중 -->
        <div v-else>
          <h3 class="text-xl font-bold mb-4 text-gray-800">SKAXIS가 평가 중...</h3>
          <p class="text-gray-600 mb-6">
            면접 세션이 종료 중입니다. 모든 녹화 내용이 저장되는 중입니다.
          </p>
          <div class="mb-6">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm text-gray-600">면접 종료 처리 중...</span>
              <span class="text-sm font-medium text-[#FF7A00]">{{ countdown }}초</span>
            </div>
            <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                class="h-full bg-[#FF7A00] rounded-full transition-all duration-1000"
                :style="{ width: `${(10 - countdown) * 10}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// State
const candidateName = ref('');
const applicationNumber = ref('');
const interviewStarted = ref(false);
const hasStarted = ref(false);
const isRecording = ref(false);
const currentQuestionIndex = ref(0);
const showEndConfirmation = ref(false);
const cameraOn = ref(true);
const micOn = ref(true);
const sessionId = ref('');
const startTime = ref('');
const isLoading = ref(false);
const isEnding = ref(false);
const countdown = ref(10);
let countdownInterval: number | null = null;

// Computed properties
const currentYear = computed(() => new Date().getFullYear());
const todayDate = computed(() => {
  const now = new Date();
  return now.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  });
});

// Generate a random session ID
const generateSessionId = () => {
  return 'SK-' + Math.random().toString(36).substring(2, 10).toUpperCase();
};

// Format current date
const currentDate = computed(() => {
  const now = new Date();
  return now.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
});

// Format time
const formatTime = (date: Date) => {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: true 
  });
};

// Sample interview questions
const questions = ref([
  "귀하의 전문 분야와 이 직무와의 연관성에 대해 말씀해 주세요.",
  "SK 그룹에 지원하게 된 동기와 회사에 대해 알고 계신 점을 말씀해 주세요.",
  "이전에 진행했던 도전적인 프로젝트와 그 과정에서 극복한 어려움에 대해 설명해 주세요.",
  "귀하의 전문 분야에서 최신 트렌드와 발전 동향을 어떻게 파악하고 계신가요?",
  "앞으로 3-5년 후의 커리어 목표와 이 직무가 그 목표와 어떻게 연관되는지 말씀해 주세요."
]);

// Webcam placeholder image
const webcamPlaceholder = 'https://readdy.ai/api/search-image?query=professional%20looking%20person%20in%20business%20attire%20sitting%20in%20front%20of%20a%20computer%20for%20a%20video%20interview%2C%20neutral%20expression%2C%20well-lit%20home%20office%20environment%2C%20clean%20background%2C%20professional%20appearance%2C%20high%20quality%20realistic%20photo%2C%20not%20cartoon%20or%20illustration&width=320&height=180&seq=1&orientation=landscape';

// Methods
const startInterview = async () => {
  if (!candidateName.value.trim() || !applicationNumber.value.trim()) return;
  
  try {
    isLoading.value = true;
    
    // TODO: 실제 API 호출 구현
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    interviewStarted.value = true;
    hasStarted.value = true;
    isRecording.value = true;
    sessionId.value = generateSessionId();
    startTime.value = formatTime(new Date());
  } catch (error) {
    console.error('면접 시작 중 오류 발생:', error);
  } finally {
    isLoading.value = false;
  }
};

// Move to next question
const nextQuestion = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++;
  }
};

// End interview confirmation
const endInterview = () => {
  showEndConfirmation.value = true;
};

// 면접 종료 프로세스 시작
const startEndingProcess = () => {
  isEnding.value = true;
  countdown.value = 10;
  
  countdownInterval = window.setInterval(() => {
    countdown.value--;
    
    if (countdown.value <= 0) {
      if (countdownInterval) {
        clearInterval(countdownInterval);
      }
      confirmEndInterview();
    }
  }, 1000);
};

// 면접 종료 확인 메서드 수정
const confirmEndInterview = () => {
  isEnding.value = false;
  if (countdownInterval) {
    clearInterval(countdownInterval);
  }
  interviewStarted.value = false;
  hasStarted.value = false;
  isRecording.value = false;
  showEndConfirmation.value = false;
  
  // Navigate to result page with candidate name
  router.push({
    name: 'result',
    query: {
      candidateName: candidateName.value
    }
  });
  
  // Reset form
  candidateName.value = '';
  applicationNumber.value = '';
  currentQuestionIndex.value = 0;
};

// Toggle camera
const toggleCamera = () => {
  cameraOn.value = !cameraOn.value;
};

// Toggle microphone
const toggleMicrophone = () => {
  micOn.value = !micOn.value;
};

// Initialize
onMounted(() => {
  // Set initial session ID
  sessionId.value = generateSessionId();
});

// 컴포넌트가 언마운트될 때 인터벌 정리
onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval);
  }
});
</script>

<style scoped>
/* Pretendard 폰트 적용 */
:root {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
  background-color: white;
}

/* 전체 배경색 하얀색으로 설정 */
body {
  background-color: white;
}

/* Custom styles for input focus state */
input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(255, 122, 0, 0.2);
}

/* Animation for questions */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.question-enter-active {
  animation: fadeIn 0.5s ease-out;
}

/* Remove number input arrows */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* 전체 텍스트에 Pretendard 폰트 적용 */
* {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}
</style> 