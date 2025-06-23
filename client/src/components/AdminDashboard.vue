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

    <!-- 지원자 삭제 확인 모달 -->
    <div v-if="showCandidateDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
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
    </div>

    <!-- 지원자 추가/수정 모달 -->
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
          <div v-if="isEditingCandidate">
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

    <!-- 고정 위치 버튼 -->
    <div v-if="activeView === 'candidates'" class="fixed bottom-8 right-8 z-50">
      <button class="px-6 py-3 bg-orange-500 text-white rounded-lg shadow-lg hover:bg-orange-600 transition-colors">적용</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';
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

// 지원자 목록 데이터
const candidateList = ref<Array<{ id: number; name: string; position: string; interviewers: string[]; status: string; interviewDate: string; score: number | null; interviewTime: string; room: string }>>([
  { id: 1, name: '홍길동', position: '소프트웨어 엔지니어', interviewers: ['김민수', '이지원'], status: '서류 합격', interviewDate: '2025-06-20', score: null, interviewTime: '09:00 ~ 10:00', room: '1호실' },
  { id: 2, name: '김철수', position: '프론트엔드 개발자', interviewers: ['박성훈'], status: '면접 예정', interviewDate: '2025-06-21', score: null, interviewTime: '', room: '2호실' },
  { id: 3, name: '이영희', position: '백엔드 개발자', interviewers: ['최영희', '정태우'], status: '최종 합격', interviewDate: '2025-06-15', score: 92, interviewTime: '', room: '1호실' },
  { id: 4, name: '박지민', position: 'UI/UX 디자이너', interviewers: ['강미란'], status: '면접 완료', interviewDate: '2025-06-16', score: 88, interviewTime: '', room: '3호실' },
  { id: 5, name: '최수진', position: '데이터 엔지니어', interviewers: ['김민수'], status: '서류 합격', interviewDate: '2025-06-22', score: null, interviewTime: '', room: '2호실' }
]);

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
