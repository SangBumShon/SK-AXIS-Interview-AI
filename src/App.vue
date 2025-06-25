<template>
  <div class="min-h-screen bg-gray-50">
    <InterviewSetup
      v-if="$route.name === 'setup'"
    />
    <router-view v-else />
  </div>
</template>

<script setup lang="ts">
import InterviewSetup from './components/InterviewSetup.vue';
</script>

<style>
/* 전역 스타일 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 기본 스타일 리셋 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style> 