<template>
  <!-- 통계 분석 모달 -->
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-8 max-w-6xl w-full mx-4 relative animate-fadeIn overflow-auto max-h-[90vh]">
      <button @click="$emit('close')" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
        <i class="fas fa-times"></i>
      </button>
      <div class="mb-8">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">면접 통계 분석</h2>
          <div class="flex items-center gap-4">
            <div class="relative">
              <select v-model="statisticsFilter.period" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500">
                <option value="all">전체 기간</option>
                <option value="month">이번 달</option>
                <option value="quarter">이번 분기</option>
                <option value="year">올해</option>
              </select>
            </div>
          </div>
        </div>
        <!-- Statistics Dashboard -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- 직무별 면접 현황 -->
          <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-800">직무별 면접 현황</h3>
            <div class="h-80" ref="jobChartRef"></div>
          </div>
          <!-- 면접자 점수 분포 -->
          <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-800">면접자 점수 분포</h3>
            <div class="h-80" ref="scoreDistributionChartRef"></div>
          </div>
          <!-- 역량별 평균 면접 점수 -->
          <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-800">역량별 평균 면접 점수</h3>
            <div class="h-80" ref="avgScoreChartRef"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
defineProps<{
  statisticsFilter: any;
}>();
const emits = defineEmits(['close']);
</script>
<style scoped>
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fadeIn {
  animation: fadeIn 0.3s ease-in-out;
}
</style> 