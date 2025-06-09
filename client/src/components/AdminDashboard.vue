<template>
    <div class="fixed inset-0 bg-white z-50 overflow-auto">
      <div class="flex h-full">
        <!-- 사이드바 -->
        <div class="w-64 bg-white border-r border-gray-200 h-full shadow-sm flex flex-col justify-between">
          <div>
            <div class="p-6">
              <div class="flex items-center gap-2 mb-8">
                <h1 class="text-2xl font-bold">
                  <span class="text-red-600">SK</span><span class="text-orange-500">AXIS</span>
                </h1>
              </div>
              <nav class="space-y-1">
                <a href="#" class="flex items-center px-4 py-3 text-gray-900 bg-gray-100 rounded-lg">
                  <i class="fas fa-tachometer-alt w-5 text-red-600"></i>
                  <span class="ml-3 font-medium">대시보드</span>
                </a>
                <a href="#" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <i class="fas fa-users w-5 text-gray-500"></i>
                  <span class="ml-3">지원자 관리</span>
                </a>
                <a href="#" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <i class="fas fa-calendar-alt w-5 text-gray-500"></i>
                  <span class="ml-3">면접 일정</span>
                </a>
                <a href="#" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <i class="fas fa-chart-bar w-5 text-gray-500"></i>
                  <span class="ml-3">통계 분석</span>
                </a>
                <a href="#" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <i class="fas fa-cog w-5 text-gray-500"></i>
                  <span class="ml-3">시스템 설정</span>
                </a>
              </nav>
            </div>
          </div>
          <div class="p-6 border-t border-gray-200">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                <i class="fas fa-user text-gray-500"></i>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900">관리자</p>
                <p class="text-xs text-gray-500">admin@skaxis.com</p>
              </div>
            </div>
          </div>
        </div>
        <!-- 메인 콘텐츠 -->
        <div class="flex-1 overflow-auto">
          <div class="container mx-auto px-6 py-8">
            <!-- 헤더 -->
            <div class="flex justify-between items-center mb-6 border-b border-gray-200 pb-4">
              <div class="flex items-center gap-6">
                <span class="text-xl text-gray-700 font-bold">관리자 대시보드</span>
              </div>
              <div class="flex items-center gap-4">
                <button class="px-4 py-2 text-gray-600 hover:text-gray-800 !rounded-button whitespace-nowrap cursor-pointer flex items-center gap-2">
                  <i class="fas fa-info-circle"></i> About
                </button>
                <button class="px-4 py-2 text-gray-600 hover:text-gray-800 !rounded-button whitespace-nowrap cursor-pointer flex items-center gap-2">
                  <i class="fas fa-headset"></i> 개발자 문의
                </button>
                <button @click="emitClose" class="text-gray-400 hover:text-gray-600">
                  <i class="fas fa-times text-2xl"></i>
                </button>
              </div>
            </div>
            <!-- 통계 대시보드 -->
            <div class="grid grid-cols-4 gap-6 mb-8">
              <div class="bg-white rounded-lg p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex items-center gap-4 mb-4">
                  <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-users text-blue-600 text-2xl"></i>
                  </div>
                  <div>
                    <h3 class="text-lg font-medium text-gray-700">전체 지원자</h3>
                    <p class="text-3xl font-semibold text-gray-900">128</p>
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
                  <button @click="showDeleteConfirm = true" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors !rounded-button whitespace-nowrap cursor-pointer flex items-center gap-2">
                    <i class="fas fa-trash-alt"></i> 전체 삭제
                  </button>
                  <label class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors !rounded-button whitespace-nowrap cursor-pointer flex items-center gap-2">
                    <i class="fas fa-file-upload"></i> 엑셀 업로드
                    <input type="file" accept=".xlsx,.xls" class="hidden" @change="handleExcelUpload">
                  </label>
                  <button @click="downloadExcel" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors !rounded-button whitespace-nowrap cursor-pointer flex items-center gap-2">
                    <i class="fas fa-file-download"></i> 엑셀 다운로드
                  </button>
                </div>
              </div>
              <div class="overflow-x-auto">
                <table class="min-w-full">
                  <thead class="bg-gray-50">
                    <tr>
                      <th v-for="column in tableColumns" :key="column.key"
                          @click="sortBy(column.key)"
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
                        <button @click="viewDetails(interview.id)" class="text-red-600 hover:text-red-800">
                          <i class="fas fa-eye"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div> <!-- container -->
        </div>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold text-gray-900 mb-4">전체 삭제 확인</h3>
        <p class="text-gray-600 mb-6">모든 면접자 데이터를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.</p>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteConfirm = false" class="px-4 py-2 text-gray-600 hover:text-gray-800">
            취소
          </button>
          <button @click="deleteAllInterviews" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
            삭제
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, computed } from 'vue';
  import { useRouter } from 'vue-router';
  const router = useRouter();
  const filters = ref({
    period: 'all',
    room: 'all',
    status: 'all',
    search: ''
  });
  const sortConfig = ref({
    key: 'date',
    direction: 'asc'
  });
  const tableColumns = [
    { key: 'date', label: '날짜' },
    { key: 'time', label: '시간' },
    { key: 'room', label: '면접실' },
    { key: 'candidate', label: '지원자' },
    { key: 'position', label: '지원 직무' },
    { key: 'department', label: '지원 부서' },
    { key: 'interviewers', label: '면접관' },
    { key: 'status', label: '상태' },
    { key: 'score', label: '점수' },
    { key: 'actions', label: '상세보기' }
  ];
  const interviews = ref([
    {
      id: 1,
      date: '2025-05-29',
      time: '09:00 ~ 10:00',
      room: '1호실',
      candidate: '홍길동',
      position: '소프트웨어 엔지니어',
      department: 'IT 개발부',
      interviewers: ['김민수', '이지원', '박성훈'],
      status: 'completed',
      score: 92
    },
    {
      id: 2,
      date: '2025-05-29',
      time: '10:30 ~ 11:30',
      room: '1호실',
      candidate: '이지은',
      position: '프론트엔드 개발자',
      department: 'IT 개발부',
      interviewers: ['최영희', '정태우', '강미란'],
      status: 'in_progress',
      score: null
    },
    // ...추가 데이터는 실제 상황에 맞게 넣으세요
  ]);
  const sortedInterviews = computed(() => {
    let filtered = [...interviews.value];
    // Apply filters
    if (filters.value.period !== 'all') {
      // Add date filtering logic if needed
    }
    if (filters.value.room !== 'all') {
      filtered = filtered.filter(i => i.room === filters.value.room);
    }
    if (filters.value.status !== 'all') {
      filtered = filtered.filter(i => i.status === filters.value.status);
    }
    if (filters.value.search) {
      const search = filters.value.search.toLowerCase();
      filtered = filtered.filter(i =>
        i.candidate.toLowerCase().includes(search) ||
        i.department.toLowerCase().includes(search)
      );
    }
    // Apply sorting
    return filtered.sort((a, b) => {
      const aVal = a[sortConfig.value.key as keyof typeof a] || '';
      const bVal = b[sortConfig.value.key as keyof typeof b] || '';
      if (aVal < bVal) return sortConfig.value.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.value.direction === 'asc' ? 1 : -1;
      return 0;
    });
  });
  const emitClose = () => {
    router.push('/'); // 첫 화면으로 이동
  };
  function sortBy(key: string) {
    if (sortConfig.value.key === key) {
      sortConfig.value.direction = sortConfig.value.direction === 'asc' ? 'desc' : 'asc';
    } else {
      sortConfig.value.key = key;
      sortConfig.value.direction = 'asc';
    }
  }
  function getStatusText(status: string) {
    switch (status) {
      case 'completed': return '평가 완료';
      case 'pending': return '대기중';
      case 'in_progress': return '진행중';
      default: return status;
    }
  }
  function viewDetails(id: number) {
    // 상세보기 팝업 등 추가 구현 가능
    alert('면접 상세보기: ' + id);
  }
  function handleExcelUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];
      // 실제 업로드 구현 필요
      alert('엑셀 업로드: ' + file.name);
      input.value = '';
    }
  }
  function downloadExcel() {
    // 실제 다운로드 구현 필요
    alert('엑셀 다운로드');
  }
  const showDeleteConfirm = ref(false);

  // 전체 삭제 함수
  function deleteAllInterviews() {
    // TODO: API 호출하여 전체 데이터 삭제
    showDeleteConfirm.value = false;
    // 삭제 후 목록 새로고침
    // refreshInterviews();
  }
  </script>
  
  <style scoped>
  /* 관리자 대시보드에 맞는 스타일만 남기세요 */
  </style>
  