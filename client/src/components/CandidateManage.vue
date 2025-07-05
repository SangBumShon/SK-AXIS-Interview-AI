<template>
  <!-- 지원자 관리 뷰 -->
  <div class="p-8 overflow-visible min-h-0 h-auto">
    <!-- 지원자 관리 헤더 -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900">지원자 관리</h2>
    </div>
    <!-- 필터 및 검색 -->
    <div class="bg-white rounded-lg p-6 mb-6 border border-gray-200">
      <div class="grid grid-cols-4 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">상태</label>
          <select v-model="filters.status" class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm">
            <option value="all">전체</option>
            <option value="면접 예정">면접 예정</option>
            <option value="면접 완료">면접 완료</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">면접 일정</label>
          <input type="date" v-model="filters.interviewDate" class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm">
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">검색</label>
          <div class="relative">
            <input type="text" v-model="filters.search" placeholder="이름 또는 직무 검색" class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm pr-10">
            <i class="fas fa-search absolute right-3 top-2.5 text-gray-400"></i>
          </div>
        </div>
      </div>
    </div>
    <!-- 지원자 목록 테이블 -->
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div class="p-4 border-b border-gray-100 flex justify-between items-center">
        <h2 class="text-lg font-medium text-gray-700">지원자 목록</h2>
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <label for="itemsPerPage" class="text-sm text-gray-500">페이지당</label>
            <select id="itemsPerPage" v-model.number="itemsPerPage" class="px-2 py-1 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option :value="8">8</option>
              <option :value="10">10</option>
              <option :value="15">15</option>
            </select>
            <span class="text-sm text-gray-500">개 보기</span>
          </div>
          <button @click="openAddModal" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2">
            <i class="fas fa-plus"></i>
            추가
          </button>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">날짜</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">시간</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">면접실</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">지원자</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">면접관</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">점수</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">관리</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="candidate in pagedCandidates" :key="candidate.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.interviewDate }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.interviewTime || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.room || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.name }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.interviewers ? candidate.interviewers.join(', ') : '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="{
                  'px-2 py-1 text-xs font-medium rounded-full': true,
                  'bg-green-100 text-green-800': candidate.status === 'COMPLETED',
                  'bg-yellow-100 text-yellow-800': candidate.status === 'SCHEDULED' || candidate.status === 'UNDECIDED',
                  'bg-blue-100 text-blue-800': candidate.status === 'IN_PROGRESS',
                  'bg-gray-100 text-gray-800': candidate.status === 'CANCELLED'
                }">{{ getStatusText(candidate.status) }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">{{ candidate.score ?? '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <button class="text-blue-600 hover:text-blue-800" @click="openEditModal(candidate)">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="text-red-600 hover:text-red-800" @click="openDeleteModal(candidate)">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- 페이지네이션 및 페이지당 개수 선택 UI (테두리 밖) -->
    <div class="relative px-4 pb-4 mt-6">
      <div class="absolute left-0 top-0 flex items-center gap-2">
        <label for="itemsPerPageCandidate" class="text-sm text-gray-500">페이지당</label>
        <select id="itemsPerPageCandidate" v-model.number="itemsPerPage" class="px-2 py-1 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
          <option :value="8">8</option>
          <option :value="10">10</option>
          <option :value="15">15</option>
        </select>
        <span class="text-sm text-gray-500">개 보기</span>
      </div>
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
    <!-- 적용 버튼: 테두리 안, 오른쪽 정렬 -->
    <div class="flex justify-end mt-4 mb-2">
      <button class="px-6 py-3 bg-orange-500 text-white rounded-lg shadow-lg hover:bg-orange-600 transition-colors" @click="reloadPage">적용</button>
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
            <input type="date" v-model="form.interviewDate" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">시간</label>
            <input type="text" v-model="form.interviewTime" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">면접실</label>
            <input type="text" v-model="form.room" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">지원자</label>
            <input type="text" v-model="form.name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">면접관 (쉼표로 구분)</label>
            <input type="text" v-model="form.interviewersString" placeholder="예: 김민수, 이지원" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">상태</label>
            <select v-model="form.status" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
              <option value="SCHEDULED">SCHEDULED</option>
              <option value="IN_PROGRESS">IN_PROGRESS</option>
              <option value="COMPLETED">COMPLETED</option>
              <option value="CANCELLED">CANCELLED</option>
              <option value="UNDECIDED">UNDECIDED</option>
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
            <label class="block text-sm font-medium text-gray-700 mb-1">점수</label>
            <input type="number" v-model="form.score" min="0" max="100" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="closeModal"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors whitespace-nowrap"
          >
            취소
          </button>
          <button
            @click="isEditing ? updateCandidate() : addCandidate()"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors whitespace-nowrap"
          >
            저장
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
const filters = ref({ status: 'all', interviewDate: '', search: '' });

// 모달 상태 및 폼
const showModal = ref(false);
const isEditing = ref(false);
const form = ref<Partial<Candidate & { interviewersString?: string }>>({});

// 삭제 모달 상태
const showDeleteModal = ref(false);
const deletingCandidate = ref<Candidate | null>(null);

// 목록 fetch 함수
async function fetchCandidates() {
  const response = await fetch('http://3.38.218.18:8080/api/v1/interviewees/simple');
  if (response.ok) {
    const result = await response.json();
    console.log('서버에서 받아온 최신 목록:', result.data);
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
        interviewId: item.interviewId,
        name: item.name,
        position: item.job,
        interviewers: item.interviewers ? (item.interviewers as string).split(',').map((s: any) => s.trim()) : [],
        status: item.status,
        interviewDate,
        score: item.score,
        interviewTime,
        room: item.roomNo
      };
    });
  }
}
onMounted(fetchCandidates);

// 필터/페이징 등 기존 computed 유지
const filteredCandidates = computed(() => {
  let filtered = [...candidateList.value];
  if (filters.value.status !== 'all') {
    filtered = filtered.filter(c => c.status === filters.value.status);
  }
  if (filters.value.interviewDate) {
    filtered = filtered.filter(c => c.interviewDate === filters.value.interviewDate);
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase();
    filtered = filtered.filter(c =>
      c.name.toLowerCase().includes(search) ||
      c.position.toLowerCase().includes(search)
    );
  }
  return filtered;
});

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
watch(itemsPerPage, () => { currentPage.value = 1; });
const visiblePages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1);
  if (current <= 3) return [1, 2, 3, 4, 5];
  if (current >= total - 2) return [total - 4, total - 3, total - 2, total - 1, total].filter(p => p > 0);
  return [current - 2, current - 1, current, current + 1, current + 2];
});

// 모달 열기/닫기
function openAddModal() {
  isEditing.value = false;
  form.value = {};
  showModal.value = true;
}
function openEditModal(candidate: Candidate) {
  isEditing.value = true;
  form.value = { ...candidate, interviewersString: candidate.interviewers?.join(', ') };
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
  const date = form.value.interviewDate ?? '';
  const time = form.value.interviewTime ?? '00:00';
  const startAt = date && time ? `${date}T${time}:00` : '';
  if (!startAt) {
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
  // 날짜 포맷 변환: '2025. 07. 03.' → '2025-07-03'
  let rawDate = form.value.interviewDate ?? '';
  rawDate = rawDate.replace(/\./g, '').replace(/\s/g, '').replace(/-+/g, '');
  if (/^\d{8}$/.test(rawDate)) {
    rawDate = `${rawDate.slice(0,4)}-${rawDate.slice(4,6)}-${rawDate.slice(6,8)}`;
  }
  const time = form.value.interviewTime ?? '00:00';
  // year, month, day, hour, minute로 분리해서 로컬 Date 객체 생성
  const [year, month, day] = rawDate.split('-').map(Number);
  const [hour, minute] = time.split(':').map(Number);
  const localDate = new Date(year, month - 1, day, hour, minute);
  const startAt = localDate.toISOString();
  // endAt: startAt에서 30분 더하기
  let endAt = startAt;
  if (startAt) {
    const startDateObj = new Date(localDate);
    startDateObj.setMinutes(startDateObj.getMinutes() + 30);
    endAt = startDateObj.toISOString();
  }
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
    alert('지원자 추가 실패');
  }
}

// 지원자 수정 함수 (PUT)
async function updateCandidate() {
  if (!validateCandidateForm()) return;
  const interviewersArr = form.value.interviewersString
    ? form.value.interviewersString.split(',').map(s => s.trim()).filter(Boolean)
    : [];
  const rawDate = form.value.interviewDate ?? '';
  let normalizedDate = rawDate.replace(/\./g, '-').replace(/\s/g, '');
  normalizedDate = normalizedDate.replace(/^-+|-+$/g, '').replace(/-+/g, '-');
  const dateParts = normalizedDate.split('-').filter(Boolean);
  if (dateParts.length === 3) {
    normalizedDate = `${dateParts[0]}-${dateParts[1].padStart(2, '0')}-${dateParts[2].padStart(2, '0')}`;
  }
  const time = form.value.interviewTime ?? '00:00';
  const startAt = normalizedDate && time ? `${normalizedDate}T${time}:00` : '';
  // endAt: startAt에서 30분 더하기
  let endAt = startAt;
  if (startAt) {
    const startDateObj = new Date(startAt);
    startDateObj.setMinutes(startDateObj.getMinutes() + 30);
    endAt = `${startDateObj.getFullYear()}-${String(startDateObj.getMonth() + 1).padStart(2, '0')}-${String(startDateObj.getDate()).padStart(2, '0')}T${String(startDateObj.getHours()).padStart(2, '0')}:${String(startDateObj.getMinutes()).padStart(2, '0')}:00`;
  }
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
    alert('삭제 실패');
  } finally {
    showDeleteModal.value = false;
    deletingCandidate.value = null;
  }
}

function reloadPage() {
  window.location.reload();
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
/* 필요한 스타일 */
</style> 