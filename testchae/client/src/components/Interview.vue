<!-- Interview.vue -->
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
                <div v-for="(question, qIndex) in getQuestionsForCandidate(candidateIds[index])" :key="question.id" class="p-4 bg-gray-50 rounded-lg">
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
      <!-- Webcam container -->
      <div class="fixed bottom-4 right-4 w-64 h-48 bg-gray-900 rounded-lg overflow-hidden shadow-lg">
        <video ref="webcamRef" class="w-full h-full object-cover"></video>
        <div class="absolute bottom-2 right-2">
          <button @click="toggleWebcam" class="text-white bg-red-600 px-2 py-1 rounded text-sm cursor-pointer">
            <i class="fas fa-video"></i>
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted } from 'vue';
  import type { Question } from '../data/questionData';
  import { getQuestionsForCandidate as getCandidateQuestions } from '../data/questionData';
  
  interface Props {
    roomName: string;
    timeRange: string;
    interviewers: string;
    candidates: string[];
    candidateIds: string[];
  }
  
  const props = withDefaults(defineProps<Props>(), {
    roomName: '',
    timeRange: '',
    interviewers: '',
    candidates: () => [],
    candidateIds: () => []
  });
  
  const emit = defineEmits<{
    (e: 'close'): void;
    (e: 'startSession'): void;
    (e: 'endSession'): void;
    (e: 'toggleWebcam'): void;
  }>();
  
  const webcamRef = ref<HTMLVideoElement | null>(null);
  const webcamStream = ref<MediaStream | null>(null);
  
  const getQuestionsForCandidate = (candidateId: string): Question[] => {
    return getCandidateQuestions(candidateId);
  };
  
  const startSession = () => {
    emit('startSession');
  };
  
  const endSession = () => {
    emit('endSession');
  };
  
  const close = () => {
    if (webcamStream.value) {
      webcamStream.value.getTracks().forEach(track => track.stop());
      webcamStream.value = null;
    }
    emit('close');
  };
  
  const setupWebcam = () => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        webcamStream.value = stream;
        if (webcamRef.value) {
          webcamRef.value.srcObject = stream;
          webcamRef.value.play();
        }
      })
      .catch(err => console.log('웹캠 접근 오류:', err));
  };
  
  const toggleWebcam = () => {
    emit('toggleWebcam');
    if (webcamRef.value) {
      if (webcamRef.value.paused) {
        webcamRef.value.play();
      } else {
        webcamRef.value.pause();
      }
    }
  };
  
  onMounted(() => {
    setupWebcam();
  });
  </script>
  