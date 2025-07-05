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
          @close="emitClose"
          @showDeleteConfirm="showDeleteConfirm = true"
          @handleExcelUpload="handleExcelUpload"
          @downloadExcel="downloadExcel"
          @sortBy="sortBy"
          @viewDetails="viewDetails"
        />
        <CandidateManage
          v-if="activeView === 'candidates'"
          :candidateList="candidateList"
          :filters="candidateFilters"
          @addNewCandidate="addNewCandidate"
          @editCandidate="editCandidate"
          @deleteCandidate="deleteCandidate"
        />
        <InterviewCalendar
          v-if="showCalendarView"
          :calendarDays="calendarDays"
          :currentMonthYear="currentMonthYear"
          @close="showCalendarView = false"
          @prevMonth="prevMonth"
          @nextMonth="nextMonth"
          @showInterviewDetail="showInterviewDetail"
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

    <!-- Delete Confirmation Modal -->
    <!-- <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
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
    </div> -->

    <!-- 지원자 삭제 확인 모달 -->
    <!-- <div v-if="showCandidateDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4 relative animate-fadeIn">
        <h3 class="text-xl font-bold text-gray-900 mb-4">지원자 삭제</h3>
        <p class="text-gray-700 mb-6">정말로 {{ deletingCandidate?.name }} 지원자를 삭제하시겠습니까?</p>
        <div class="flex justify-end gap-3">
          <button
            @click="showCandidateDeleteModal = false; deletingCandidate = null"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors whitespace-nowrap"
          >
            취소
          </button>
          <button
            @click="confirmDeleteCandidate"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors whitespace-nowrap"
          >
            삭제
          </button>
        </div>
      </div>
    </div> -->

    <!-- 지원자 추가/수정 모달
    <div v-if="showCandidateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4 relative animate-fadeIn">
        <h3 class="text-xl font-bold text-gray-900 mb-6">
          {{ isEditingCandidate ? '지원자 정보 수정' : '새 지원자 추가' }}
        </h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">이름</label>
            <input type="text" v-model="candidateForm.name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">지원 직무</label>
            <input type="text" v-model="candidateForm.position" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">상태</label>
            <select v-model="candidateForm.status" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
              <option value="">상태 선택</option>
              <option value="서류 합격">서류 합격</option>
              <option value="면접 예정">면접 예정</option>
              <option value="면접 완료">면접 완료</option>
              <option value="최종 합격">최종 합격</option>
            </select>
            <div v-if="candidateForm.status" class="mt-1">
              <span :class="{
                'px-2 py-1 text-xs font-medium rounded-full': true,
                'bg-yellow-100 text-yellow-800': candidateForm.status === '서류 합격',
                'bg-blue-100 text-blue-800': candidateForm.status === '면접 예정',
                'bg-green-100 text-green-800': candidateForm.status === '최종 합격',
                'bg-gray-100 text-gray-800': candidateForm.status === '면접 완료'
              }">{{ candidateForm.status }}</span>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">면접 일정</label>
            <input type="date" v-model="candidateForm.interviewDate" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">면접 시간</label>
            <input type="text" v-model="candidateForm.interviewTime" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">면접관 (쉼표로 구분)</label>
            <input type="text" v-model="candidateForm.interviewersString" placeholder="예: 김민수, 이지원" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">면접실</label>
            <input type="text" v-model="candidateForm.room" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">점수</label>
            <input type="number" v-model="candidateForm.score" min="0" max="100" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="closeCandidateModal"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors whitespace-nowrap"
          >
            취소
          </button>
          <button
            @click="saveCandidateForm"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors whitespace-nowrap"
          >
            저장
          </button>
        </div>
      </div>
    </div> -->

    캘린더 모달
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

    <!-- 통계 분석 모달 -->
    <!-- (StatisticsModal.vue로 대체, 이 부분은 삭제) -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';
import axios from 'axios';
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

// 지원자 필터 상태
const candidateFilters = ref({
  status: 'all',
  interviewDate: '',
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
  { key: 'department', label: '지원 부서' },
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
const candidateList = ref<any[]>([]);

// 모달 상태
const showDeleteConfirm = ref(false);
const showCalendarView = ref(false);
const selectedInterview = ref<any>(null);
const currentDate = ref(new Date());
const showStatisticsView = ref(false);
const statisticsFilter = ref({
  period: 'all'
});

// 지원자 관리 모달 상태
const showCandidateDeleteModal = ref(false);
const showCandidateModal = ref(false);
const deletingCandidate = ref<any>(null);
const isEditingCandidate = ref(false);
const candidateForm = ref<{ id: number; name: string; position: string; interviewersString: string; status: string; interviewDate: string; score: number | null; interviewTime: string; room: string; interviewers?: string[] }>({
  id: 0,
  name: '',
  position: '',
  interviewersString: '',
  status: '',
  interviewDate: '',
  score: null,
  interviewTime: '',
  room: ''
});

// 차트 참조
const jobChartRef = ref(null);
const scoreDistributionChartRef = ref(null);
const avgScoreChartRef = ref(null);

let jobChart: echarts.ECharts | null = null;
let scoreDistributionChart: echarts.ECharts | null = null;
let avgScoreChart: echarts.ECharts | null = null;

// 뷰 변경 함수
const setActiveView = (view: string) => {
  activeView.value = view;
};

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

// @ts-expect-error - 함수가 사용되지 않지만 필요할 수 있음
const deleteAllInterviews = () => {
  interviews.value = [];
  showDeleteConfirm.value = false;
};

const handleExcelUpload = () => {
  // 엑셀 업로드 버튼/파일 input/함수 모두 제거
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

// 지원자 관리 함수들
const addNewCandidate = () => {
  isEditingCandidate.value = false;
  candidateForm.value = {
    id: 0,
    name: '',
    position: '',
    interviewersString: '',
    status: '',
    interviewDate: '',
    score: null,
    interviewTime: '',
    room: ''
  };
  showCandidateModal.value = true;
};

const editCandidate = (candidate: any) => {
  isEditingCandidate.value = true;
  candidateForm.value = { ...candidate };
  showCandidateModal.value = true;
};

const deleteCandidate = (candidate: any) => {
  deletingCandidate.value = candidate;
  showCandidateDeleteModal.value = true;
};

// @ts-expect-error - 함수가 사용되지 않지만 필요할 수 있음
const confirmDeleteCandidate = () => {
  if (deletingCandidate.value) {
    candidateList.value = candidateList.value.filter(c => c.id !== deletingCandidate.value.id);
    deletingCandidate.value = null;
    showCandidateDeleteModal.value = false;
  }
};

const closeCandidateModal = () => {
  showCandidateModal.value = false;
  candidateForm.value = {
    id: 0,
    name: '',
    position: '',
    interviewersString: '',
    status: '',
    interviewDate: '',
    score: null,
    interviewTime: '',
    room: ''
  };
};

// @ts-expect-error - 함수가 사용되지 않지만 필요할 수 있음
const saveCandidateForm = async () => {
  // @ts-expect-error - interviewersArr 변수가 사용되지 않지만 필요할 수 있음
  const interviewersArr = candidateForm.value.interviewersString
    ? candidateForm.value.interviewersString.split(',').map(s => s.trim()).filter(Boolean)
    : [];
  if (isEditingCandidate.value) {
    // 수정
    try {
      await axios.put(
        `http://3.38.218.18:8080/api/v1/interviewees/${candidateForm.value.id}`,
        {
          name: candidateForm.value.name,
          score: candidateForm.value.score
        }
      );
      // 목록 갱신
      const response = await fetch('http://3.38.218.18:8080/api/v1/interviewees/simple');
      if (response.ok) {
        const result = await response.json();
        candidateList.value = result.data.map((item: any) => {
          let interviewDate = '';
          let interviewTime = '';
          if (item.startAt) {
            const dateObj = new Date(item.startAt);
            interviewDate = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`;
            interviewTime = `${String(dateObj.getHours()).padStart(2, '0')}:${String(dateObj.getMinutes()).padStart(2, '0')}`;
          }
          return {
            id: item.intervieweeId,
            name: item.name,
            position: '',
            interviewers: item.interviewers ? (item.interviewers as string).split(',').map((s: any) => s.trim()) : [],
            status: item.status,
            interviewDate,
            score: item.score,
            interviewTime,
            room: item.roomNo
          }
        });
      }
      closeCandidateModal();
      alert('수정 성공!');
    } catch (e) {
      alert('수정 실패');
    }
  } else {
    // 추가
    try {
      await axios.post('http://3.38.218.18:8080/api/v1/interviewees', {
        name: candidateForm.value.name,
        score: candidateForm.value.score
      });
      // 목록 갱신
      const response = await fetch('http://3.38.218.18:8080/api/v1/interviewees/simple');
      if (response.ok) {
        const result = await response.json();
        candidateList.value = result.data.map((item: any) => {
          let interviewDate = '';
          let interviewTime = '';
          if (item.startAt) {
            const dateObj = new Date(item.startAt);
            interviewDate = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`;
            interviewTime = `${String(dateObj.getHours()).padStart(2, '0')}:${String(dateObj.getMinutes()).padStart(2, '0')}`;
          }
          return {
            id: item.intervieweeId,
            name: item.name,
            position: '',
            interviewers: item.interviewers ? (item.interviewers as string).split(',').map((s: any) => s.trim()) : [],
            status: item.status,
            interviewDate,
            score: item.score,
            interviewTime,
            room: item.roomNo
          }
        });
      }
      closeCandidateModal();
      alert('추가 성공!');
    } catch (e) {
      alert('추가 실패');
    }
  }
};

// 통계 차트 초기화
const initCharts = () => {
  if (jobChartRef.value) {
    jobChart = echarts.init(jobChartRef.value);
    jobChart.setOption({
      title: {
        text: '직무별 면접 현황',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          type: 'pie',
          radius: '50%',
          data: [
            { value: 35, name: '개발' },
            { value: 25, name: '디자인' },
            { value: 20, name: '마케팅' },
            { value: 15, name: '영업' },
            { value: 5, name: '기타' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    });
  }

  if (scoreDistributionChartRef.value) {
    scoreDistributionChart = echarts.init(scoreDistributionChartRef.value);
    scoreDistributionChart.setOption({
      title: {
        text: '면접자 점수 분포',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['0-20', '21-40', '41-60', '61-80', '81-100']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: [5, 15, 30, 25, 10],
          type: 'bar'
        }
      ]
    });
  }

  if (avgScoreChartRef.value) {
    avgScoreChart = echarts.init(avgScoreChartRef.value);
    avgScoreChart.setOption({
      title: {
        text: '역량별 평균 면접 점수',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      radar: {
        indicator: [
          { name: '전문성', max: 100 },
          { name: '의사소통', max: 100 },
          { name: '문제해결', max: 100 },
          { name: '팀워크', max: 100 },
          { name: '리더십', max: 100 }
        ]
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: [85, 75, 90, 80, 70],
              name: '평균 점수'
            }
          ]
        }
      ]
    });
  }
};

// 통계 필터 변경 감지
watch(statisticsFilter, () => {
  // 여기에 필터 변경 시 차트 업데이트 로직 추가
  updateCharts();
}, { deep: true });

// 차트 업데이트 함수
const updateCharts = () => {
  // 여기에 차트 데이터 업데이트 로직 추가
};

// 사이드바 통계 분석 링크 클릭 이벤트 핸들러
const showStatistics = () => {
  showStatisticsView.value = true;
  // 차트가 이미 초기화되어 있지 않은 경우에만 초기화
  if (!jobChart) {
    initCharts();
  }
};

onMounted(async () => {
  // 기존 차트 초기화 등 유지
  initCharts();
  // 면접자 목록 불러오기
  try {
    const response = await fetch('http://3.38.218.18:8080/api/v1/interviewees/simple');
    if (!response.ok) throw new Error('서버 오류');
    const result = await response.json();
    interviews.value = result.data.map((item: any) => {
      let date = '';
      let time = '';
      if (item.startAt) {
        // Z(UTC) 제거 후 파싱
        const startAtStr = item.startAt.replace(/Z$/, '');
        const dateObj = new Date(startAtStr);
        date = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`;
        time = `${String(dateObj.getHours()).padStart(2, '0')}:${String(dateObj.getMinutes()).padStart(2, '0')}`;
      }
      return {
        id: item.intervieweeId,
        date,
        time,
        room: item.roomNo,
        candidate: item.name,
        position: '',
        department: '',
        interviewers: item.interviewers ? (item.interviewers as string).split(',').map((s: any) => s.trim()) : [],
        status: item.status,
        score: item.score
      }
    });
    // candidateList도 동일하게 변환
    candidateList.value = result.data.map((item: any) => {
      let interviewDate = '';
      let interviewTime = '';
      if (item.startAt) {
        // Z(UTC) 제거 후 파싱
        const startAtStr = item.startAt.replace(/Z$/, '');
        const dateObj = new Date(startAtStr);
        interviewDate = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`;
        interviewTime = `${String(dateObj.getHours()).padStart(2, '0')}:${String(dateObj.getMinutes()).padStart(2, '0')}`;
      }
      return {
        id: item.intervieweeId,
        name: item.name,
        interviewers: item.interviewers ? (item.interviewers as string).split(',').map((s: any) => s.trim()) : [],
        status: item.status,
        interviewDate,
        score: item.score,
        interviewTime,
        room: item.roomNo
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