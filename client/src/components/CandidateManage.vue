<template>
  <!-- 지원자 관리 뷰 -->
  <div class="p-8 overflow-visible min-h-0 h-auto">
    <!-- 지원자 관리 헤더 -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900">지원자 관리</h2>
    </div>
    <!-- 필터 및 검색 -->
    <div class="bg-white rounded-lg p-6 mb-6 border border-gray-200">
      <div class="grid grid-cols-4 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">상태</label>
          <select v-model="filters.status" class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm">
            <option value="all">전체</option>
            <option value="면접 예정">면접 예정</option>
            <option value="면접 완료">면접 완료</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">면접 일정</label>
          <input type="date" v-model="filters.interviewDate" class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm">
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">검색</label>
          <div class="relative">
            <input type="text" v-model="filters.search" placeholder="이름 또는 직무 검색" class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm pr-10">
            <i class="fas fa-search absolute right-3 top-2.5 text-gray-400"></i>
          </div>
        </div>
      </div>
    </div>
    <!-- 지원자 목록 테이블 -->
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div class="p-4 border-b border-gray-100 flex justify-between items-center">
        <h2 class="text-lg font-medium text-gray-700">지원자 목록</h2>
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <label for="itemsPerPage" class="text-sm text-gray-500">페이지당</label>
            <select id="itemsPerPage" v-model.number="itemsPerPage" class="px-2 py-1 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option :value="8">8</option>
              <option :value="10">10</option>
              <option :value="15">15</option>
            </select>
            <span class="text-sm text-gray-500">개 보기</span>
          </div>
          <button @click="$emit('addNewCandidate')" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2">
            <i class="fas fa-plus"></i>
            추가
          </button>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이름</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">지원 직무</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">면접 일정</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">면접 시간</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">면접관</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">면접실</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">최종 점수</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">관리</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="candidate in pagedCandidates" :key="candidate.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.name }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.position }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.interviewDate }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.interviewTime || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.interviewers ? candidate.interviewers.join(', ') : '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.room || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="{
                  'px-2 py-1 text-xs font-medium rounded-full': true,
                  'bg-yellow-100 text-yellow-800': candidate.status === '서류 합격',
                  'bg-blue-100 text-blue-800': candidate.status === '면접 예정',
                  'bg-green-100 text-green-800': candidate.status === '최종 합격',
                  'bg-gray-100 text-gray-800': candidate.status === '면접 완료'
                }">{{ candidate.status || '-' }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.score ?? '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <button class="text-blue-600 hover:text-blue-800" @click="$emit('editCandidate', candidate)">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="text-red-600 hover:text-red-800" @click="$emit('deleteCandidate', candidate)">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- 페이지네이션 및 페이지당 개수 선택 UI (테두리 밖) -->
    <div class="relative px-4 pb-4 mt-6">
      <div class="absolute left-0 top-0 flex items-center gap-2">
        <label for="itemsPerPageCandidate" class="text-sm text-gray-500">페이지당</label>
        <select id="itemsPerPageCandidate" v-model.number="itemsPerPage" class="px-2 py-1 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
          <option :value="8">8</option>
          <option :value="10">10</option>
          <option :value="15">15</option>
        </select>
        <span class="text-sm text-gray-500">개 보기</span>
      </div>
      <div class="flex justify-center items-center gap-2 w-full">
        <button @click="goToPage(1)" :disabled="currentPage === 1" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === 1 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-blue-100'">
          <i class="fas fa-angle-double-left"></i>
        </button>
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === 1 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-blue-100'">
          <i class="fas fa-chevron-left"></i>
        </button>
        <span v-for="page in visiblePages" :key="page">
          <button @click="goToPage(page)" :class="page === currentPage ? 'bg-red-500 text-white' : 'bg-white text-gray-700 hover:bg-red-100'" class="px-3 py-1 rounded-full border mx-1 shadow-sm transition-colors duration-150">{{ page }}</button>
        </span>
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages || totalPages === 0" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === totalPages || totalPages === 0 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-blue-100'">
          <i class="fas fa-chevron-right"></i>
        </button>
        <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages || totalPages === 0" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === totalPages || totalPages === 0 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-blue-100'">
          <i class="fas fa-angle-double-right"></i>
        </button>
      </div>
    </div>
    <!-- 적용 버튼: 테두리 안, 오른쪽 정렬 -->
    <div class="flex justify-end mt-4 mb-2">
      <button class="px-6 py-3 bg-orange-500 text-white rounded-lg shadow-lg hover:bg-orange-600 transition-colors">적용</button>
    </div>
    <!-- 지원자 추가/수정/삭제 모달 등은 상위에서 관리/emit으로 처리 -->
  </div>
</template>
<script setup lang="ts">
import { defineProps, defineEmits, computed, ref, watch } from 'vue';
interface Candidate {
  id: number;
  name: string;
  position: string;
  interviewers: string[];
  status: string;
  interviewDate: string;
  score: number | null;
  interviewTime: string;
  room: string;
}
const props = defineProps<{
  candidateList: Candidate[];
  filters: any;
}>();
const emits = defineEmits([
  'addNewCandidate',
  'editCandidate',
  'deleteCandidate'
]);
const filteredCandidates = computed(() => {
  let filtered = [...props.candidateList];
  if (props.filters.status !== 'all') {
    filtered = filtered.filter(c => c.status === props.filters.status);
  }
  if (props.filters.interviewDate) {
    filtered = filtered.filter(c => c.interviewDate === props.filters.interviewDate);
  }
  if (props.filters.search) {
    const search = props.filters.search.toLowerCase();
    filtered = filtered.filter(c =>
      c.name.toLowerCase().includes(search) ||
      c.position.toLowerCase().includes(search)
    );
  }
  return filtered;
});

// 페이징 관련 상태
const itemsPerPage = ref(8);
const currentPage = ref(1);
const pagedCandidates = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return filteredCandidates.value.slice(start, start + itemsPerPage.value);
});
const totalPages = computed(() => Math.ceil(filteredCandidates.value.length / itemsPerPage.value));
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
}
// 페이지당 개수 변경 시 1페이지로 이동
watch(itemsPerPage, () => {
  currentPage.value = 1;
});
// 최대 5개만 보이는 페이지네이션 계산
const visiblePages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  if (total <= 5) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  if (current <= 3) {
    return [1, 2, 3, 4, 5];
  }
  if (current >= total - 2) {
    return [total - 4, total - 3, total - 2, total - 1, total].filter(p => p > 0);
  }
  return [current - 2, current - 1, current, current + 1, current + 2];
});
</script>
<style scoped>
/* 필요한 스타일 */
</style> 