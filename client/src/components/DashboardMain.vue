<!-- DashboardMain.vue -->
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
      <!-- 전체 지원자 -->
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
          취소된 면접자 수 : <span class="text-red-600 font-medium flex items-center"><i class="fas fa-times text-xs"></i>{{ cancelledInterviewsCount }}명</span>
        </p>
      </div>
      <!-- 오늘의 면접 -->
      <div class="bg-white rounded-lg p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
            <i class="fas fa-calendar-day text-green-600 text-2xl"></i>
          </div>
          <div>
            <h3 class="text-lg font-medium text-gray-700">오늘의 면접</h3>
            <p class="text-3xl font-semibold text-gray-900">{{ todayInterviewsCount }}</p>
          </div>
        </div>
        <p class="text-sm text-gray-500 flex items-center gap-1">
          전일 대비 <span class="text-green-600 font-medium flex items-center"><i class="fas fa-caret-up text-xs"></i>{{ todayInterviewsCount }}</span>
        </p>
      </div>
      <!-- 완료된 면접 -->
      <div class="bg-white rounded-lg p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
            <i class="fas fa-check-circle text-purple-600 text-2xl"></i>
          </div>
          <div>
            <h3 class="text-lg font-medium text-gray-700">완료된 면접</h3>
            <p class="text-3xl font-semibold text-gray-900">{{ completedInterviewsCount }}</p>
          </div>
        </div>
        <p class="text-sm text-gray-500">전체 면접 대비 {{ completedPercentage }}%</p>
      </div>
      <!-- 대기중 -->
      <div class="bg-white rounded-lg p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
            <i class="fas fa-clock text-orange-600 text-2xl"></i>
          </div>
          <div>
            <h3 class="text-lg font-medium text-gray-700">대기중</h3>
            <p class="text-3xl font-semibold text-gray-900">{{ scheduledInterviewsCount }}</p>
          </div>
        </div>
        <p class="text-sm text-gray-500">전체 면접 대비 {{ scheduledPercentage }}%</p>
      </div>
    </div>
    
    <!-- 필터 섹션 -->
    <div class="bg-white rounded-lg p-6 mb-8 border border-gray-100">
      <div class="grid grid-cols-4 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-2">면접 기간</label>
          <select :value="filters.period" @change="updateFilter('period', ($event.target as HTMLSelectElement).value)" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-gray-400">
            <option value="all">전체 기간</option>
            <option value="today">오늘</option>
            <option value="week">이번 주</option>
            <option value="month">이번 달</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">면접실</label>
          <select :value="filters.room" @change="updateFilter('room', ($event.target as HTMLSelectElement).value)" class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500">
            <option value="all">전체</option>
            <option value="회의실A">회의실A</option>
            <option value="회의실B">회의실B</option>
            <option value="회의실C">회의실C</option>
            <option value="회의실D">회의실D</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">평가 상태</label>
          <select :value="filters.status" @change="updateFilter('status', ($event.target as HTMLSelectElement).value)" class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500">
            <option value="all">전체</option>
            <option value="COMPLETED">평가 완료</option>
            <option value="SCHEDULED">대기중</option>
            <option value="IN_PROGRESS">진행중</option>
            <option value="CANCELLED">취소</option>
            <option value="UNDECIDED">미정</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">검색</label>
          <div class="relative">
            <input type="text" :value="filters.search" @input="updateFilter('search', ($event.target as HTMLInputElement).value)" placeholder="이름, 부서, 면접실, 면접관 검색" class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500">
            <i class="fas fa-search absolute right-3 top-2.5 text-gray-400"></i>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 테이블 섹션 -->
    <div class="bg-white rounded-lg border border-gray-100 overflow-hidden mb-8">
      <div class="p-4 border-b border-gray-100 flex justify-between items-center">
        <h2 class="text-lg font-medium text-gray-700">면접자 목록 ({{ sortedInterviews.length }}건)</h2>
        <div class="flex items-center gap-3">
          <button @click="showDeleteConfirm = true" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2">
            <i class="fas fa-trash-alt"></i> 전체 삭제
          </button>
          <label class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2">
            <i class="fas fa-file-upload"></i> 엑셀 업로드
            <input type="file" accept=".xlsx,.xls" class="hidden" @change="handleExcelUpload">
          </label>
          <button @click="$emit('downloadExcel')" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2">
            <i class="fas fa-file-download"></i> 엑셀 다운로드
          </button>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th v-for="column in visibleTableColumns" :key="column.key"
                  @click="$emit('sortBy', column.key)"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                {{ column.label }} <i class="fas fa-sort ml-1"></i>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="pagedInterviews.length === 0">
              <td :colspan="visibleTableColumns.length" class="px-6 py-8 text-center text-gray-500">
                <div class="flex flex-col items-center">
                  <i class="fas fa-search text-3xl text-gray-300 mb-2"></i>
                  <span>조건에 맞는 면접자가 없습니다.</span>
                </div>
              </td>
            </tr>
            <tr v-for="interview in pagedInterviews" :key="interview.id" class="hover:bg-gray-50">
              <td v-for="column in visibleTableColumns" :key="column.key" class="px-6 py-4 whitespace-nowrap">
                <template v-if="column.key === 'date'">
                  <span class="text-sm">{{ interview.date }}</span>
                </template>
                <template v-else-if="column.key === 'time'">
                  <span class="text-sm">{{ interview.time }}</span>
                </template>
                <template v-else-if="column.key === 'room'">
                  <span class="text-sm">{{ interview.room || '-' }}</span>
                </template>
                <template v-else-if="column.key === 'candidate'">
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ interview.candidate }}</div>
                    <div v-if="interview.position && interview.position.trim()" class="text-sm text-gray-500">{{ interview.position }}</div>
                  </div>
                </template>
                <template v-else-if="column.key === 'interviewers'">
                  <div class="max-w-32 truncate text-sm" :title="interview.interviewers.join(', ')">
                    {{ interview.interviewers.join(', ') || '-' }}
                  </div>
                </template>
                <template v-else-if="column.key === 'status'">
                  <span :class="{
                    'px-2 py-1 text-xs font-medium rounded-full': true,
                    'bg-green-100 text-green-800': interview.status === 'COMPLETED',
                    'bg-yellow-100 text-yellow-800': interview.status === 'SCHEDULED' || interview.status === 'UNDECIDED',
                    'bg-blue-100 text-blue-800': interview.status === 'IN_PROGRESS',
                    'bg-gray-100 text-gray-800': interview.status === 'CANCELLED'
                  }">
                    {{ getStatusText(interview.status) }}
                  </span>
                </template>
                <template v-else-if="column.key === 'score'">
                  <span v-if="interview.score !== null" :class="{
                    'font-medium text-sm': true,
                    'text-green-600': interview.score >= 90,
                    'text-blue-600': interview.score >= 80 && interview.score < 90,
                    'text-yellow-600': interview.score >= 70 && interview.score < 80,
                    'text-red-600': interview.score < 70
                  }">
                    {{ interview.score }}점
                  </span>
                  <span v-else class="text-gray-400 text-sm">-</span>
                </template>
                <template v-else-if="column.key === 'actions'">
                  <button @click="$emit('viewDetails', interview.id)" class="text-red-600 hover:text-red-800 p-1" title="상세보기">
                    <i class="fas fa-eye"></i>
                  </button>
                </template>
                <template v-else>
                  <span class="text-sm">{{ (interview as any)[column.key] }}</span>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 페이지네이션 및 페이지당 개수 선택 UI -->
    <div class="relative px-4 pb-4">
      <div class="absolute left-0 top-0 flex items-center gap-2">
        <label for="itemsPerPageDashboard" class="text-sm text-gray-500">페이지당</label>
        <select id="itemsPerPageDashboard" v-model.number="itemsPerPage" class="px-2 py-1 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
          <option :value="5">5</option>
          <option :value="10">10</option>
          <option :value="15">15</option>
        </select>
        <span class="text-sm text-gray-500">개 보기</span>
      </div>
      <div class="flex justify-center items-center gap-2 w-full">
        <button @click="goToPage(1)" :disabled="currentPage === 1" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === 1 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-red-100'">
          <i class="fas fa-angle-double-left"></i>
        </button>
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === 1 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-red-100'">
          <i class="fas fa-chevron-left"></i>
        </button>
        <span v-for="page in visiblePages" :key="page">
          <button @click="goToPage(page)" :class="page === currentPage ? 'bg-red-500 text-white' : 'bg-white text-gray-700 hover:bg-red-100'" class="px-3 py-1 rounded-full border mx-1 shadow-sm transition-colors duration-150">{{ page }}</button>
        </span>
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages || totalPages === 0" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === totalPages || totalPages === 0 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-red-100'">
          <i class="fas fa-chevron-right"></i>
        </button>
        <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages || totalPages === 0" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === totalPages || totalPages === 0 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-red-100'">
          <i class="fas fa-angle-double-right"></i>
        </button>
      </div>
    </div>
    
    <!-- 전체 삭제 확인 모달 추가 (파일 하단에 위치) -->
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
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, ref, computed, watch } from 'vue';

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

const props = defineProps<{
  candidateList: Candidate[];
  filters: Record<string, string>;
  tableColumns: TableColumn[];
  sortedInterviews: Interview[];
}>();

const emits = defineEmits([
  'close',
  'showDeleteConfirm',
  'handleExcelUpload',
  'downloadExcel',
  'sortBy',
  'viewDetails',
  'updateFilters'
]);

// 페이징 관련 상태
const itemsPerPage = ref(5);
const currentPage = ref(1);

const pagedInterviews = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return props.sortedInterviews.slice(start, start + itemsPerPage.value);
});

const totalPages = computed(() => Math.ceil(props.sortedInterviews.length / itemsPerPage.value));

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
}

watch(itemsPerPage, () => {
  currentPage.value = 1;
});

// 필터가 변경될 때마다 첫 페이지로 이동
watch(() => props.sortedInterviews, () => {
  currentPage.value = 1;
});

// 최대 5개만 보이는 페이지네이션 계산
const visiblePages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  if (total <= 5) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  if (current <= 3) {
    return [1, 2, 3, 4, 5];
  }
  if (current >= total - 2) {
    return [total - 4, total - 3, total - 2, total - 1, total].filter(p => p > 0);
  }
  return [current - 2, current - 1, current, current + 1, current + 2];
});

// '지원 부서' 컬럼을 제외한 컬럼만 사용 (필요하다면 포함)
const visibleTableColumns = computed(() => props.tableColumns);

// 통계 계산을 위한 computed 속성들
const todayInterviewsCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD 형식
  return props.candidateList.filter(candidate => candidate.interviewDate === today).length;
});

const completedInterviewsCount = computed(() => {
  return props.candidateList.filter(candidate => candidate.status === 'COMPLETED').length;
});

const scheduledInterviewsCount = computed(() => {
  return props.candidateList.filter(candidate => candidate.status === 'SCHEDULED').length;
});

const completedPercentage = computed(() => {
  if (props.candidateList.length === 0) return 0;
  return Math.round((completedInterviewsCount.value / props.candidateList.length) * 100);
});

const scheduledPercentage = computed(() => {
  if (props.candidateList.length === 0) return 0;
  return Math.round((scheduledInterviewsCount.value / props.candidateList.length) * 100);
});

const cancelledInterviewsCount = computed(() => {
  return props.candidateList.filter(candidate => candidate.status === 'CANCELLED').length;
});

// 엑셀 업로드 처리 함수
function handleExcelUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  fetch('http://3.38.218.18:8080/api/v1/uploads/interview-schedule', {
    method: 'POST',
    body: formData
  })
    .then(response => {
      if (!response.ok) {
        alert('엑셀 업로드 실패: ' + response.statusText);
        return;
      }
      alert('엑셀 업로드 성공!');
    })
    .catch(error => {
      alert('엑셀 업로드 중 오류 발생: ' + (error as Error).message);
    })
    .finally(() => {
      (event.target as HTMLInputElement).value = '';
    });
}

function getStatusText(status: string) {
  switch ((status || '').toUpperCase()) {
    case 'COMPLETED': return '평가 완료';
    case 'SCHEDULED': return '대기중';
    case 'IN_PROGRESS': return '진행중';
    case 'CANCELLED': return '취소';
    case 'UNDECIDED': return '미정';
    default: return status;
  }
}

// 모달 상태 추가
const showDeleteConfirm = ref(false);

// 필터 업데이트 함수 - 수정된 버전
function updateFilter(key: string, value: string) {
  const newFilters = { ...props.filters, [key]: value };
  console.log('Filter updated:', key, '=', value); // 디버깅용
  console.log('New filters:', newFilters); // 디버깅용
  emits('updateFilters', newFilters);
}

function deleteAllInterviews() {
  fetch('http://3.38.218.18:8080/api/v1/interviews?deleteFiles=true', {
    method: 'DELETE',
    headers: { 'Accept': '*/*' }
  })
    .then(response => {
      if (!response.ok) {
        alert('전체 삭제 실패: ' + response.statusText);
        return;
      }
      alert('전체 삭제가 완료되었습니다.');
      showDeleteConfirm.value = false;
      // 필요하다면 데이터 새로고침 emit 등 추가
    })
    .catch(error => {
      alert('전체 삭제 중 오류 발생: ' + (error as Error).message);
      showDeleteConfirm.value = false;
    });
}
</script>

<style scoped>
/* 필요한 스타일 */
</style>