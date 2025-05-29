<!-- InterviewSetup.vue -->
<template>
    <div class="min-h-screen bg-white flex justify-center items-center relative">
      <button class="absolute top-4 right-4 text-gray-600 hover:text-gray-800 transition-colors cursor-pointer">
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
          <div class="overflow-x-auto">
            <table class="min-w-full bg-white border border-gray-200">
              <thead>
                <tr class="bg-gray-50">
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider border-b">시간</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider border-b">면접관</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider border-b">지원자</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider border-b w-20">선택</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="timeSlot in availableTimeSlots"
                    :key="timeSlot.id"
                    class="hover:bg-gray-50 cursor-pointer transition-colors"
                    :class="{'bg-red-50': selectedTimeSlot === timeSlot.id}"
                    @click="selectedTimeSlot = timeSlot.id">
                  <td class="px-4 py-3 text-sm text-gray-900 whitespace-nowrap text-center">{{ timeSlot.timeRange }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">
                    <div class="flex flex-col items-center space-y-1">
                      <div v-for="interviewerId in timeSlot.interviewerIds" :key="interviewerId" class="text-center">
                        {{ getPersonById(interviewerId)?.name }}
                      </div>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">
                    <div class="flex flex-col items-center space-y-1">
                      <div v-for="candidateId in timeSlot.candidateIds" :key="candidateId" class="text-center">
                        {{ getPersonById(candidateId)?.name }}
                      </div>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-center">
                    <div class="w-5 h-5 rounded-full border inline-flex items-center justify-center mx-auto"
                         :class="selectedTimeSlot === timeSlot.id ? 'border-red-500 bg-red-500' : 'border-gray-300'">
                      <i v-if="selectedTimeSlot === timeSlot.id" class="fas fa-check text-white text-xs"></i>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <button
          class="w-full bg-red-600 text-white py-3 rounded-md font-medium hover:bg-red-700 transition-colors !rounded-button whitespace-nowrap cursor-pointer"
          :disabled="!canProceed"
          :class="{'opacity-50 cursor-not-allowed': !canProceed}"
          @click="onStartInterview"
        >
          면접 시작하기
        </button>
        <div class="mt-6 text-center text-xs text-gray-500">
          <p>© 2025 SK AXIS. All rights reserved.</p>
          <p>2025년 5월 29일 최신 기준</p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import type { Room, TimeSlot, Person } from '../data/interviewData';
  import { getPersonById } from '../data/interviewData';
  
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
  
  const availableTimeSlots = computed(() => {
    if (!selectedRoom.value) return [];
    return props.timeSlots.filter(slot => 
      slot.roomId === selectedRoom.value && 
      slot.candidateIds.length > 0
    );
  });
  
  const canProceed = computed(() => {
    return selectedRoom.value && selectedTimeSlot.value;
  });
  
  const toggleRoomDropdown = () => { showRoomDropdown.value = !showRoomDropdown.value; };
  const selectRoom = (roomId: string) => {
    selectedRoom.value = roomId;
    selectedTimeSlot.value = '';
    showRoomDropdown.value = false;
  };
  
  const onStartInterview = () => {
    if (!canProceed.value) return;
    const timeSlot = availableTimeSlots.value.find(t => t.id === selectedTimeSlot.value);
    if (!timeSlot) return;
    
    const roomName = props.rooms.find(r => r.id === selectedRoom.value)?.name || '';
    
    router.push({
      name: 'interview',
      query: {
        roomName,
        timeRange: timeSlot.timeRange,
        interviewers: timeSlot.interviewerIds.map(id => getPersonById(id)?.name).join(', '),
        candidates: JSON.stringify(timeSlot.candidateIds.map(id => getPersonById(id)?.name)),
        candidateIds: JSON.stringify(timeSlot.candidateIds)
      }
    });
  };
  
  onMounted(() => {
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.relative') && showRoomDropdown.value) {
        showRoomDropdown.value = false;
      }
    });
  });
  </script>
  