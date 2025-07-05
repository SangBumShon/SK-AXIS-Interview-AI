<!-- CandidateManage.vue -->
<template>
  <!-- 지원자 관리 뷰 -->
  <div class="p-8 overflow-visible min-h-0 h-auto">
    <!-- 지원자 관리 헤더 -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900">지원자 관리</h2>
      <div class="text-sm text-gray-600">
        총 {{ candidateList.length }}명 | 필터 결과: {{ filteredCandidates.length }}명
      </div>
    </div>
    
    <!-- 필터 및 검색 - 개선된 버전 -->
    <div class="bg-white rounded-lg p-6 mb-6 border border-gray-200">
      <div class="grid grid-cols-5 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">상태</label>
          <select v-model="filters.status" @change="onFilterChange" class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="all">전체</option>
            <option value="SCHEDULED">예정</option>
            <option value="IN_PROGRESS">진행중</option>
            <option value="COMPLETED">완료</option>
            <option value="CANCELLED">취소</option>
            <option value="UNDECIDED">미정</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">면접 일정</label>
          <input 
            type="date" 
            v-model="filters.interviewDate" 
            @change="onFilterChange"
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">면접실</label>
          <select v-model="filters.room" @change="onFilterChange" class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="all">전체</option>
            <option v-for="room in uniqueRooms" :key="room" :value="room">{{ room }}</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">검색</label>
          <div class="relative">
            <input 
              type="text" 
              v-model="filters.search" 
              @input="onFilterChange"
              placeholder="이름, 직무, 면접관 검색" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <i class="fas fa-search absolute right-3 top-2.5 text-gray-400"></i>
          </div>
        </div>
      </div>
      
      <!-- 필터 상태 표시 및 초기화 버튼 -->
      <div class="mt-4 flex items-center justify-between">
        <div class="flex items-center gap-2 flex-wrap">
          <span class="text-sm text-gray-600">활성 필터:</span>
          <span v-if="filters.status !== 'all'" class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
            상태: {{ getStatusText(filters.status) }}
          </span>
          <span v-if="filters.interviewDate" class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
            날짜: {{ filters.interviewDate }}
          </span>
          <span v-if="filters.room !== 'all'" class="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
            면접실: {{ filters.room }}
          </span>
          <span v-if="filters.search" class="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
            검색: "{{ filters.search }}"
          </span>
          <span v-if="!hasActiveFilters" class="text-xs text-gray-400">없음</span>
        </div>
        
        <button 
          v-if="hasActiveFilters"
          @click="resetFilters" 
          class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50">
          <i class="fas fa-times mr-1"></i>필터 초기화
        </button>
      </div>
    </div>
    
    <!-- 지원자 목록 테이블 -->
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div class="p-4 border-b border-gray-100 flex justify-between items-center">
        <h2 class="text-lg font-medium text-gray-700">
          지원자 목록 
          <span class="text-sm font-normal text-gray-500">
            ({{ filteredCandidates.length }}명 / 전체 {{ candidateList.length }}명)
          </span>
        </h2>
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <label for="itemsPerPage" class="text-sm text-gray-500">페이지당</label>
            <select id="itemsPerPage" v-model.number="itemsPerPage" class="px-2 py-1 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option :value="8">8</option>
              <option :value="10">10</option>
              <option :value="15">15</option>
              <option :value="20">20</option>
            </select>
            <span class="text-sm text-gray-500">개 보기</span>
          </div>
          <button @click="openAddModal" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2">
            <i class="fas fa-plus"></i>
            지원자 추가
          </button>
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th @click="sortBy('interviewDate')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100">
                날짜 <i class="fas fa-sort ml-1"></i>
              </th>
              <th @click="sortBy('interviewTime')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100">
                시간 <i class="fas fa-sort ml-1"></i>
              </th>
              <th @click="sortBy('room')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100">
                면접실 <i class="fas fa-sort ml-1"></i>
              </th>
              <th @click="sortBy('name')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100">
                지원자 <i class="fas fa-sort ml-1"></i>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">면접관</th>
              <th @click="sortBy('status')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100">
                상태 <i class="fas fa-sort ml-1"></i>
              </th>
              <th @click="sortBy('score')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100">
                점수 <i class="fas fa-sort ml-1"></i>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">관리</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="pagedCandidates.length === 0">
              <td colspan="8" class="px-6 py-8 text-center text-gray-500">
                <div class="flex flex-col items-center">
                  <i class="fas fa-search text-3xl text-gray-300 mb-2"></i>
                  <span>조건에 맞는 지원자가 없습니다.</span>
                  <button @click="resetFilters" class="mt-2 text-blue-600 hover:text-blue-800 text-sm">
                    필터 초기화
                  </button>
                </div>
              </td>
            </tr>
            <tr v-for="candidate in pagedCandidates" :key="candidate.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                {{ formatDate(candidate.interviewDate) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">{{ candidate.interviewTime || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 py-1 bg-gray-100 text-gray-800 rounded-md text-xs">
                  {{ candidate.room || '-' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <div class="text-sm font-medium text-gray-900">{{ candidate.name }}</div>
                  <div v-if="candidate.position && candidate.position.trim()" class="text-sm text-gray-500">{{ candidate.position }}</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="max-w-32 truncate" :title="candidate.interviewers ? candidate.interviewers.join(', ') : '-'">
                  {{ candidate.interviewers ? candidate.interviewers.join(', ') : '-' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="{
                  'px-2 py-1 text-xs font-medium rounded-full': true,
                  'bg-green-100 text-green-800': candidate.status === 'COMPLETED',
                  'bg-yellow-100 text-yellow-800': candidate.status === 'SCHEDULED' || candidate.status === 'UNDECIDED',
                  'bg-blue-100 text-blue-800': candidate.status === 'IN_PROGRESS',
                  'bg-gray-100 text-gray-800': candidate.status === 'CANCELLED'
                }">{{ getStatusText(candidate.status) }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span v-if="candidate.score !== null" :class="{
                  'font-medium': true,
                  'text-green-600': candidate.score >= 90,
                  'text-blue-600': candidate.score >= 80 && candidate.score < 90,
                  'text-yellow-600': candidate.score >= 70 && candidate.score < 80,
                  'text-red-600': candidate.score < 70
                }">
                  {{ candidate.score }}점
                </span>
                <span v-else class="text-gray-400">-</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <button class="text-blue-600 hover:text-blue-800 p-1" @click="openEditModal(candidate)" title="수정">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="text-red-600 hover:text-red-800 p-1" @click="openDeleteModal(candidate)" title="삭제">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 페이지네이션 -->
    <div class="relative px-4 pb-4 mt-6" v-if="totalPages > 1">
      <div class="flex justify-center items-center gap-2 w-full">
        <button @click="goToPage(1)" :disabled="currentPage === 1" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === 1 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-blue-100'">
          <i class="fas fa-angle-double-left"></i>
        </button>
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === 1 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-blue-100'">
          <i class="fas fa-chevron-left"></i>
        </button>
        <span v-for="page in visiblePages" :key="page">
          <button @click="goToPage(page)" :class="page === currentPage ? 'bg-red-500 text-white' : 'bg-white text-gray-700 hover:bg-red-100'" class="px-3 py-1 rounded-full border mx-1 shadow-sm transition-colors duration-150">{{ page }}</button>
        </span>
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages || totalPages === 0" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === totalPages || totalPages === 0 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-blue-100'">
          <i class="fas fa-chevron-right"></i>
        </button>
        <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages || totalPages === 0" class="px-3 py-1 rounded-full border shadow-sm transition-colors duration-150" :class="currentPage === totalPages || totalPages === 0 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-blue-100'">
          <i class="fas fa-angle-double-right"></i>
        </button>
      </div>
    </div>

    <!-- 지원자 추가/수정 모달 -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4 relative animate-fadeIn">
        <h3 class="text-xl font-bold text-gray-900 mb-6">
          {{ isEditing ? '지원자 정보 수정' : '새 지원자 추가' }}
        </h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">날짜</label>
            <input type="date" v-model="form.interviewDate" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">시간</label>
            <input type="time" v-model="form.interviewTime" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">면접실</label>
            <input type="text" v-model="form.room" placeholder="예: 회의실A" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">지원자 이름</label>
            <input type="text" v-model="form.name" placeholder="이름을 입력하세요" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">면접관 (쉼표로 구분)</label>
            <input type="text" v-model="form.interviewersString" placeholder="예: 김민수, 이지원" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">상태</label>
            <select v-model="form.status" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="SCHEDULED">예정</option>
              <option value="IN_PROGRESS">진행중</option>
              <option value="COMPLETED">완료</option>
              <option value="CANCELLED">취소</option>
              <option value="UNDECIDED">미정</option>
            </select>
            <div v-if="form.status" class="mt-1">
              <span :class="{
                'px-2 py-1 text-xs font-medium rounded-full': true,
                'bg-yellow-100 text-yellow-800': form.status === 'SCHEDULED' || form.status === 'UNDECIDED',
                'bg-blue-100 text-blue-800': form.status === 'IN_PROGRESS',
                'bg-green-100 text-green-800': form.status === 'COMPLETED',
                'bg-gray-100 text-gray-800': form.status === 'CANCELLED'
              }">{{ getStatusText(form.status) }}</span>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">점수 (0-100)</label>
            <input type="number" v-model="form.score" min="0" max="100" placeholder="점수를 입력하세요" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="closeModal"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
          >
            취소
          </button>
          <button
            @click="isEditing ? updateCandidate() : addCandidate()"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            {{ isEditing ? '수정' : '추가' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 삭제 모달 -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4 relative animate-fadeIn">
        <h3 class="text-xl font-bold text-gray-900 mb-4">지원자 삭제</h3>
        <p class="text-gray-700 mb-6">정말로 {{ deletingCandidate?.name }} 지원자를 삭제하시겠습니까?</p>
        <div class="flex justify-end gap-3">
          <button
            @click="showDeleteModal = false; deletingCandidate = null"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
          >
            취소
          </button>
          <button
            @click="confirmDeleteCandidate"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            삭제
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';

interface Candidate {
  id: number;
  interviewId: number;
  name: string;
  position: string;
  interviewers: string[];
  status: string;
  interviewDate: string;
  score: number | null;
  interviewTime: string;
  room: string;
}

// 내부 상태로 관리
const candidateList = ref<Candidate[]>([]);

// 개선된 필터 상태
const filters = ref({ 
  status: 'all', 
  interviewDate: '', 
  search: '',
  room: 'all'
});

// 정렬 상태
const sortConfig = ref({
  key: 'interviewDate',
  direction: 'asc' as 'asc' | 'desc'
});

// 모달 상태 및 폼
const showModal = ref(false);
const isEditing = ref(false);
const form = ref<Partial<Candidate & { interviewersString?: string }>>({});

// 삭제 모달 상태
const showDeleteModal = ref(false);
const deletingCandidate = ref<Candidate | null>(null);

// 고유 면접실 목록
const uniqueRooms = computed(() => {
  const rooms = candidateList.value
    .map(c => c.room)
    .filter(room => room && room.trim())
    .filter((room, index, arr) => arr.indexOf(room) === index)
    .sort();
  return rooms;
});

// 활성 필터 여부 확인
const hasActiveFilters = computed(() => {
  return filters.value.status !== 'all' ||
         filters.value.interviewDate !== '' ||
         filters.value.search !== '' ||
         filters.value.room !== 'all';
});

// 목록 fetch 함수
async function fetchCandidates() {
  try {
    const response = await fetch('http://3.38.218.18:8080/api/v1/interviewees/simple');
    if (response.ok) {
      const result = await response.json();
      console.log('서버에서 받아온 최신 목록:', result.data);
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
          interviewId: item.interviewId,
          name: item.name,
          position: item.job,
          interviewers: item.interviewers ? String(item.interviewers).split(',').map((s: string) => s.trim()) : [],
          status: item.status,
          interviewDate,
          score: item.score,
          interviewTime,
          room: item.roomNo
        };
      });
    }
  } catch (error) {
    console.error('데이터 로딩 실패:', error);
    alert('데이터를 불러오는데 실패했습니다.');
  }
}

onMounted(fetchCandidates);

// 개선된 필터링 로직
const filteredCandidates = computed(() => {
  let filtered = [...candidateList.value];
  
  // 상태 필터
  if (filters.value.status !== 'all') {
    filtered = filtered.filter(c => c.status === filters.value.status);
  }
  
  // 날짜 필터
  if (filters.value.interviewDate) {
    filtered = filtered.filter(c => c.interviewDate === filters.value.interviewDate);
  }
  
  // 면접실 필터
  if (filters.value.room !== 'all') {
    filtered = filtered.filter(c => c.room === filters.value.room);
  }
  
  // 검색 필터 - 확장된 검색 범위
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase();
    filtered = filtered.filter(c =>
      c.name.toLowerCase().includes(search) ||
      (c.position && c.position.toLowerCase().includes(search)) ||
      (c.room && c.room.toLowerCase().includes(search)) ||
      c.interviewers.some(interviewer => interviewer.toLowerCase().includes(search))
    );
  }
  
  // 정렬 적용
  return filtered.sort((a, b) => {
    const key = sortConfig.value.key as keyof Candidate;
    const aVal = a[key] ?? '';
    const bVal = b[key] ?? '';
    if (aVal < bVal) return sortConfig.value.direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortConfig.value.direction === 'asc' ? 1 : -1;
    return 0;
  });
});

// 페이징
const itemsPerPage = ref(8);
const currentPage = ref(1);

const pagedCandidates = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return filteredCandidates.value.slice(start, start + itemsPerPage.value);
});

const totalPages = computed(() => Math.ceil(filteredCandidates.value.length / itemsPerPage.value));

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
}

// 페이지 관련 watcher
watch(itemsPerPage, () => { 
  currentPage.value = 1; 
});

watch(filteredCandidates, () => {
  currentPage.value = 1;
});

const visiblePages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1);
  if (current <= 3) return [1, 2, 3, 4, 5];
  if (current >= total - 2) return [total - 4, total - 3, total - 2, total - 1, total].filter(p => p > 0);
  return [current - 2, current - 1, current, current + 1, current + 2];
});

// 필터 변경 핸들러
function onFilterChange() {
  currentPage.value = 1;
  console.log('필터 변경됨:', filters.value);
}

// 필터 초기화
function resetFilters() {
  filters.value = {
    status: 'all',
    interviewDate: '',
    search: '',
    room: 'all'
  };
  currentPage.value = 1;
}

// 정렬 함수
function sortBy(key: string) {
  if (sortConfig.value.key === key) {
    sortConfig.value.direction = sortConfig.value.direction === 'asc' ? 'desc' : 'asc';
  } else {
    sortConfig.value.key = key;
    sortConfig.value.direction = 'asc';
  }
}

// 모달 열기/닫기
function openAddModal() {
  isEditing.value = false;
  form.value = {
    status: 'SCHEDULED',
    score: null
  };
  showModal.value = true;
}

function openEditModal(candidate: Candidate) {
  isEditing.value = true;
  form.value = { 
    ...candidate, 
    interviewersString: candidate.interviewers?.join(', ') || ''
  };
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  form.value = {};
}

// 공통 폼 검증 함수
function validateCandidateForm() {
  if (!form.value.name || !form.value.room) {
    alert('지원자 이름과 면접실을 모두 입력해 주세요.');
    return false;
  }
  
  if (!form.value.interviewDate || !form.value.interviewTime) {
    alert('면접 일자와 시간을 모두 입력해 주세요.');
    return false;
  }
  
  return true;
}

// 지원자 추가 함수 (POST)
async function addCandidate() {
  if (!validateCandidateForm()) return;
  
  const interviewersArr = form.value.interviewersString
    ? form.value.interviewersString.split(',').map(s => s.trim()).filter(Boolean)
    : [];
  
  // 날짜와 시간 조합
  const date = form.value.interviewDate || '';
  const time = form.value.interviewTime || '00:00';
  
  // 로컬 시간으로 Date 객체 생성
  const [year, month, day] = date.split('-').map(Number);
  const [hour, minute] = time.split(':').map(Number);
  const localDate = new Date(year, month - 1, day, hour, minute);
  const startAt = localDate.toISOString();
  
  // endAt: startAt에서 30분 추가
  const endDate = new Date(localDate);
  endDate.setMinutes(endDate.getMinutes() + 30);
  const endAt = endDate.toISOString();
  
  const payload = {
    name: form.value.name,
    job: form.value.position || "개발자",
    roomId: form.value.room,
    interviewers: interviewersArr.join(', '),
    startAt,
    endAt,
    score: form.value.score ?? 0,
    status: form.value.status
  };
  
  console.log('지원자 추가 payload:', payload);
  
  try {
    await axios.post('http://3.38.218.18:8080/api/v1/interviewees/interviewee', payload);
    await fetchCandidates();
    closeModal();
    alert('지원자 추가 성공!');
  } catch (e) {
    console.error('지원자 추가 실패:', e);
    alert('지원자 추가 실패');
  }
}

// 지원자 수정 함수 (PUT)
async function updateCandidate() {
  if (!validateCandidateForm()) return;
  
  const interviewersArr = form.value.interviewersString
    ? form.value.interviewersString.split(',').map(s => s.trim()).filter(Boolean)
    : [];
  
  const date = form.value.interviewDate || '';
  const time = form.value.interviewTime || '00:00';
  
  // 날짜 정규화
  const normalizedDate = date.replace(/\./g, '-').replace(/\s/g, '');
  const startAt = `${normalizedDate}T${time}:00`;
  
  // endAt: startAt에서 30분 추가
  const startDateObj = new Date(startAt);
  startDateObj.setMinutes(startDateObj.getMinutes() + 30);
  const endAt = startDateObj.toISOString().replace('Z', '').slice(0, 19);
  
  const payload = {
    name: form.value.name,
    job: form.value.position || " ",
    status: form.value.status,
    startAt,
    endAt,
    interviewers: interviewersArr.join(', '),
    roomName: form.value.room,
    score: form.value.score ?? 0
  };
  
  console.log('지원자 수정 payload:', payload);
  
  try {
    await axios.put(`http://3.38.218.18:8080/api/v1/interviewees/${form.value.id}`, payload);
    await fetchCandidates();
    closeModal();
    alert('지원자 수정 성공!');
  } catch (e) {
    console.error('지원자 수정 실패:', e);
    alert('지원자 수정 실패');
  }
}

// 삭제
function openDeleteModal(candidate: Candidate) {
  deletingCandidate.value = candidate;
  showDeleteModal.value = true;
}

async function confirmDeleteCandidate() {
  if (!deletingCandidate.value) return;
  
  try {
    await axios.delete(`http://3.38.218.18:8080/api/v1/interviews/${deletingCandidate.value.interviewId}/interviewees/${deletingCandidate.value.id}`);
    await fetchCandidates();
    alert('삭제 성공!');
  } catch (e) {
    console.error('삭제 실패:', e);
    alert('삭제 실패');
  } finally {
    showDeleteModal.value = false;
    deletingCandidate.value = null;
  }
}

// 유틸리티 함수들
function formatDate(dateString: string) {
  if (!dateString) return '-';
  
  try {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  } catch {
    return dateString;
  }
}

function getStatusText(status: string) {
  switch ((status || '').toUpperCase()) {
    case 'SCHEDULED': return '예정';
    case 'IN_PROGRESS': return '진행중';
    case 'COMPLETED': return '완료';
    case 'CANCELLED': return '취소';
    case 'UNDECIDED': return '미정';
    default: return status;
  }
}

</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-in-out;
}

/* 테이블 호버 효과 개선 */
tbody tr:hover {
  background-color: #f8fafc;
}

/* 필터 태그 호버 효과 */
.px-2.py-1.bg-blue-100:hover {
  background-color: #dbeafe;
}

/* 스크롤바 스타일링 */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>