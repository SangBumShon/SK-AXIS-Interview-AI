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
      
      <!-- 면접관 환영 문구 추가 -->
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold mb-2 text-gray-800">AI 면접 시스템</h2>
        <div class="mt-4 p-6 bg-gradient-to-r from-red-50 to-orange-50 rounded-xl shadow-lg border-2 border-red-100">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-12 h-12 bg-gradient-to-br from-red-600 to-orange-500 rounded-full flex items-center justify-center shadow-md">
              <i class="fas fa-user text-lg text-white"></i>
            </div>
            <div class="flex-1">
              <h3 class="text-xl font-bold mb-1 tracking-wide">
                <span class="bg-gradient-to-r from-red-600 to-orange-500 bg-clip-text text-transparent">
                  {{ userDisplayName }}님 환영합니다
                </span>
              </h3>
            </div>
          </div>
          <div class="text-center">
            <p class="text-gray-800 text-lg font-medium tracking-wide">
              오늘도 <span class="font-bold text-red-600">SK</span><span class="font-bold text-orange-500">AXIS</span>와 함께
              <br class="hidden sm:block">
              좋은 인재를 찾아보세요
              <i class="fas fa-star text-yellow-400 ml-2 animate-pulse"></i>
            </p>
          </div>
        </div>
      </div>
      
      <div class="text-center mb-6">
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
                <td class="px-4 py-3 text-center text-sm text-gray-700 border-b whitespace-pre-line">{{ schedule.interviewers.join('\n') }}</td>
                <td class="px-4 py-3 text-center text-sm text-gray-700 border-b whitespace-pre-line">{{ getIntervieweeNames(schedule.interviewees) }}</td>
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
      <!-- 버튼 영역을 flex로 배치 -->
      <div class="flex gap-4">
        <button 
          @click="logout"
          class="px-6 py-3 text-gray-600 hover:text-gray-800 transition-colors cursor-pointer flex items-center gap-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          <i class="fas fa-sign-out-alt"></i>
          로그아웃
        </button>
        <button
          class="flex-1 bg-red-600 text-white py-3 rounded-md font-medium hover:bg-red-700 transition-colors !rounded-button whitespace-nowrap cursor-pointer"
          :disabled="!canProceed"
          :class="{
            'opacity-50 cursor-not-allowed': !canProceed,
            'bg-gray-400': !isToday
          }"
          @click="onStartInterview"
        >
          {{ isToday ? '면접 시작하기' : '오늘 날짜의 면접만 시작할 수 있습니다' }}
        </button>
      </div>
      <div class="mt-6 text-center text-xs text-gray-500">
        <p>© 2025 SK AXIS. All rights reserved.</p>
        <p>2025년 6월 16일 최신 기준</p>
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

import AdminLoginModal from './AdminLoginModal.vue';
import { getInterviewSchedules } from '../services/interviewService';

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

// 로그인한 사용자 이름을 가져오는 computed 속성
const userDisplayName = computed(() => {
  return localStorage.getItem('userDisplayName') || '면접관';
});

// API 데이터에서 동적으로 rooms 생성
const rooms = computed(() => {
  if (!schedules.value || !Array.isArray(schedules.value)) {
    return [];
  }
  const uniqueRooms = new Set(schedules.value.map(schedule => schedule.roomName));
  return Array.from(uniqueRooms).map((roomName, index) => ({
    id: `room${index + 1}`,
    name: roomName
  }));
});

// 오늘 날짜와 선택된 날짜가 일치하는지 확인하는 computed 속성
const isToday = computed(() => {
  const today = new Date().toISOString().split('T')[0];
  return selectedDate.value === today;
});

// selectedRoom, selectedTimeSlot, isToday가 모두 true일 때만 canProceed가 true가 되도록 변경
const canProceed = computed(() => {
  return selectedRoom.value && 
         selectedTimeSlot.value && 
         isToday.value && 
         selectedSchedule.value;
});

// props.rooms 대신 rooms.value 사용
const filteredSchedules = computed(() => {
  if (!schedules.value || !Array.isArray(schedules.value)) {
    return [];
  }
  return schedules.value.filter(schedule => 
    schedule.roomName === rooms.value.find(r => r.id === selectedRoom.value)?.name
  );
});

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
    console.log('API Response:', response);
    schedules.value = response.schedules || [];
  } catch (err) {
    error.value = '면접 일정을 불러오는데 실패했습니다.';
    console.error(err);
    schedules.value = []; // 에러 시 빈 배열로 초기화
  } finally {
    loading.value = false;
  }
};

const selectTimeSlot = (schedule: any) => {
  selectedSchedule.value = schedule;
  selectedTimeSlot.value = schedule.timeRange;
};

// 날짜가 변경될 때마다 일정을 다시 불러옵니다
watch(selectedDate, () => {
  fetchSchedules();
});

const onStartInterview = () => {
  if (!canProceed.value || !selectedSchedule.value) return;
  
  console.log('선택된 스케줄:', selectedSchedule.value);
  console.log('전체 스케줄:', schedules.value);
  
  // 면접 일정에서 지원자 정보 추출
  const candidateIds: number[] = [];
  const candidateNames: string[] = [];
  
  // API 응답에서 해당 스케줄의 지원자 정보 찾기
  const scheduleData = schedules.value.find(schedule => 
    schedule.roomName === selectedSchedule.value.roomName &&
    schedule.timeRange === selectedSchedule.value.timeRange
  );
  
  console.log('찾은 스케줄 데이터:', scheduleData);
  
  if (scheduleData && scheduleData.interviewees) {
    scheduleData.interviewees.forEach((interviewee: { name: string; id: number }) => {
      candidateNames.push(interviewee.name);
      candidateIds.push(interviewee.id);
    });
  }
  
  console.log('추출된 지원자 ID:', candidateIds);
  console.log('추출된 지원자 이름:', candidateNames);
  
  // candidateIds가 비어있지 않은지 확인
  if (candidateIds.length === 0) {
    console.error('지원자 정보를 찾을 수 없습니다.');
    alert('지원자 정보를 불러오는 중 오류가 발생했습니다. 다시 시도해주세요.');
    return;
  }
  
  router.push({
    name: 'interview',
    query: {
      roomName: selectedSchedule.value.roomName,
      date: selectedDate.value,
      timeRange: selectedSchedule.value.timeRange,
      interviewers: selectedSchedule.value.interviewers.join(', '),
      interviewerIds: JSON.stringify(selectedSchedule.value.interviewerIds || []),
      candidates: JSON.stringify(candidateNames),
      candidateIds: JSON.stringify(candidateIds)
    }
  });
};

const handleAdminLogin = () => {
  // 로그인 성공 시 관리자 대시보드로 이동
  router.push('/admin');
};

// 로그아웃 함수 추가
const logout = () => {
  // 메인 로그인 페이지로 이동
  router.push('/');
};

// 지원자 이름을 추출하는 함수
const getIntervieweeNames = (interviewees: any[]): string => {
  if (!interviewees || !Array.isArray(interviewees)) {
    return '';
  }
  return interviewees.map((interviewee: any) => interviewee.name || '').join('\n');
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