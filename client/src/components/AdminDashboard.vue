<!-- DashboardMain.vue 수정 사항:

1. updateFilter 함수 수정 - 전체 filters 객체를 올바르게 emit
2. 검색 범위 확장 - 더 많은 필드에서 검색 가능
3. 디버깅을 위한 콘솔 로그 추가

DashboardMain.vue의 updateFilter 함수를 다음과 같이 수정하세요:

```javascript
// 필터 업데이트 함수 수정
function updateFilter(key: string, value: string) {
  const newFilters = { ...props.filters, [key]: value };
  console.log('Filter updated:', key, value, newFilters); // 디버깅용
  emits('updateFilters', newFilters);
}
```

AdminDashboard.vue -->
<template>
  <div class="bg-white z-50 min-h-screen">
    <div class="flex min-h-screen">
      <!-- 사이드바: 항상 고정 -->
      <div class="w-64 bg-white border-r border-gray-200 h-screen shadow-sm flex flex-col justify-between fixed left-0 top-0 z-40">
        <div>
          <div class="p-6">
            <div class="flex items-center gap-2 mb-8">
              <h1 class="text-2xl font-bold">
                <span class="text-red-600">SK</span><span class="text-orange-500">AXIS</span>
              </h1>
            </div>
            <nav class="space-y-1">
              <a href="#" @click.prevent="setActiveView('dashboard')" 
                 :class="activeView === 'dashboard' ? 'text-gray-900 bg-gray-100' : 'text-gray-600 hover:bg-gray-50'"
                 class="flex items-center px-4 py-3 rounded-lg">
                <i class="fas fa-tachometer-alt w-5" :class="activeView === 'dashboard' ? 'text-red-600' : 'text-gray-500'"></i>
                <span class="ml-3" :class="activeView === 'dashboard' ? 'font-medium' : ''">대시보드</span>
              </a>
              <a href="#" @click.prevent="setActiveView('candidates')"
                 :class="activeView === 'candidates' ? 'text-gray-900 bg-gray-100' : 'text-gray-600 hover:bg-gray-50'"
                 class="flex items-center px-4 py-3 rounded-lg">
                <i class="fas fa-users w-5" :class="activeView === 'candidates' ? 'text-red-600' : 'text-gray-500'"></i>
                <span class="ml-3" :class="activeView === 'candidates' ? 'font-medium' : ''">지원자 관리</span>
              </a>
              <a href="#" @click.prevent="showCalendarView = true" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                <i class="fas fa-calendar-alt w-5 text-gray-500"></i>
                <span class="ml-3">면접 일정</span>
              </a>
              <a href="#" @click.prevent="showStatistics" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                <i class="fas fa-chart-bar w-5 text-gray-500"></i>
                <span class="ml-3">통계 분석</span>
              </a>
              <a href="#" @click.prevent="setActiveView('system-settings')"
                 :class="activeView === 'system-settings' ? 'text-gray-900 bg-gray-100' : 'text-gray-600 hover:bg-gray-50'"
                 class="flex items-center px-4 py-3 rounded-lg">
                <i class="fas fa-cog w-5" :class="activeView === 'system-settings' ? 'text-red-600' : 'text-gray-500'"></i>
                <span class="ml-3" :class="activeView === 'system-settings' ? 'font-medium' : ''">시스템 설정</span>
              </a>
            </nav>
          </div>
        </div>
        <div class="p-6 border-t border-gray-200">
          <div class="flex flex-col gap-3">
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
      </div>
      
      <!-- 메인 콘텐츠: 사이드바 오른쪽에 위치, 스크롤 가능 -->
      <div class="flex-1 ml-64">
        <DashboardMain
          v-if="activeView === 'dashboard'"
          :candidateList="candidateList"
          :filters="filters"
          :tableColumns="tableColumns"
          :sortedInterviews="sortedInterviews"
          @updateFilters="updateFilters"
          @close="emitClose"
        />
        <CandidateManage
          v-if="activeView === 'candidates'"
        />
        <InterviewCalendar
          v-if="showCalendarView"
          :calendarDays="calendarDays"
          :currentMonthYear="currentMonthYear"
          @close="showCalendarView = false"
          @prevMonth="prevMonth"
          @nextMonth="nextMonth"
        />
        <StatisticsModal
          v-if="showStatisticsView"
          :statisticsFilter="statisticsFilter"
          @close="showStatisticsView = false"
        />
        <SystemSettings
          v-if="activeView === 'system-settings'"
          @close="setActiveView('dashboard')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import DashboardMain from './DashboardMain.vue';
import CandidateManage from './CandidateManage.vue';
import InterviewCalendar from './InterviewCalendar.vue';
import StatisticsModal from './StatisticsModal.vue';
import SystemSettings from './SystemSettings.vue';

const router = useRouter();

// 활성 뷰 상태
const activeView = ref('dashboard');

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
  { key: 'interviewers', label: '면접관' },
  { key: 'status', label: '상태' },
  { key: 'score', label: '점수' },
  { key: 'actions', label: '상세보기' }
];

// 면접 데이터
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
const interviews = ref<Interview[]>([]);

// 지원자 목록 데이터
interface Candidate {
  id: number;
  name: string;
  position: string;
  department?: string;
  interviewers: string[];
  status: string;
  interviewDate: string;
  score: number | null;
  interviewTime: string;
  room: string;
}
const candidateList = ref<Candidate[]>([]);

// 모달 상태
const showCalendarView = ref(false);
const currentDate = ref(new Date());
const showStatisticsView = ref(false);
const statisticsFilter = ref({
  period: 'all'
});

// 뷰 변경 함수
const setActiveView = (view: string) => {
  activeView.value = view;
};

// 필터 업데이트 함수 수정
const updateFilters = (newFilters: typeof filters.value) => {
  filters.value = { ...newFilters };
};

// 정렬된 면접 목록 - 필터링 로직 개선
const sortedInterviews = computed(() => {
  let filtered = [...interviews.value];

  // 기간 필터
  if (filters.value.period !== 'all') {
    const today = new Date();
    const pad = (n: number) => n.toString().padStart(2, '0');
    if (filters.value.period === 'today') {
      const todayStr = `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`;
      filtered = filtered.filter(i => i.date === todayStr);
    } else if (filters.value.period === 'week') {
      const startOfWeek = new Date(today);
      startOfWeek.setHours(0,0,0,0);
      startOfWeek.setDate(today.getDate() - today.getDay());
      const endOfWeek = new Date(startOfWeek);
      endOfWeek.setDate(startOfWeek.getDate() + 6);
      endOfWeek.setHours(23,59,59,999);
      filtered = filtered.filter(i => {
        const [y, m, d] = i.date.split('-').map(Number);
        const dateObj = new Date(y, m - 1, d);
        return dateObj >= startOfWeek && dateObj <= endOfWeek;
      });
    } else if (filters.value.period === 'month') {
      const year = today.getFullYear();
      const month = today.getMonth() + 1;
      filtered = filtered.filter(i => {
        const [y, m] = i.date.split('-').map(Number);
        return y === year && m === month;
      });
    }
  }

  // 면접실 필터
  if (filters.value.room !== 'all') {
    filtered = filtered.filter(i => i.room === filters.value.room);
  }

  // 상태 필터
  if (filters.value.status !== 'all') {
    filtered = filtered.filter(i => i.status === filters.value.status);
  }

  // 검색 필터 - 개선된 로직
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase();
    filtered = filtered.filter(i =>
      i.candidate.toLowerCase().includes(search) ||
      (i.department && i.department.toLowerCase().includes(search)) ||
      (i.position && i.position.toLowerCase().includes(search)) ||
      i.room.toLowerCase().includes(search) ||
      i.interviewers.some((interviewer: string) => interviewer.toLowerCase().includes(search))
    );
  }

  // 정렬
  return filtered.sort((a, b) => {
    const key = sortConfig.value.key as keyof Interview;
    const aVal = a[key] ?? '';
    const bVal = b[key] ?? '';
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
interface CalendarDay {
  date: number;
  isCurrentMonth: boolean;
  interviews: Interview[];
}
const calendarDays = computed<CalendarDay[]>(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const days: CalendarDay[] = [];

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
    const dayInterviews = interviews.value.filter((interview: Interview) => interview.date === dayStr);
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

const prevMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1);
};

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1);
};

// 사이드바 통계 분석 링크 클릭 이벤트 핸들러
const showStatistics = () => {
  showStatisticsView.value = true;
};

onMounted(async () => {
  try {
    const response = await fetch('http://3.38.218.18:8080/api/v1/interviewees/simple');
    if (!response.ok) throw new Error('서버 오류');
    const result = await response.json();
    interviews.value = result.data.map((item: Record<string, any>): Interview => {
      let date = '';
      let time = '';
      if (item.startAt) {
        const startAtStr = item.startAt.replace(/Z$/, '');
        const dateObj = new Date(startAtStr);
        date = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`;
        time = `${String(dateObj.getHours()).padStart(2, '0')}:${String(dateObj.getMinutes()).padStart(2, '0')}`;
      }
      return {
        id: item.intervieweeId,
        date,
        time,
        room: item.roomNo || '',
        candidate: item.name || '',
        position: item.position || '',
        department: item.department || '개발팀',
        interviewers: item.interviewers ? String(item.interviewers).split(',').map((s: string) => s.trim()) : [],
        status: item.status || 'UNDECIDED',
        score: item.score ?? null
      };
    });
    candidateList.value = result.data.map((item: Record<string, any>): Candidate => {
      let interviewDate = '';
      let interviewTime = '';
      if (item.startAt) {
        const startAtStr = item.startAt.replace(/Z$/, '');
        const dateObj = new Date(startAtStr);
        interviewDate = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`;
        interviewTime = `${String(dateObj.getHours()).padStart(2, '0')}:${String(dateObj.getMinutes()).padStart(2, '0')}`;
      }
      return {
        id: item.intervieweeId,
        name: item.name,
        position: item.position || '',
        department: item.department || '개발팀',
        interviewers: item.interviewers ? String(item.interviewers).split(',').map((s: string) => s.trim()) : [],
        status: item.status,
        interviewDate,
        score: item.score ?? null,
        interviewTime,
        room: item.roomNo || ''
      };
    });
  } catch (e) {
    alert('면접자 목록을 불러오지 못했습니다.');
  }
});
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-in-out;
}

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>