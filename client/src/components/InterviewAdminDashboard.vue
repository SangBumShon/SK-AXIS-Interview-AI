<template>
  <div class="min-h-screen flex bg-white">
    <!-- Sidebar -->
    <aside class="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="p-4 border-b border-gray-200">
          <h1 class="text-2xl font-bold">
            <span class="text-[#E60012]">SK</span>
            <span class="text-[#FF7A00]">AXIS</span>
          </h1>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 p-4 space-y-1">
          <router-link to="/admin" class="flex items-center px-4 py-2 text-[#FF7A00] bg-orange-50 rounded-lg">
            <i class="fas fa-chart-line w-5"></i>
            <span class="ml-3">대시보드</span>
          </router-link>
          <router-link to="/admin/interviews" class="flex items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
            <i class="fas fa-video w-5"></i>
            <span class="ml-3">면접 관리</span>
          </router-link>
          <router-link to="/admin/candidates" class="flex items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
            <i class="fas fa-users w-5"></i>
            <span class="ml-3">지원자 관리</span>
          </router-link>
          <router-link to="/admin/schedule" class="flex items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
            <i class="fas fa-calendar-alt w-5"></i>
            <span class="ml-3">일정 관리</span>
          </router-link>
          <router-link to="/admin/interviewers" class="flex items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
            <i class="fas fa-user-tie w-5"></i>
            <span class="ml-3">면접관 관리</span>
          </router-link>
          <router-link to="/admin/reports" class="flex items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
            <i class="fas fa-file-alt w-5"></i>
            <span class="ml-3">보고서</span>
          </router-link>
          <router-link to="/admin/settings" class="flex items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
            <i class="fas fa-cog w-5"></i>
            <span class="ml-3">설정</span>
          </router-link>
        </nav>

        <!-- User Info -->
        <div class="p-4 border-t border-gray-200">
          <div class="flex items-center">
            <div class="w-8 h-8 rounded-full bg-[#FF7A00] text-white flex items-center justify-center">
              <i class="fas fa-user"></i>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-gray-900">관리자</p>
              <p class="text-xs text-gray-500">admin@skaxis.com</p>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="ml-64 p-8 flex-1 bg-white">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">면접 관리 대시보드</h1>
          <p class="text-gray-600 mt-1">면접 현황 및 통계</p>
        </div>
        <div class="flex space-x-4">
          <button class="!rounded-button whitespace-nowrap px-4 py-2 bg-[#FF7A00] text-white hover:bg-[#e66e00]">
            <i class="fas fa-plus mr-2"></i>새 면접 등록
          </button>
          <button class="!rounded-button whitespace-nowrap px-4 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50">
            <i class="fas fa-download mr-2"></i>엑셀 다운로드
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center">
              <i class="fas fa-video text-blue-500 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm text-gray-600">오늘의 면접</p>
              <p class="text-2xl font-semibold text-gray-900">12</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="w-12 h-12 rounded-full bg-green-50 flex items-center justify-center">
              <i class="fas fa-check-circle text-green-500 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm text-gray-600">완료된 면접</p>
              <p class="text-2xl font-semibold text-gray-900">45</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="w-12 h-12 rounded-full bg-yellow-50 flex items-center justify-center">
              <i class="fas fa-clock text-yellow-500 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm text-gray-600">대기 중</p>
              <p class="text-2xl font-semibold text-gray-900">8</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div class="w-12 h-12 rounded-full bg-purple-50 flex items-center justify-center">
              <i class="fas fa-user-tie text-purple-500 text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm text-gray-600">활동 면접관</p>
              <p class="text-2xl font-semibold text-gray-900">6</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Interview List -->
      <div class="bg-white rounded-lg shadow-sm">
        <!-- Filters -->
        <div class="p-6 border-b border-gray-200">
          <div class="flex flex-wrap gap-4">
            <div class="flex-1 min-w-[200px]">
              <label class="block text-sm font-medium text-gray-700 mb-1">상태</label>
              <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7A00]">
                <option value="">전체</option>
                <option value="scheduled">예정</option>
                <option value="in-progress">진행 중</option>
                <option value="completed">완료</option>
                <option value="cancelled">취소</option>
              </select>
            </div>
            <div class="flex-1 min-w-[200px]">
              <label class="block text-sm font-medium text-gray-700 mb-1">직무</label>
              <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7A00]">
                <option value="">전체</option>
                <option value="developer">개발자</option>
                <option value="designer">디자이너</option>
                <option value="pm">PM</option>
                <option value="marketing">마케팅</option>
              </select>
            </div>
            <div class="flex-1 min-w-[200px]">
              <label class="block text-sm font-medium text-gray-700 mb-1">날짜</label>
              <input type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7A00]">
            </div>
            <div class="flex-1 min-w-[200px]">
              <label class="block text-sm font-medium text-gray-700 mb-1">면접관</label>
              <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7A00]">
                <option value="">전체</option>
                <option value="1">김면접</option>
                <option value="2">이평가</option>
                <option value="3">박관리</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Table -->
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">지원자</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">직무</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">날짜</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">상태</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">점수</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">면접관</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">작업</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="interview in interviews" :key="interview.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                      <i class="fas fa-user text-gray-500"></i>
                    </div>
                    <div class="ml-3">
                      <p class="text-sm font-medium text-gray-900">{{ interview.candidate }}</p>
                      <p class="text-xs text-gray-500">{{ interview.applicationNumber }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ interview.position }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ interview.date }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusClass(interview.status)" class="px-2 py-1 text-xs font-medium rounded-full">
                    {{ getStatusText(interview.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ interview.score || '-' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ interview.interviewer }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                  <button class="text-[#FF7A00] hover:text-[#E60012] mr-3">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="text-gray-600 hover:text-gray-900">
                    <i class="fas fa-ellipsis-v"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="px-6 py-4 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-700">
              총 <span class="font-medium">120</span>건 중 <span class="font-medium">1</span> - <span class="font-medium">10</span>건 표시
            </div>
            <div class="flex space-x-2">
              <button class="!rounded-button whitespace-nowrap px-3 py-1 border border-gray-300 text-gray-700 hover:bg-gray-50">
                이전
              </button>
              <button class="!rounded-button whitespace-nowrap px-3 py-1 bg-[#FF7A00] text-white">
                1
              </button>
              <button class="!rounded-button whitespace-nowrap px-3 py-1 border border-gray-300 text-gray-700 hover:bg-gray-50">
                2
              </button>
              <button class="!rounded-button whitespace-nowrap px-3 py-1 border border-gray-300 text-gray-700 hover:bg-gray-50">
                3
              </button>
              <button class="!rounded-button whitespace-nowrap px-3 py-1 border border-gray-300 text-gray-700 hover:bg-gray-50">
                다음
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

// Sample data
const interviews = ref([
  {
    id: 1,
    candidate: '홍길동',
    applicationNumber: 'APP-001',
    position: '시니어 개발자',
    date: '2024-03-15 14:00',
    status: 'completed',
    score: 85,
    interviewer: '김면접'
  },
  {
    id: 2,
    candidate: '김철수',
    applicationNumber: 'APP-002',
    position: 'UX 디자이너',
    date: '2024-03-15 15:30',
    status: 'in-progress',
    score: null,
    interviewer: '이평가'
  },
  {
    id: 3,
    candidate: '이영희',
    applicationNumber: 'APP-003',
    position: '프로젝트 매니저',
    date: '2024-03-16 10:00',
    status: 'scheduled',
    score: null,
    interviewer: '박관리'
  }
]);

// Helper functions
const getStatusClass = (status: string) => {
  const classes = {
    'scheduled': 'bg-blue-100 text-blue-800',
    'in-progress': 'bg-yellow-100 text-yellow-800',
    'completed': 'bg-green-100 text-green-800',
    'cancelled': 'bg-red-100 text-red-800'
  };
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800';
};

const getStatusText = (status: string) => {
  const texts = {
    'scheduled': '예정',
    'in-progress': '진행 중',
    'completed': '완료',
    'cancelled': '취소'
  };
  return texts[status as keyof typeof texts] || status;
};
</script>

<style scoped>
/* Pretendard 폰트 적용 */
:root {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
  background-color: white;
}

/* 전체 배경색 하얀색으로 설정 */
body {
  background-color: white;
}

/* 전체 텍스트에 Pretendard 폰트 적용 */
* {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}

/* Custom styles for select elements */
select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

/* Hide number input arrows */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style> 