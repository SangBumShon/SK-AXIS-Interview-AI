<template>
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center relative overflow-hidden">
        <div class="mb-6">
          <div class="w-24 h-24 mx-auto mb-6">
            <i class="fas fa-circle-notch fa-spin text-red-600 text-5xl"></i>
          </div>
          <h3 class="text-2xl font-bold mb-3">
            <span class="text-red-600">SK</span><span class="text-orange-500">AXIS</span>가
            <span class="text-gray-900">면접 결과를 분석 중입니다...</span>
          </h3>
          <p class="text-gray-600 text-lg">AI가 면접 내용을 평가하고 있습니다</p>
        </div>
        <div class="w-full bg-gray-200 h-3 rounded-full overflow-hidden">
          <div class="loading-progress bg-gradient-to-r from-red-600 to-orange-500 h-full rounded-full"></div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  // 아무 props/state 필요 없음(타이머 등은 부모가 관리)
  </script>
  
  <style scoped>
  @keyframes loading {
    0% { width: 0; }
    100% { width: 100%; }
  }
  .loading-progress {
    animation: loading 10s linear forwards;
  }
  </style>
  