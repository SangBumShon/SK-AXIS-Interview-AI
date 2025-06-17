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
              <a href="#" @click.prevent="showCalendarView = true" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
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
              <button class="px-4 py-2 text-gray-600 hover:text-gray-800 rounded-lg whitespace-nowrap cursor-pointer flex items-center gap-2">
                <i class="fas fa-info-circle"></i> About
              </button>
              <button class="px-4 py-2 text-gray-600 hover:text-gray-800 rounded-lg whitespace-nowrap cursor-pointer flex items-center gap-2">
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
                <button @click="showDeleteConfirm = true" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2">
                  <i class="fas fa-trash-alt"></i> 전체 삭제
                </button>
                <label class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2">
                  <i class="fas fa-file-upload"></i> 엑셀 업로드
                  <input type="file" accept=".xlsx,.xls" class="hidden" @change="handleExcelUpload">
                </label>
                <button @click="downloadExcel" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2">
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

    <!-- 캘린더 모달 -->
    <div v-if="showCalendarView" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 relative">
        <button @click="showCalendarView = false" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <i class="fas fa-times"></i>
        </button>
        <div class="mb-8">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-gray-900">면접 일정 관리</h2>
            <div class="flex items-center gap-4">
              <button @click="prevMonth" class="p-2 hover:bg-gray-100 rounded-full">
                <i class="fas fa-chevron-left"></i>
              </button>
              <h3 class="text-xl font-semibold">{{ currentMonthYear }}</h3>
              <button @click="nextMonth" class="p-2 hover:bg-gray-100 rounded-full">
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
          </div>
          
          <!-- Calendar Grid -->
          <div class="grid grid-cols-7 gap-px bg-gray-200 rounded-lg overflow-hidden">
            <!-- Days of week -->
            <div v-for="day in ['일', '월', '화', '수', '목', '금', '토']" :key="day"
                 class="bg-gray-50 p-4 text-center font-medium text-gray-700">
              {{ day }}
            </div>
            
            <!-- Calendar days -->
            <div v-for="(day, index) in calendarDays" :key="index"
                 class="bg-white min-h-[100px] p-2 relative"
                 :class="{'bg-gray-50': !day.isCurrentMonth}">
              <div class="flex justify-between items-center mb-2">
                <span :class="{'text-gray-400': !day.isCurrentMonth, 'text-gray-900': day.isCurrentMonth}">
                  {{ day.date }}
                </span>
                <div v-if="day.interviews.length > 0" class="flex items-center gap-1">
                  <span class="text-xs font-medium px-2 py-0.5 bg-red-100 text-red-600 rounded-full">
                    {{ day.interviews.length }}건
                  </span>
                </div>
              </div>
              
              <!-- Interview slots -->
              <div class="space-y-1">
                <div v-if="day.interviews.length <= 3">
                  <div v-for="interview in day.interviews" :key="interview.id"
                       class="text-xs p-1.5 rounded cursor-pointer truncate flex items-center gap-1"
                       :class="getInterviewClass(interview)"
                       @click="showInterviewDetail(interview)">
                    <i class="fas fa-user-tie text-xs"></i>
                    {{ interview.time }} - {{ interview.candidate }}
                  </div>
                </div>
                <div v-else>
                  <div v-for="interview in day.interviews.slice(0, 2)" :key="interview.id"
                       class="text-xs p-1.5 rounded cursor-pointer truncate flex items-center gap-1"
                       :class="getInterviewClass(interview)"
                       @click="showInterviewDetail(interview)">
                    <i class="fas fa-user-tie text-xs"></i>
                    {{ interview.time }} - {{ interview.candidate }}
                  </div>
                  <div class="text-xs p-1.5 rounded bg-gray-100 text-gray-600 cursor-pointer text-center"
                       @click="showInterviewDetail(day.interviews[0])">
                    + {{ day.interviews.length - 2 }}건 더보기
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Interview Detail Modal -->
    <div v-if="selectedInterview" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">면접 상세 정보</h3>
          <button @click="selectedInterview = null" class="text-gray-400 hover:text-gray-600">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-500">날짜 및 시간</p>
            <p class="font-medium">{{ selectedInterview.date }} {{ selectedInterview.time }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">면접실</p>
            <p class="font-medium">{{ selectedInterview.room }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">지원자</p>
            <p class="font-medium">{{ selectedInterview.candidate }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">지원 부서</p>
            <p class="font-medium">{{ selectedInterview.department }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">면접관</p>
            <p class="font-medium">{{ selectedInterview.interviewers.join(', ') }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">상태</p>
            <span :class="{
              'px-2 py-1 text-xs font-medium rounded-full': true,
              'bg-green-100 text-green-800': selectedInterview.status === 'completed',
              'bg-yellow-100 text-yellow-800': selectedInterview.status === 'pending',
              'bg-blue-100 text-blue-800': selectedInterview.status === 'in_progress'
            }">
              {{ getStatusText(selectedInterview.status) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 필터 상태
const filters = ref({
  period: 'all',
  room: 'all',
  status: 'all',
  search: ''
});

// 정렬 설정
const sortConfig = ref({
  key: 'date',
  direction: 'asc' as 'asc' | 'desc'
});

// 테이블 컬럼 정의
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

// 면접 데이터
const interviews = ref([
  {
    id: 1,
    date: '2025-06-16',
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
    date: '2025-06-16',
    time: '10:30 ~ 11:30',
    room: '2호실',
    candidate: '이지은',
    position: '프론트엔드 개발자',
    department: 'IT 개발부',
    interviewers: ['최영희', '정태우', '강미란'],
    status: 'in_progress',
    score: null
  },
  {
    id: 3,
    date: '2025-06-17',
    time: '09:00 ~ 10:00',
    room: '1호실',
    candidate: '박준호',
    position: '백엔드 개발자',
    department: 'IT 개발부',
    interviewers: ['김민수', '이지원', '최영희'],
    status: 'pending',
    score: null
  },
  {
    id: 4,
    date: '2025-06-18',
    time: '14:00 ~ 15:00',
    room: '3호실',
    candidate: '김서연',
    position: 'UI/UX 디자이너',
    department: '디자인팀',
    interviewers: ['박성훈', '강미란', '정태우'],
    status: 'pending',
    score: null
  },
  {
    id: 5,
    date: '2025-06-19',
    time: '11:00 ~ 12:00',
    room: '2호실',
    candidate: '정민우',
    position: '데이터 엔지니어',
    department: '데이터팀',
    interviewers: ['김민수', '최영희', '이지원'],
    status: 'pending',
    score: null
  }
]);

// 모달 상태
const showDeleteConfirm = ref(false);
const showCalendarView = ref(false);
const selectedInterview = ref<any>(null);
const currentDate = ref(new Date());

// 정렬된 면접 목록
const sortedInterviews = computed(() => {
  let filtered = [...interviews.value];

  if (filters.value.period !== 'all') {
    // 날짜 필터링 로직 추가 가능
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

  return filtered.sort((a, b) => {
    const aVal = (a as any)[sortConfig.value.key] || '';
    const bVal = (b as any)[sortConfig.value.key] || '';
    if (aVal < bVal) return sortConfig.value.direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortConfig.value.direction === 'asc' ? 1 : -1;
    return 0;
  });
});

// 현재 월/년 표시
const currentMonthYear = computed(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth() + 1;
  return `${year}년 ${month}월`;
});

// 캘린더 날짜 배열
const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const days: any[] = [];

  // 이전 달 날짜 추가
  const prevMonthDays = firstDay.getDay();
  const prevMonth = new Date(year, month, 0);
  for (let i = prevMonthDays - 1; i >= 0; i--) {
    days.push({
      date: prevMonth.getDate() - i,
      isCurrentMonth: false,
      interviews: []
    });
  }

  // 현재 달 날짜 추가
  for (let date = 1; date <= lastDay.getDate(); date++) {
    const dayStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(date).padStart(2, '0')}`;
    const dayInterviews = interviews.value.filter(interview => interview.date === dayStr);
    days.push({
      date,
      isCurrentMonth: true,
      interviews: dayInterviews
    });
  }

  // 다음 달 날짜 추가
  const remainingDays = 42 - days.length; // 6행 × 7일
  for (let i = 1; i <= remainingDays; i++) {
    days.push({
      date: i,
      isCurrentMonth: false,
      interviews: []
    });
  }

  return days;
});

// 함수들
const emitClose = () => {
  router.push('/');
};

const sortBy = (key: string) => {
  if (sortConfig.value.key === key) {
    sortConfig.value.direction = sortConfig.value.direction === 'asc' ? 'desc' : 'asc';
  } else {
    sortConfig.value.key = key;
    sortConfig.value.direction = 'asc';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed': return '평가 완료';
    case 'pending': return '대기중';
    case 'in_progress': return '진행중';
    default: return status;
  }
};

const viewDetails = (id: number) => {
  const interview = interviews.value.find(i => i.id === id);
  if (interview) {
    selectedInterview.value = interview;
  }
};

const deleteAllInterviews = () => {
  interviews.value = [];
  showDeleteConfirm.value = false;
};

const handleExcelUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    console.log('Excel file uploaded:', file.name);
    // 엑셀 파일 처리 로직 추가
  }
};

const downloadExcel = () => {
  console.log('Excel download requested');
  // 엑셀 다운로드 로직 추가
};

const prevMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1);
};

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1);
};

const getInterviewClass = (interview: any) => {
  switch (interview.status) {
    case 'completed': return 'bg-green-100 text-green-800';
    case 'pending': return 'bg-yellow-100 text-yellow-800';
    case 'in_progress': return 'bg-blue-100 text-blue-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

// 캘린더에서 면접 일정 클릭 시 상세 정보 표시 함수
const showInterviewDetail = (interview: any) => {
  selectedInterview.value = interview;
};

</script>