<template>
  <!-- 면접 일정(캘린더) 뷰 -->
  <div>
    <!-- 캘린더 모달 -->
    <div class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-6xl mx-4 relative animate-slideUp overflow-hidden max-h-[95vh]">
        <!-- 헤더 -->
        <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-8 text-white relative overflow-hidden">
          <!-- 배경 패턴 -->
          <div class="absolute inset-0 opacity-10">
            <div class="absolute top-4 right-4 w-32 h-32 border border-white rounded-full"></div>
            <div class="absolute bottom-4 left-4 w-24 h-24 border border-white rounded-full"></div>
            <div class="absolute top-1/2 left-1/3 w-16 h-16 border border-white rounded-full"></div>
          </div>
          
          <div class="relative z-10 flex justify-between items-center">
            <div class="flex items-center gap-4">
              <div class="w-16 h-16 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                <i class="fas fa-calendar-alt text-3xl"></i>
              </div>
              <div>
                <h2 class="text-3xl font-bold mb-2">면접 일정 관리</h2>
                <p class="text-white text-opacity-90">월별 면접 일정을 한눈에 확인하세요</p>
              </div>
            </div>
            
            <div class="flex items-center gap-4">
              <!-- 월 네비게이션 -->
              <div class="bg-white bg-opacity-20 backdrop-blur-sm rounded-xl p-2 flex items-center gap-2">
                <button @click="$emit('prevMonth')" 
                        class="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center hover:bg-opacity-30 transition-all duration-200">
                  <i class="fas fa-chevron-left"></i>
                </button>
                <h3 class="text-xl font-semibold px-4 min-w-[140px] text-center">{{ currentMonthYear }}</h3>
                <button @click="$emit('nextMonth')" 
                        class="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center hover:bg-opacity-30 transition-all duration-200">
                  <i class="fas fa-chevron-right"></i>
                </button>
              </div>
              
              <!-- 닫기 버튼 -->
              <button @click="$emit('close')" 
                      class="w-12 h-12 bg-white bg-opacity-20 backdrop-blur-sm rounded-xl flex items-center justify-center hover:bg-opacity-30 transition-all duration-200 group">
                <i class="fas fa-times text-xl group-hover:rotate-90 transition-transform duration-200"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- 캘린더 내용 -->
        <div class="p-8 overflow-y-auto max-h-[calc(95vh-180px)] bg-gradient-to-br from-gray-50 to-white">
          <div class="overflow-x-auto">
            <div class="grid grid-cols-7 gap-2 bg-white rounded-2xl shadow-lg p-6 min-w-[700px]">
              <!-- 요일 헤더 -->
              <div v-for="(day, index) in ['일', '월', '화', '수', '목', '금', '토']" :key="day"
                   class="p-4 text-center font-bold text-gray-700 rounded-xl"
                   :class="{
                     'text-red-500': index === 0,
                     'text-blue-500': index === 6,
                     'bg-gray-50': true
                   }">
                {{ day }}
              </div>
              
              <!-- 캘린더 날짜들 -->
              <div v-for="(day, index) in visibleDays" :key="index"
                   class="relative h-[140px] rounded-xl border-2 transition-all duration-200 hover:shadow-lg group cursor-pointer"
                   :class="{
                     'bg-white border-gray-100': day.isCurrentMonth,
                     'bg-gray-50 border-gray-50': !day.isCurrentMonth,
                     'hover:border-blue-200': day.isCurrentMonth,
                     'hover:bg-blue-50': day.isCurrentMonth && day.interviews.length > 0
                   }"
                   @click="day.isCurrentMonth && day.interviews.length > 0 ? openDayModal(day) : null">
                
                <div v-if="day.isCurrentMonth" class="p-3 h-full flex flex-col">
                  <!-- 날짜 및 배지 -->
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-lg font-semibold text-gray-900">{{ day.date }}</span>
                    <div v-if="day.interviews.length > 0" class="flex items-center gap-1">
                      <span class="text-xs font-bold px-2 py-1 rounded-full cursor-pointer select-none transition-all duration-200 hover:scale-110"
                            :class="getBadgeColor(day.interviews.length)"
                            @click.stop="openDayModal(day)">
                        {{ day.interviews.length }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- 면접 일정 리스트 -->
                  <div class="space-y-1 flex-1 overflow-hidden">
                    <div v-if="day.interviews.length <= 3">
                      <div v-for="interview in day.interviews" :key="interview.id"
                           class="text-xs p-2 rounded-lg cursor-pointer truncate flex items-center gap-1.5 transition-all duration-200 hover:scale-[1.02] hover:shadow-md"
                           :class="getInterviewClass(interview)"
                           @click.stop="showInterviewDetail(interview)">
                        <i class="fas fa-user-tie text-xs"></i>
                        <span class="font-medium">{{ interview.time }}</span>
                        <span>{{ interview.candidate }}</span>
                      </div>
                    </div>
                    <div v-else>
                      <div v-for="interview in day.interviews.slice(0, 2)" :key="interview.id"
                           class="text-xs p-2 rounded-lg cursor-pointer truncate flex items-center gap-1.5 transition-all duration-200 hover:scale-[1.02] hover:shadow-md"
                           :class="getInterviewClass(interview)"
                           @click.stop="showInterviewDetail(interview)">
                        <i class="fas fa-user-tie text-xs"></i>
                        <span class="font-medium">{{ interview.time }}</span>
                        <span>{{ interview.candidate }}</span>
                      </div>
                      <div class="text-xs p-2 rounded-lg bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 cursor-pointer text-center font-medium transition-all duration-200 hover:from-blue-100 hover:to-blue-200 hover:text-blue-700"
                           @click.stop="openDayModal(day)">
                        <i class="fas fa-plus-circle mr-1"></i>
                        {{ day.interviews.length - 2 }}건 더보기
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 다른 달 날짜 -->
                <div v-else class="p-3">
                  <span class="text-gray-400 font-medium">{{ day.date }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 일별 상세 모달 -->
    <div v-if="showDayModal && selectedDay" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-60 p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full mx-4 relative animate-slideUp overflow-hidden max-h-[90vh]">
        <!-- 일별 모달 헤더 -->
        <div class="bg-gradient-to-r from-indigo-500 to-purple-600 p-6 text-white">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
                <i class="fas fa-calendar-day text-xl"></i>
              </div>
              <div>
                <h3 class="text-2xl font-bold">{{ selectedDay.date }}일 면접 일정</h3>
                <p class="text-white text-opacity-90">총 {{ selectedDay.interviews.length }}건의 면접</p>
              </div>
            </div>
            <button @click="closeDayModal" 
                    class="w-10 h-10 bg-white bg-opacity-20 rounded-xl flex items-center justify-center hover:bg-opacity-30 transition-all duration-200 group">
              <i class="fas fa-times group-hover:rotate-90 transition-transform duration-200"></i>
            </button>
          </div>
        </div>
        
        <!-- 일별 모달 내용 -->
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div class="space-y-4">
            <div v-for="interview in selectedDay.interviews" :key="interview.id" 
                 class="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-lg transition-all duration-200 cursor-pointer group"
                 @click="showInterviewDetail(interview)">
              <div class="flex justify-between items-start mb-3">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                    <i class="fas fa-user-tie text-blue-600"></i>
                  </div>
                  <div>
                    <h4 class="font-bold text-gray-900 group-hover:text-blue-600 transition-colors">{{ interview.candidate }}</h4>
                    <p class="text-sm text-gray-500">{{ interview.department }}</p>
                  </div>
                </div>
                <span class="text-lg font-bold text-gray-900">{{ interview.time }}</span>
              </div>
              
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">면접관:</span>
                  <span class="ml-2 font-medium">{{ interview.interviewers?.join(', ') }}</span>
                </div>
                <div>
                  <span class="text-gray-500">면접실:</span>
                  <span class="ml-2 font-medium">{{ interview.room }}</span>
                </div>
              </div>
              
              <div class="flex justify-between items-center mt-3">
                <span class="text-xs font-medium px-3 py-1 rounded-full"
                      :class="getStatusClass(interview.status)">
                  {{ getStatusText(interview.status) }}
                </span>
                <i class="fas fa-chevron-right text-gray-400 group-hover:text-blue-500 transition-colors"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 면접 상세 정보 모달 -->
    <div v-if="selectedInterview" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-70 p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 relative animate-slideUp overflow-hidden">
        <!-- 상세 모달 헤더 -->
        <div class="bg-gradient-to-r from-emerald-500 to-teal-600 p-6 text-white">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
                <i class="fas fa-info-circle text-xl"></i>
              </div>
              <div>
                <h3 class="text-xl font-bold">면접 상세 정보</h3>
                <p class="text-white text-opacity-90">{{ selectedInterview.candidate }}</p>
              </div>
            </div>
            <button @click="closeInterviewDetail" 
                    class="w-10 h-10 bg-white bg-opacity-20 rounded-xl flex items-center justify-center hover:bg-opacity-30 transition-all duration-200 group">
              <i class="fas fa-times group-hover:rotate-90 transition-transform duration-200"></i>
            </button>
          </div>
        </div>
        
        <!-- 상세 모달 내용 -->
        <div class="p-6">
          <div class="space-y-5">
            <div class="bg-gray-50 rounded-xl p-4">
              <p class="text-sm text-gray-500 mb-1">날짜 및 시간</p>
              <p class="text-lg font-bold text-gray-900 flex items-center gap-2">
                <i class="fas fa-clock text-blue-500"></i>
                {{ selectedInterview.date }} {{ selectedInterview.time }}
              </p>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-blue-50 rounded-xl p-4">
                <p class="text-sm text-blue-600 mb-1">면접실</p>
                <p class="font-bold text-gray-900">{{ selectedInterview.room }}</p>
              </div>
              <div class="bg-purple-50 rounded-xl p-4">
                <p class="text-sm text-purple-600 mb-1">지원 부서</p>
                <p class="font-bold text-gray-900">{{ selectedInterview.department }}</p>
              </div>
            </div>
            
            <div class="bg-green-50 rounded-xl p-4">
              <p class="text-sm text-green-600 mb-2">면접관</p>
              <div class="flex flex-wrap gap-2">
                <span v-for="interviewer in selectedInterview.interviewers" :key="interviewer"
                      class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                  {{ interviewer }}
                </span>
              </div>
            </div>
            
            <div class="bg-yellow-50 rounded-xl p-4">
              <p class="text-sm text-yellow-600 mb-2">상태</p>
              <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-bold"
                    :class="getStatusClass(selectedInterview.status)">
                <i :class="getStatusIcon(selectedInterview.status)"></i>
                {{ getStatusText(selectedInterview.status) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { defineProps, defineEmits } from 'vue';

interface Interview {
  id: number;
  date: string;
  time: string;
  room: string;
  candidate: string;
  position: string;
  department: string;
  interviewers: string[];
  status: string;
  score: number | null;
}

interface CalendarDay {
  date: number;
  isCurrentMonth: boolean;
  interviews: Interview[];
}

const props = defineProps<{
  calendarDays: CalendarDay[];
  currentMonthYear: string;
}>();

const emits = defineEmits([
  'close',
  'prevMonth',
  'nextMonth',
  'showInterviewDetail'
]);

const selectedDay = ref<CalendarDay | null>(null);
const showDayModal = ref(false);
const selectedInterview = ref<Interview | null>(null);

function showInterviewDetail(interview: Interview) {
  selectedInterview.value = interview;
}

function closeInterviewDetail() {
  selectedInterview.value = null;
}

function openDayModal(day: CalendarDay) {
  selectedDay.value = day;
  showDayModal.value = true;
}

function closeDayModal() {
  showDayModal.value = false;
  selectedDay.value = null;
}

function getInterviewClass(interview: Interview) {
  switch (interview.status) {
    case 'completed': return 'bg-green-100 text-green-800 border border-green-200';
    case 'pending': return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
    case 'in_progress': return 'bg-blue-100 text-blue-800 border border-blue-200';
    default: return 'bg-gray-100 text-gray-800 border border-gray-200';
  }
}

function getStatusClass(status: string) {
  switch (status) {
    case 'completed': return 'bg-green-100 text-green-800';
    case 'pending': return 'bg-yellow-100 text-yellow-800';
    case 'in_progress': return 'bg-blue-100 text-blue-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'completed': return '완료';
    case 'pending': return '대기중';
    case 'in_progress': return '진행중';
    default: return '미정';
  }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'completed': return 'fas fa-check-circle';
    case 'pending': return 'fas fa-clock';
    case 'in_progress': return 'fas fa-play-circle';
    default: return 'fas fa-question-circle';
  }
}

function getBadgeColor(count: number) {
  if (count >= 6) return 'bg-red-500 text-white shadow-lg';
  if (count >= 3) return 'bg-orange-400 text-white shadow-md';
  if (count >= 1) return 'bg-blue-400 text-white shadow-sm';
  return 'bg-gray-100 text-gray-400';
}

// calendarDays를 주 단위(7개씩)로 쪼개는 computed
const weeks = computed(() => {
  const days = [...props.calendarDays];
  const result = [];
  for (let i = 0; i < days.length; i += 7) {
    result.push(days.slice(i, i + 7));
  }
  // 마지막 주가 모두 다음 달이면 제거
  while (result.length && result[result.length - 1].every(day => !day.isCurrentMonth)) {
    result.pop();
  }
  return result;
});

const visibleDays = computed(() => weeks.value.flat());
</script>

<style scoped>
/* 애니메이션 */
@keyframes slideUp {
  from { 
    opacity: 0; 
    transform: translateY(30px) scale(0.95); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0) scale(1); 
  }
}

.animate-slideUp {
  animation: slideUp 0.4s ease-out;
}

/* 호버 효과 */
.hover\:scale-\[1\.02\]:hover {
  transform: scale(1.02);
}

/* 스크롤바 스타일링 */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #2563eb, #5b21b6);
}

/* 그라데이션 배경 */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}

/* z-index 커스텀 */
.z-60 {
  z-index: 60;
}

.z-70 {
  z-index: 70;
}

/* Tailwind JIT purge 방지용 */
.dummy-tailwind-colors {
  background-color: theme('colors.red.500');
  background-color: theme('colors.orange.400');
  background-color: theme('colors.blue.400');
  background-color: theme('colors.gray.100');
  color: theme('colors.white');
  color: theme('colors.gray.400');
}
</style>