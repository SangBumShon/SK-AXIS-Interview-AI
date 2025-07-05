<template>
  <!-- 면접 일정(캘린더) 뷰 -->
  <div>
    <!-- 캘린더 모달 -->
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 relative">
        <button @click="$emit('close')" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <i class="fas fa-times"></i>
        </button>
        <div class="mb-8">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-gray-900">면접 일정 관리</h2>
            <div class="flex items-center gap-4">
              <button @click="$emit('prevMonth')" class="p-2 hover:bg-gray-100 rounded-full">
                <i class="fas fa-chevron-left"></i>
              </button>
              <h3 class="text-xl font-semibold">{{ currentMonthYear }}</h3>
              <button @click="$emit('nextMonth')" class="p-2 hover:bg-gray-100 rounded-full">
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
          </div>
          <!-- Calendar Grid -->
          <div class="grid grid-cols-7 gap-px bg-gray-200 rounded-lg overflow-hidden">
            <!-- Days of week -->
            <div v-for="day in ['일', '월', '화', '수', '목', '금', '토']" :key="day"
                 class="bg-gray-50 p-4 text-center font-medium text-gray-700">
              {{ day }}
            </div>
            <!-- Calendar days -->
            <div v-for="(day, index) in calendarDays" :key="index"
                 class="bg-white min-h-[100px] p-2 relative"
                 :class="{'bg-gray-50': !day.isCurrentMonth}">
              <div class="flex justify-between items-center mb-2">
                <span :class="{'text-gray-400': !day.isCurrentMonth, 'text-gray-900': day.isCurrentMonth}">
                  {{ day.date }}
                </span>
                <div v-if="day.interviews.length > 0" class="flex items-center gap-1">
                  <span
                    class="text-xs font-medium px-2 py-0.5 rounded-full cursor-pointer select-none"
                    :class="getBadgeColor(day.interviews.length)"
                    @click="openDayModal(day)"
                  >
                    {{ day.interviews.length }}건
                  </span>
                </div>
              </div>
              <!-- Interview slots -->
              <div class="space-y-1">
                <div v-if="day.interviews.length <= 3">
                  <div v-for="interview in day.interviews" :key="interview.id"
                       class="text-xs p-1.5 rounded cursor-pointer truncate flex items-center gap-1"
                       :class="getInterviewClass(interview)"
                       @click="showInterviewDetail(interview)">
                    <i class="fas fa-user-tie text-xs"></i>
                    {{ interview.time }} - {{ interview.candidate }}
                  </div>
                </div>
                <div v-else>
                  <div v-for="interview in day.interviews.slice(0, 2)" :key="interview.id"
                       class="text-xs p-1.5 rounded cursor-pointer truncate flex items-center gap-1"
                       :class="getInterviewClass(interview)"
                       @click="showInterviewDetail(interview)">
                    <i class="fas fa-user-tie text-xs"></i>
                    {{ interview.time }} - {{ interview.candidate }}
                  </div>
                  <div class="text-xs p-1.5 rounded bg-gray-100 text-gray-600 cursor-pointer text-center"
                       @click="openDayModal(day)">
                    + {{ day.interviews.length - 2 }}건 더보기
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Interview Detail Modal은 상위에서 관리 -->
  </div>
  <div v-if="showDayModal && selectedDay" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 relative">
      <button @click="closeDayModal" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
        <i class="fas fa-times"></i>
      </button>
      <h3 class="text-lg font-bold mb-4">{{ selectedDay.date }}일 전체 면접 일정</h3>
      <ul>
        <li v-for="interview in selectedDay.interviews" :key="interview.id" class="mb-2 border-b pb-2 last:border-b-0 last:pb-0">
          <div class="flex flex-col text-sm">
            <span><b>시간:</b> {{ interview.time }}</span>
            <span><b>지원자:</b> {{ interview.candidate }}</span>
            <span><b>면접관:</b> {{ interview.interviewers?.join(', ') }}</span>
            <span><b>면접실:</b> {{ interview.room }}</span>
            <span><b>상태:</b> {{ interview.status }}</span>
            <button class="mt-1 text-blue-600 hover:underline text-xs self-end" @click="showInterviewDetail(interview)">상세보기</button>
          </div>
        </li>
      </ul>
    </div>
  </div>
  <div v-if="selectedInterview" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">면접 상세 정보</h3>
        <button @click="closeInterviewDetail" class="text-gray-400 hover:text-gray-600">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="space-y-4">
        <div>
          <p class="text-sm text-gray-500">날짜 및 시간</p>
          <p class="font-medium">{{ selectedInterview.date }} {{ selectedInterview.time }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">면접실</p>
          <p class="font-medium">{{ selectedInterview.room }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">지원자</p>
          <p class="font-medium">{{ selectedInterview.candidate }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">지원 부서</p>
          <p class="font-medium">{{ selectedInterview.department }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">면접관</p>
          <p class="font-medium">{{ selectedInterview.interviewers?.join(', ') }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">상태</p>
          <span :class="{
            'px-2 py-1 text-xs font-medium rounded-full': true,
            'bg-green-100 text-green-800': selectedInterview.status === 'completed',
            'bg-yellow-100 text-yellow-800': selectedInterview.status === 'pending',
            'bg-blue-100 text-blue-800': selectedInterview.status === 'in_progress'
          }">
            {{ selectedInterview.status }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
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
defineProps<{
  calendarDays: any[];
  currentMonthYear: string;
}>();
const emits = defineEmits([
  'close',
  'prevMonth',
  'nextMonth',
  'showInterviewDetail'
]);
const selectedDay = ref<any|null>(null);
const showDayModal = ref(false);

const selectedInterview = ref<any|null>(null);
function showInterviewDetail(interview: any) {
  selectedInterview.value = interview;
}
function closeInterviewDetail() {
  selectedInterview.value = null;
}

function openDayModal(day: any) {
  selectedDay.value = day;
  showDayModal.value = true;
}
function closeDayModal() {
  showDayModal.value = false;
  selectedDay.value = null;
}
function getInterviewClass(interview: Interview) {
  switch (interview.status) {
    case 'completed': return 'bg-green-100 text-green-800';
    case 'pending': return 'bg-yellow-100 text-yellow-800';
    case 'in_progress': return 'bg-blue-100 text-blue-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}
function getBadgeColor(count: number) {
  if (count >= 6) return 'bg-red-600 text-white';
  if (count >= 3) return 'bg-red-400 text-white';
  if (count >= 1) return 'bg-red-100 text-red-600';
  return 'bg-gray-100 text-gray-400';
}
</script>
<style scoped>
/* Tailwind JIT purge 방지용: 동적 색상 클래스 강제 포함 */
.dummy-tailwind-colors {
  /* bg-red-600 text-white bg-red-400 bg-red-100 text-red-600 bg-gray-100 text-gray-400 */
  background-color: theme('colors.red.600');
  background-color: theme('colors.red.400');
  background-color: theme('colors.red.100');
  background-color: theme('colors.gray.100');
  color: theme('colors.white');
  color: theme('colors.red.600');
  color: theme('colors.gray.400');
}
</style> 