<!-- InterviewSetup.vue -->
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
        <p class="text-gray-600">면접 호실과 시간을 선택해주세요</p>
      </div>
      <!-- 날짜 선택 부분 -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">면접 날짜</label>
        <input
          type="date"
          v-model="selectedDate"
          class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
        />
      </div>
      <!-- 면접실 선택 부분 -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">면접 호실</label>
        <div class="relative">
          <div
            @click="toggleRoomDropdown"
            class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500 cursor-pointer text-gray-700 flex justify-between items-center"
          >
            <span v-if="selectedRoom">{{ rooms.find(r => r.id === selectedRoom)?.name }}</span>
            <span v-else class="text-gray-500">면접 호실을 선택해주세요</span>
            <i class="fas fa-chevron-down text-gray-600"></i>
          </div>
          <div v-if="showRoomDropdown" class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg">
            <div
              v-for="room in rooms"
              :key="room.id"
              @click="selectRoom(room.id)"
              class="px-3 py-2 hover:bg-gray-50 cursor-pointer"
            >
              {{ room.name }}
            </div>
          </div>
        </div>
      </div>
      <div class="mb-6" v-if="selectedRoom">
        <label class="block text-sm font-medium text-gray-700 mb-2">면접 일정</label>
        <div v-if="loading" class="text-center py-4">
          <i class="fas fa-spinner fa-spin text-gray-500"></i>
          <span class="ml-2 text-gray-500">일정을 불러오는 중...</span>
        </div>
        <div v-else-if="error" class="text-center py-4 text-red-500">
          {{ error }}
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full bg-white border border-gray-200">
            <thead>
              <tr class="bg-gray-50">
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider border-b">시간</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider border-b">면접관</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider border-b">지원자</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider border-b w-20">선택</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="schedule in filteredSchedules" :key="schedule.timeRange" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-center text-sm text-gray-700 border-b">{{ schedule.timeRange }}</td>
                <td class="px-4 py-3 text-center text-sm text-gray-700 border-b">{{ schedule.interviewers.join(', ') }}</td>
                <td class="px-4 py-3 text-center text-sm text-gray-700 border-b">{{ schedule.interviewees.join(', ') }}</td>
                <td class="px-4 py-3 text-center border-b">
                  <button
                    @click="selectTimeSlot(schedule)"
                    class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                  >
                    선택
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <button
        class="w-full bg-red-600 text-white py-3 rounded-md font-medium hover:bg-red-700 transition-colors !rounded-button whitespace-nowrap cursor-pointer"
        :disabled="!canProceed"
        :class="{
          'opacity-50 cursor-not-allowed': !canProceed,
          'bg-gray-400': !isToday
        }"
        @click="onStartInterview"
      >
        {{ isToday ? '면접 시작하기' : '오늘 날짜의 면접만 시작할 수 있습니다' }}
      </button>
      <div class="mt-6 text-center text-xs text-gray-500">
        <p>© 2025 SK AXIS. All rights reserved.</p>
        <p>2025년 5월 29일 최신 기준</p>
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
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import type { Room, TimeSlot, Person } from '../data/interviewData';
// getPersonById 제거 (사용하지 않음)
import AdminLoginModal from './AdminLoginModal.vue';
import { getInterviewSchedules } from '../services/interviewService';

interface Props {
  rooms: Room[];
  timeSlots: TimeSlot[];
  people: Person[];
}

const props = withDefaults(defineProps<Props>(), {
  rooms: () => [],
  timeSlots: () => [],
  people: () => []
});

const router = useRouter();

const selectedRoom = ref<string>('');
const selectedTimeSlot = ref<string>('');
const showRoomDropdown = ref(false);
const selectedDate = ref<string>(new Date().toISOString().split('T')[0]);
const schedules = ref<any[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const showAdminLogin = ref(false);
const selectedSchedule = ref<any>(null);

// 오늘 날짜와 선택된 날짜가 일치하는지 확인하는 computed 속성 추가
const isToday = computed(() => {
  const today = new Date().toISOString().split('T')[0];
  return selectedDate.value === today;
});

// Remove the unused availableTimeSlots computed property
// const availableTimeSlots = computed(() => {
//   if (!selectedRoom.value || !selectedDate.value) return [];
//   return props.timeSlots.filter(slot => 
//     slot.roomId === selectedRoom.value && 
//     slot.date === selectedDate.value &&
//     slot.candidateIds.length > 0
//   );
// });

const canProceed = computed(() => {
  return selectedRoom.value && 
         selectedTimeSlot.value && 
         isToday.value && 
         selectedSchedule.value; // 선택된 일정이 있는 경우에만 true
});

const filteredSchedules = computed(() =>
  schedules.value.filter(schedule => 
    schedule.roomName === props.rooms.find(r => r.id === selectedRoom.value)?.name
  )
);

const toggleRoomDropdown = () => { showRoomDropdown.value = !showRoomDropdown.value; };
const selectRoom = (roomId: string) => {
  selectedRoom.value = roomId;
  selectedTimeSlot.value = '';
  showRoomDropdown.value = false;
};

const fetchSchedules = async () => {
  if (!selectedDate.value) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    const response = await getInterviewSchedules(selectedDate.value);
    schedules.value = response.schedules;
  } catch (err) {
    error.value = '면접 일정을 불러오는데 실패했습니다.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

// 날짜가 변경될 때마다 일정을 다시 불러옵니다
watch(selectedDate, () => {
  fetchSchedules();
});

const selectTimeSlot = (schedule: any) => {
  selectedSchedule.value = schedule;
  selectedTimeSlot.value = schedule.timeRange;
};

const onStartInterview = () => {
  if (!canProceed.value || !selectedSchedule.value) return;
  
  router.push({
    name: 'interview',
    query: {
      roomName: selectedSchedule.value.roomName,
      date: selectedDate.value,
      timeRange: selectedSchedule.value.timeRange,
      interviewers: selectedSchedule.value.interviewers.join(', '),
      candidates: JSON.stringify(selectedSchedule.value.interviewees),
      candidateIds: JSON.stringify(selectedSchedule.value.interviewees)
    }
  });
};

const handleAdminLogin = () => {
  // 로그인 성공 시 관리자 대시보드로 이동
  router.push('/admin');
};

onMounted(() => {
  fetchSchedules();
  document.addEventListener('click', (event) => {
    const target = event.target as HTMLElement;
    if (!target.closest('.relative') && showRoomDropdown.value) {
      showRoomDropdown.value = false;
    }
  });
});
</script>
