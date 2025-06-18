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
        <div class="grid" :class="[candidates.length > 1 ? 'grid-cols-2 gap-6' : 'grid-cols-1']">
          <div v-for="(candidate, index) in candidates" :key="index" class="bg-white rounded-lg shadow-lg p-6">
            <div class="flex justify-between items-center mb-4">
              <h4 class="text-xl font-semibold text-gray-900">{{ candidate }} 님</h4>
              <span class="text-sm text-gray-500">지원자 {{ index + 1 }}</span>
            </div>
            <div class="space-y-4">
              <div v-for="(question, qIndex) in getQuestionsForCandidate(candidateIds[index] || 0)" :key="question.id" class="p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center gap-3 mb-2">
                  <span class="flex items-center justify-center w-6 h-6 bg-red-600 text-white rounded-full text-sm font-medium">
                    {{ qIndex + 1 }}
                  </span>
                  <h5 class="font-medium text-gray-900">
                    {{ question.type === 'common' ? '공통 질문' : '개별 질문' }} {{ qIndex + 1 }}
                  </h5>
                </div>
                <p class="text-gray-700 ml-9">{{ question.content }}</p>
              </div>
            </div>
          </div>
        </div>
        <div class="flex justify-center space-x-4 mt-8">
          <button
            class="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium !rounded-button whitespace-nowrap cursor-pointer flex items-center gap-2"
            @click="startSession"
          >
            <i class="fas fa-play"></i>
            면접 시작
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
import { ref, defineProps, defineEmits } from 'vue'
import { useRouter } from 'vue-router'
import type { Question } from '../data/questionData'
import { getQuestionsForCandidate as getCandidateQuestions } from '../data/questionData'
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
const isAnalyzing = ref(false)

// 비언어적 데이터 저장소
const nonverbalData = ref<Record<number, any>>({})

const getQuestionsForCandidate = (candidateId: number): Question[] => {
  // candidateId가 유효한지 확인
  if (candidateId === undefined || candidateId === null || isNaN(candidateId)) {
    console.warn(`유효하지 않은 candidateId: ${candidateId}`);
    return getCandidateQuestions(0); // 기본 질문 반환
  }
  return getCandidateQuestions(candidateId)
}

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
    console.log('면접 시작...', { candidateIds: props.candidateIds, interviewerIds: props.interviewerIds })
    isAnalyzing.value = true

    // FastAPI 서버에 면접 시작 요청
    const response = await fetch('/api/v1/interview/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        interviewee_ids: props.candidateIds,
        interviewer_ids: props.interviewerIds
      })
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
          console.error('서버 응답 (JSON이 아님):', text)
          errorMessage = `서버 오류 (${response.status}): ${text}`
        }
      } catch (e) {
        console.error('에러 응답 파싱 실패:', e)
        errorMessage = `서버 오류 (${response.status})`
      }
      
      throw new Error(errorMessage)
    }

    const result = await response.json()
    console.log('면접 시작 성공:', result)
    emit('startSession')  // 면접 시작 이벤트 발생
    isAnalyzing.value = false
  } catch (error: unknown) {
    console.error('면접 시작 중 오류:', error)
    isAnalyzing.value = false
    alert('면접 시작 중 오류가 발생했습니다: ' + (error instanceof Error ? error.message : String(error)))
  }
}

const endSession = async () => {
  try {
    isAnalyzing.value = true
    console.log('면접 종료...', { nonverbalData: nonverbalData.value })

    // FastAPI 서버에 면접 종료 요청
    const response = await fetch('/api/v1/interview/end', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        interview_id: 1,  // 임시 ID
        interviewees: props.candidates.map((_, index) => {  // name 파라미터를 _로 변경
          const id = props.candidateIds[index]
          const data = nonverbalData.value[id] || {
            posture: { upright: 0, leaning: 0, slouching: 0 },
            facial_expression: { smile: 0, neutral: 0, frown: 0, angry: 0 },
            gaze: 0,
            gesture: 0
          }
          return {
            interviewee_id: id,
            posture: data.posture,
            facial_expression: data.facial_expression,
            gaze: data.gaze,
            gesture: data.gesture
          }
        })
      })
    })

    if (!response.ok) {
      const contentType = response.headers.get('content-type')
      let errorMessage = '면접 종료 실패'
      
      try {
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } else {
          const text = await response.text()
          console.error('서버 응답 (JSON이 아님):', text)
          errorMessage = `서버 오류 (${response.status}): ${text}`
        }
      } catch (e) {
        console.error('에러 응답 파싱 실패:', e)
        errorMessage = `서버 오류 (${response.status})`
      }
      
      throw new Error(errorMessage)
    }

    const result = await response.json()
    console.log('면접 종료 성공:', result)
    emit('endSession')  // 면접 종료 이벤트 발생

    // 결과 페이지로 이동
    router.push({
      name: 'result',
      query: {
        candidates: JSON.stringify(props.candidates),
        tab: '0'
      }
    })
  } catch (error: unknown) {
    console.error('면접 종료 중 오류:', error)
    alert('면접 종료 중 오류가 발생했습니다: ' + (error instanceof Error ? error.message : String(error)))
  } finally {
    isAnalyzing.value = false
  }
}

const close = () => {
  router.push('/')
}
</script>
