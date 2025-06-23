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
                  <span class="text-xs font-medium px-2 py-0.5 bg-red-100 text-red-600 rounded-full">
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
                       @click="$emit('showInterviewDetail', interview)">
                    <i class="fas fa-user-tie text-xs"></i>
                    {{ interview.time }} - {{ interview.candidate }}
                  </div>
                </div>
                <div v-else>
                  <div v-for="interview in day.interviews.slice(0, 2)" :key="interview.id"
                       class="text-xs p-1.5 rounded cursor-pointer truncate flex items-center gap-1"
                       :class="getInterviewClass(interview)"
                       @click="$emit('showInterviewDetail', interview)">
                    <i class="fas fa-user-tie text-xs"></i>
                    {{ interview.time }} - {{ interview.candidate }}
                  </div>
                  <div class="text-xs p-1.5 rounded bg-gray-100 text-gray-600 cursor-pointer text-center"
                       @click="$emit('showInterviewDetail', day.interviews[0])">
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
</template>
<script setup lang="ts">
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
function getInterviewClass(interview: Interview) {
  switch (interview.status) {
    case 'completed': return 'bg-green-100 text-green-800';
    case 'pending': return 'bg-yellow-100 text-yellow-800';
    case 'in_progress': return 'bg-blue-100 text-blue-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}
</script>
<style scoped>
/* 필요한 스타일 */
</style> 