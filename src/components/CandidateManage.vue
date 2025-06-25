<template>
  <!-- 지원자 관리 뷰 -->
  <div class="p-8">
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
            <tr v-for="candidate in filteredCandidates" :key="candidate.id" class="hover:bg-gray-50">
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
    <!-- 지원자 추가/수정/삭제 모달 등은 상위에서 관리/emit으로 처리 -->
  </div>
</template>
<script setup lang="ts">
import { defineProps, defineEmits, computed } from 'vue';
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
</script>
<style scoped>
/* 필요한 스타일 */
</style> 