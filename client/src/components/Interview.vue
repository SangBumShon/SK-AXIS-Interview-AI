<template>
  <div class="fixed inset-0 bg-white z-50 overflow-auto">
    <div class="container mx-auto px-4 py-6">
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-2xl font-bold text-gray-900">면접 진행</h3>
        <button @click="close" class="text-gray-400 hover:text-gray-600 cursor-pointer">
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>
      <div class="bg-gray-50 rounded-lg p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="flex items-center gap-2">
            <i class="fas fa-door-open text-red-600"></i>
            <span class="text-gray-700">면접실: {{ roomName }}</span>
          </div>
          <div class="flex items-center gap-2">
            <i class="fas fa-clock text-red-600"></i>
            <span class="text-gray-700">시간: {{ timeRange }}</span>
          </div>
          <div class="flex items-center gap-2">
            <i class="fas fa-users text-red-600"></i>
            <span class="text-gray-700">면접관: {{ interviewers }}</span>
          </div>
        </div>
      </div>
      <div class="mb-8">
        <!-- 질문 영역 조건부 렌더링 -->
        <div v-if="Object.keys(questionsPerInterviewee).length > 0" class="grid" :class="[candidates.length > 1 ? 'grid-cols-2 gap-6' : 'grid-cols-1']">
          <div v-for="(candidate, index) in candidates" :key="index" class="bg-white rounded-lg shadow-lg p-6">
            <div class="flex justify-between items-center mb-4">
              <h4 class="text-xl font-semibold text-gray-900">{{ candidate }} 님</h4>
              <span class="text-sm text-gray-500">지원자 {{ index + 1 }}</span>
            </div>
            <div class="space-y-4">
              <div v-if="Object.keys(questionsPerInterviewee).length === 0" class="p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center gap-3 mb-2">
                  <i class="fas fa-spinner fa-spin text-red-600"></i>
                  <span class="text-gray-600">질문을 불러오는 중...</span>
                </div>
              </div>
              <div v-else>
                <!-- 각 지원자별 질문만 렌더링 -->
                <div v-for="(question, qIndex) in questionsPerInterviewee[candidateIds[index]]" :key="question.questionId" class="p-4 bg-gray-50 rounded-lg mb-4">
                  <div class="flex items-center gap-3 mb-2">
                    <span class="flex items-center justify-center w-6 h-6 bg-red-600 text-white rounded-full text-sm font-medium">
                      {{ qIndex + 1 }}
                    </span>
                    <h5 class="font-medium text-gray-900">
                      {{ question.type === '공통질문' ? '공통 질문' : '개별 질문' }} {{ qIndex + 1 }}
                    </h5>
                  </div>
                  <p class="text-gray-700 ml-9">{{ question.content }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="flex justify-center space-x-4 mt-8">
          <button
            class="px-8 py-3 rounded-lg font-medium !rounded-button whitespace-nowrap cursor-pointer flex items-center gap-2 transition-colors"
            :class="{
              'bg-green-600 text-white hover:bg-green-700': !isSessionStarted,
              'bg-gray-400 text-gray-200 cursor-not-allowed': isSessionStarted
            }"
            @click="startSession"
            :disabled="isSessionStarted"
          >
            <i class="fas fa-play"></i>
            {{ isSessionStarted ? '면접 진행 중' : '면접 시작' }}
          </button>
          <button
            class="px-8 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium !rounded-button whitespace-nowrap cursor-pointer flex items-center gap-2"
            @click="endSession"
          >
            <i class="fas fa-stop"></i>
            면접 종료
          </button>
          <button
            class="px-8 py-3 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 font-medium !rounded-button whitespace-nowrap cursor-pointer flex items-center gap-2"
            @click="close"
          >
            <i class="fas fa-times"></i>
            취소
          </button>
        </div>
      </div>
    </div>

    <!-- 우측 하단 실시간 캠/분석 오버레이 (480x270픽셀 고정) -->
    <div
      class="fixed bottom-4 right-4 bg-gray-900 rounded-lg overflow-hidden shadow-lg z-50 flex items-center justify-center"
      style="width:480px; aspect-ratio:4/3; pointer-events:none;">
      <PoseMiniWidget 
        ref="poseMiniWidgetRef"
        :intervieweeNames="candidates"
        :intervieweeIds="candidateIds"
        @updateNonverbalData="handleNonverbalData"
        style="width:100%; height:100%;" 
      />
    </div>

    <!-- AI 로딩 모달 -->
    <AiLoadingModal v-if="isAnalyzing" />
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AiLoadingModal from './AiLoadingModal.vue'
import PoseMiniWidget from './PoseMiniWidget.vue'

interface Props {
  roomName: string
  timeRange: string
  interviewers: string
  candidates: string[]
  candidateIds: number[]
  interviewerIds: number[]
}

const props = withDefaults(defineProps<Props>(), {
  roomName: '',
  timeRange: '',
  interviewers: '',
  candidates: () => [],
  candidateIds: () => [],
  interviewerIds: () => []
})

type Emits = {
  (e: 'startSession'): void
  (e: 'endSession'): void
  (e: 'close'): void
}

const emit = defineEmits<Emits>()

const router = useRouter()
const route = useRoute()
const isAnalyzing = ref(false)
const isSessionStarted = ref(false)

// PoseMiniWidget ref 추가
const poseMiniWidgetRef = ref<InstanceType<typeof PoseMiniWidget> | null>(null)

// 비언어적 데이터 저장소
const nonverbalData = ref<Record<number, any>>({})

// 질문 데이터를 저장할 상태
const questionsPerInterviewee = ref<Record<number, any[]>>({})

const interviewId = computed(() => Number(route.query.interview_id))

// PoseMiniWidget으로부터 비언어적 데이터 업데이트
const handleNonverbalData = (data: Record<string, any>) => {
  // string 키를 number로 변환
  const convertedData: Record<number, any> = {}
  Object.entries(data).forEach(([key, value]) => {
    convertedData[Number(key)] = value
  })
  nonverbalData.value = convertedData
}

const startSession = async () => {
  try {
    // isAnalyzing.value = true; // 로딩 모달 제거
    // FastAPI 서버에 면접 시작 요청
    const token = localStorage.getItem('accessToken');
    
    const requestBody = {
      intervieweeIds: props.candidateIds
    };
    
    const response = await fetch('http://3.38.218.18:8080/api/v1/interviews/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify(requestBody)
    })

    if (!response.ok) {
      const contentType = response.headers.get('content-type')
      
      let errorMessage = '면접 시작 실패'
      try {
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } else {
          const text = await response.text()
          errorMessage = `서버 오류 (${response.status}): ${text}`
        }
      } catch (e) {
        errorMessage = `서버 오류 (${response.status})`
      }
      throw new Error(errorMessage)
    }

    // 성공 응답 처리
    const contentType = response.headers.get('content-type')
    
    let result;
    if (contentType && contentType.includes('application/json')) {
      result = await response.json()
    } else {
      const text = await response.text()
      // 텍스트 응답인 경우 기본 구조로 변환
      result = {
        questionsPerInterviewee: {},
        message: text
      }
    }
    
    // 질문 데이터 저장
    questionsPerInterviewee.value = result.questionsPerInterviewee || {}
    isSessionStarted.value = true  // 면접 시작 상태로 변경
    emit('startSession')  // 면접 시작 이벤트 발생

    // === 감지 시작 명령 추가 ===
    if (poseMiniWidgetRef.value) {
      poseMiniWidgetRef.value.startDetection()
    }
  } catch (error: unknown) {
    // isAnalyzing.value = false; // 로딩 모달 제거
    alert('면접 시작 중 오류가 발생했습니다: ' + (error instanceof Error ? error.message : String(error)))
  }
}

const endSession = async () => {
  try {
    isAnalyzing.value = true;
    console.log('면접 종료...', { nonverbalData: nonverbalData.value });

    // PoseMiniWidget 감지 중단
    if (poseMiniWidgetRef.value) {
      poseMiniWidgetRef.value.stopDetection();
    }

    // FastAPI 서버에 면접 종료 요청
    const rawNonverbalData = JSON.parse(JSON.stringify(nonverbalData.value));
    const requestBody = {
      interview_id: interviewId.value,
      data: Object.fromEntries(
        props.candidateIds.map((id) => {
          const data = rawNonverbalData[id] || {
            posture: { upright: 0, leaning: 0, slouching: 0 },
            facial_expression: { smile: 0, neutral: 0, frown: 0, angry: 0 },
            gaze: 0,
            gesture: 0,
            timestamp: Date.now()
          };
          return [id, data];
        })
      )
    };
    console.log('[면접 종료] 전송되는 request body:', requestBody);
            const response = await fetch('http://3.38.218.18:8000/api/v1/interview/end', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const contentType = response.headers.get('content-type');
      let errorMessage = '면접 종료 실패';
      try {
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } else {
          const text = await response.text();
          console.error('서버 응답 (JSON이 아님):', text);
          errorMessage = `서버 오류 (${response.status}): ${text}`;
        }
      } catch (e) {
        console.error('에러 응답 파싱 실패:', e);
        errorMessage = `서버 오류 (${response.status})`;
      }
      throw new Error(errorMessage);
    }

    // === 여기서 폴링 시작 ===
    await pollUntilDone(props.candidateIds);

    // 결과 페이지로 이동
    router.push({
      name: 'result',
      query: {
        candidates: JSON.stringify(props.candidates),
        candidateIds: JSON.stringify(props.candidateIds),
        tab: '0'
      }
    });
  } catch (error) {
    console.error('면접 종료 중 오류:', error);
    alert('면접 종료 중 오류가 발생했습니다: ' + (error instanceof Error ? error.message : String(error)));
  } finally {
    isAnalyzing.value = false;
  }
};

// 폴링 함수 추가
async function pollUntilDone(candidateIds: number[]) {
  const ids = candidateIds.join(',');
  let attempts = 0;
  const maxAttempts = 300; // 최대 5분 대기 (300초)
  
  while (attempts < maxAttempts) {
    try {
      const response = await fetch(`http://3.38.218.18:8000/api/v1/results/statuses?interviewee_ids=${ids}`);
      const statuses: { status: string }[] = await response.json();
      console.log('[pollUntilDone] 현재 status 응답:', statuses);
      const allDone = statuses.every((item: { status: string }) => item.status === 'DONE');
      if (allDone) {
        console.log('[pollUntilDone] 모든 면접자의 status가 DONE입니다.');
        
        // ✅ Spring Boot /complete 엔드포인트 호출 추가
        try {
          const completeResponse = await fetch('/api/v1/interviews/complete', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              intervieweeIds: candidateIds
            })
          });
          
          if (completeResponse.ok) {
            console.log('[pollUntilDone] Spring Boot /complete 호출 성공');
          } else {
            console.error('[pollUntilDone] Spring Boot /complete 호출 실패:', completeResponse.status);
          }
        } catch (error) {
          console.error('[pollUntilDone] Spring Boot /complete 호출 중 오류:', error);
        }
        
        break;
      }
    } catch (e) {
      // 네트워크 오류 등은 무시하고 재시도
    }
    await new Promise(res => setTimeout(res, 1000));
    attempts++;
  }
  
  if (attempts >= maxAttempts) {
    console.warn('[pollUntilDone] 최대 대기 시간을 초과했습니다.');
  }
}

const close = () => {
  router.push('/')
}

// 컴포넌트 마운트 시 자동으로 질문 로드
// onMounted(() => {
//   startSession()
// })
</script>
