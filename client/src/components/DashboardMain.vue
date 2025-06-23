<template>
  <!-- 대시보드 뷰 -->
  <div class="container mx-auto px-6 py-8">
    <!-- 헤더 -->
    <div class="flex justify-between items-center mb-6 border-b border-gray-200 pb-4">
      <div class="flex items-center gap-6">
        <span class="text-xl text-gray-700 font-bold">관리자 대시보드</span>
      </div>
      <div class="flex items-center gap-4">
        <button class="px-4 py-2 text-gray-600 hover:text-gray-800 rounded-lg whitespace-nowrap cursor-pointer flex items-center gap-2">
          <i class="fas fa-info-circle"></i> About
        </button>
        <button class="px-4 py-2 text-gray-600 hover:text-gray-800 rounded-lg whitespace-nowrap cursor-pointer flex items-center gap-2">
          <i class="fas fa-headset"></i> 개발자 문의
        </button>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <i class="fas fa-times text-2xl"></i>
        </button>
      </div>
    </div>
    <!-- 통계 카드 -->
    <div class="grid grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
            <i class="fas fa-users text-blue-600 text-2xl"></i>
          </div>
          <div>
            <h3 class="text-lg font-medium text-gray-700">전체 지원자</h3>
            <p class="text-3xl font-semibold text-gray-900">{{ candidateList.length }}</p>
          </div>
        </div>
        <p class="text-sm text-gray-500 flex items-center gap-1">
          전월 대비 <span class="text-blue-600 font-medium flex items-center"><i class="fas fa-caret-up text-xs"></i>15%</span>
        </p>
      </div>
      <div class="bg-white rounded-lg p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
            <i class="fas fa-calendar-day text-green-600 text-2xl"></i>
          </div>
          <div>
            <h3 class="text-lg font-medium text-gray-700">오늘의 면접</h3>
            <p class="text-3xl font-semibold text-gray-900">12</p>
          </div>
        </div>
        <p class="text-sm text-gray-500 flex items-center gap-1">
          전일 대비 <span class="text-green-600 font-medium flex items-center"><i class="fas fa-caret-up text-xs"></i>2</span>
        </p>
      </div>
      <div class="bg-white rounded-lg p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
            <i class="fas fa-check-circle text-purple-600 text-2xl"></i>
          </div>
          <div>
            <h3 class="text-lg font-medium text-gray-700">완료된 면접</h3>
            <p class="text-3xl font-semibold text-gray-900">75</p>
          </div>
        </div>
        <p class="text-sm text-gray-500">전체 면접 대비 58%</p>
      </div>
      <div class="bg-white rounded-lg p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
            <i class="fas fa-clock text-orange-600 text-2xl"></i>
          </div>
          <div>
            <h3 class="text-lg font-medium text-gray-700">대기중</h3>
            <p class="text-3xl font-semibold text-gray-900">45</p>
          </div>
        </div>
        <p class="text-sm text-gray-500">전체 면접 대비 35%</p>
      </div>
    </div>
    <!-- 필터 섹션 -->
    <div class="bg-white rounded-lg p-6 mb-8 border border-gray-100">
      <div class="grid grid-cols-4 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-2">면접 기간</label>
          <select v-model="filters.period" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-gray-400">
            <option value="all">전체 기간</option>
            <option value="today">오늘</option>
            <option value="week">이번 주</option>
            <option value="month">이번 달</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">면접실</label>
          <select v-model="filters.room" class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500">
            <option value="all">전체</option>
            <option value="room1">1호실</option>
            <option value="room2">2호실</option>
            <option value="room3">3호실</option>
            <option value="room4">4호실</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">평가 상태</label>
          <select v-model="filters.status" class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500">
            <option value="all">전체</option>
            <option value="completed">평가 완료</option>
            <option value="pending">대기중</option>
            <option value="in_progress">진행중</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">검색</label>
          <div class="relative">
            <input type="text" v-model="filters.search" placeholder="이름 또는 부서 검색" class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500">
            <i class="fas fa-search absolute right-3 top-2.5 text-gray-400"></i>
          </div>
        </div>
      </div>
    </div>
    <!-- 테이블 섹션 -->
    <div class="bg-white rounded-lg border border-gray-100 overflow-hidden mb-8">
      <div class="p-4 border-b border-gray-100 flex justify-between items-center">
        <h2 class="text-lg font-medium text-gray-700">면접자 목록</h2>
        <div class="flex items-center gap-3">
          <button @click="$emit('showDeleteConfirm')" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2">
            <i class="fas fa-trash-alt"></i> 전체 삭제
          </button>
          <label class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2">
            <i class="fas fa-file-upload"></i> 엑셀 업로드
            <input type="file" accept=".xlsx,.xls" class="hidden" @change="$emit('handleExcelUpload', $event)">
          </label>
          <button @click="$emit('downloadExcel')" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2">
            <i class="fas fa-file-download"></i> 엑셀 다운로드
          </button>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gray-50">
            <tr>
              <th v-for="column in tableColumns" :key="column.key"
                  @click="$emit('sortBy', column.key)"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                {{ column.label }} <i class="fas fa-sort ml-1"></i>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="interview in sortedInterviews" :key="interview.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">{{ interview.date }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ interview.time }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ interview.room }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ interview.candidate }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ interview.position }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ interview.department }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ interview.interviewers.join(', ') }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="{
                  'px-2 py-1 text-xs font-medium rounded-full': true,
                  'bg-green-100 text-green-800': interview.status === 'completed',
                  'bg-yellow-100 text-yellow-800': interview.status === 'pending',
                  'bg-blue-100 text-blue-800': interview.status === 'in_progress'
                }">
                  {{ getStatusText(interview.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">{{ interview.score || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button @click="$emit('viewDetails', interview.id)" class="text-red-600 hover:text-red-800">
                  <i class="fas fa-eye"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
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
interface TableColumn {
  key: string;
  label: string;
}
defineProps<{
  candidateList: any[];
  filters: any;
  tableColumns: TableColumn[];
  sortedInterviews: Interview[];
}>();
const emits = defineEmits([
  'close',
  'showDeleteConfirm',
  'handleExcelUpload',
  'downloadExcel',
  'sortBy',
  'viewDetails'
]);
function getStatusText(status: string) {
  switch (status) {
    case 'completed': return '평가 완료';
    case 'pending': return '대기중';
    case 'in_progress': return '진행중';
    default: return status;
  }
}
</script>
<style scoped>
/* 필요한 스타일 */
</style> 