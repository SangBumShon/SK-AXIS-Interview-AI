<template>
  <div class="fixed inset-0 bg-white z-50 overflow-auto">
    <div class="container mx-auto px-4 py-6">
      <!-- 헤더 -->
      <div class="flex justify-between items-center mb-6 sticky top-0 bg-white z-10 py-4 border-b border-gray-200">
        <div class="flex items-center gap-4">
          <h2 class="text-2xl font-bold">
            <span class="text-red-600">SK</span><span class="text-orange-500">AXIS</span>
            <span class="text-gray-900 ml-2">면접 결과 보고서</span>
          </h2>
          <div class="flex items-center gap-2 ml-6">
            <div v-for="(candidate, idx) in selectedCandidates" :key="idx"
              @click="setTab(idx)"
              class="px-4 py-2 rounded-md cursor-pointer transition-colors"
              :class="tab === idx ? 'bg-red-100 text-red-700 font-medium' : 'bg-gray-100 text-gray-700'">
              {{ candidate }}
            </div>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <!-- 목차 TOC 드롭다운 -->
          <div class="relative">
            <button @click="toggleTocDropdown"
              class="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors !rounded-button whitespace-nowrap cursor-pointer">
              <i class="fas fa-list-ul text-gray-700"></i>
              <span class="text-gray-700">목차</span>
              <i class="fas fa-chevron-down text-gray-500 text-xs"></i>
            </button>
            <div v-if="showTocDropdown" class="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-20">
              <div class="p-2">
                <div v-for="section in tocSections" :key="section.id"
                  @click="scrollToSection(section.id)"
                  class="px-3 py-2 hover:bg-gray-50 rounded cursor-pointer text-gray-700 text-sm">
                  {{ section.title }}
                </div>
              </div>
            </div>
          </div>
          <button @click="emitClose" class="text-gray-400 hover:text-gray-600">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>
      </div>
      <!-- 결과 본문 -->
      <div v-if="result" class="bg-white rounded-lg p-8">
        <!-- 기본 정보 -->
        <div id="basic-info" class="mb-8 bg-gray-50 rounded-lg p-6">
          <div class="grid grid-cols-2 gap-6">
            <div>
              <h3 class="text-xl font-bold text-gray-900 mb-4">면접자 정보</h3>
              <div class="space-y-2">
                <p class="text-gray-700"><span class="font-medium">이름:</span> {{ result.candidateInfo.name }}</p>
                <p class="text-gray-700"><span class="font-medium">지원 직무:</span> {{ result.candidateInfo.position }}</p>
                <p class="text-gray-700"><span class="font-medium">지원 부서:</span> {{ result.candidateInfo.department }}</p>
              </div>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900 mb-4">면접 정보</h3>
              <div class="space-y-2">
                <p class="text-gray-700"><span class="font-medium">면접 일시:</span> {{ result.candidateInfo.interviewDate }}</p>
                <p class="text-gray-700"><span class="font-medium">면접 시간:</span> {{ result.candidateInfo.interviewTime }}</p>
                <p class="text-gray-700"><span class="font-medium">면접 장소:</span> {{ result.candidateInfo.room ?? '-' }}</p>
                <p class="text-gray-700"><span class="font-medium">면접관:</span> {{ result.candidateInfo.interviewers?.join(', ') ?? '-' }}</p>
              </div>
            </div>
          </div>
        </div>
        <!-- 종합 점수 -->
        <div id="total-score" class="mb-12 text-center">
          <div class="inline-block relative">
            <div class="w-56 h-56 rounded-full border-8 border-red-100 flex items-center justify-center bg-white shadow-lg">
              <div class="text-center">
                <div class="text-7xl font-bold text-red-600">
                  {{ result.score }}
                </div>
                <div class="text-gray-500 mt-2 text-xl">종합 점수</div>
              </div>
            </div>
          </div>
        </div>
        <!-- 역량별 평가 -->
        <div id="competency-evaluation" class="mb-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-6">역량별 평가</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="item in competencyConfig" :key="item.key" class="bg-gray-50 rounded-lg p-6">
              <div class="flex justify-between items-center mb-4">
                <div class="flex items-center gap-3">
                  <div :class="item.bg + ' w-12 h-12 rounded-full flex items-center justify-center'">
                    <i :class="item.icon + ' text-2xl ' + item.color"></i>
                  </div>
                  <h4 class="text-lg font-semibold text-gray-900">{{ item.label }}</h4>
                </div>
                <div class="flex items-center gap-2">
                  <div class="text-2xl font-bold" :class="item.color">
                    {{ result.value?.evaluationKeywords?.find((e: any) => e.category === item.key)?.score ?? '-' }}
                  </div>
                  <span class="text-gray-500">/ 15</span>
                </div>
              </div>
              <p class="text-gray-700">
                {{ getEvaluationText(item.key, result.value?.evaluationKeywords?.find((e: any) => e.category === item.key)?.score) }}
              </p>
            </div>
          </div>
        </div>
        <!-- 종합 평가 -->
        <div id="overall-evaluation" class="mb-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-6">종합 평가</h3>
          <div class="bg-gray-50 rounded-lg p-6 mb-6">
            <div class="mb-4">
              <span class="font-semibold text-gray-700">비중(전체 평가 점수에서의 비중):</span>
              <span class="ml-2 text-gray-900">{{ result.value?.overallEvaluation?.weight ?? '-' }}%</span>
            </div>
            <!-- 언어적 요소 -->
            <div class="mb-4">
              <h4 class="text-lg font-semibold text-red-600 mb-2">① 언어적 요소</h4>
              <div class="flex flex-wrap gap-6">
                <div>
                  <span class="font-medium text-gray-700">점수:</span>
                  <span class="ml-2 text-gray-900">{{ result.value?.overallEvaluation?.language?.score ?? '-' }}</span>
                </div>
                <div>
                  <span class="font-medium text-gray-700">총점(최대점수):</span>
                  <span class="ml-2 text-gray-900">{{ result.value?.overallEvaluation?.language?.maxScore ?? '-' }}</span>
                </div>
                <div class="w-full mt-2">
                  <span class="font-medium text-gray-700">사유:</span>
                  <span class="ml-2 text-gray-900">{{ result.value?.overallEvaluation?.language?.reason ?? '-' }}</span>
                </div>
              </div>
            </div>
            <!-- 비언어적 요소 -->
            <div class="mb-4">
              <h4 class="text-lg font-semibold text-blue-600 mb-2">② 비언어적 요소</h4>
              <div class="flex flex-wrap gap-6">
                <div>
                  <span class="font-medium text-gray-700">미소:</span>
                  <span class="ml-2 text-gray-900">
                    {{ result.value?.overallEvaluation?.nonverbal?.smileCount ?? '-' }}
                    <span v-if="result.value?.overallEvaluation?.nonverbal?.totalCount">
                      / {{ result.value?.overallEvaluation?.nonverbal?.totalCount }} ({{ getPercent(result.value?.overallEvaluation?.nonverbal?.smileCount, result.value?.overallEvaluation?.nonverbal?.totalCount) }}%)
                    </span>
                  </span>
                </div>
                <div>
                  <span class="font-medium text-gray-700">울상:</span>
                  <span class="ml-2 text-gray-900">
                    {{ result.value?.overallEvaluation?.nonverbal?.frownCount ?? '-' }}
                    <span v-if="result.value?.overallEvaluation?.nonverbal?.totalCount">
                      / {{ result.value?.overallEvaluation?.nonverbal?.totalCount }} ({{ getPercent(result.value?.overallEvaluation?.nonverbal?.frownCount, result.value?.overallEvaluation?.nonverbal?.totalCount) }}%)
                    </span>
                  </span>
                </div>
                <div>
                  <span class="font-medium text-gray-700">무표정:</span>
                  <span class="ml-2 text-gray-900">
                    {{ result.value?.overallEvaluation?.nonverbal?.neutralCount ?? '-' }}
                    <span v-if="result.value?.overallEvaluation?.nonverbal?.totalCount">
                      / {{ result.value?.overallEvaluation?.nonverbal?.totalCount }} ({{ getPercent(result.value?.overallEvaluation?.nonverbal?.neutralCount, result.value?.overallEvaluation?.nonverbal?.totalCount) }}%)
                    </span>
                  </span>
                </div>
                <div>
                  <span class="font-medium text-gray-700">제스처:</span>
                  <span class="ml-2 text-gray-900">
                    {{ result.value?.overallEvaluation?.nonverbal?.gestureCount ?? '-' }}
                    <span v-if="result.value?.overallEvaluation?.nonverbal?.totalCount">
                      / {{ result.value?.overallEvaluation?.nonverbal?.totalCount }} ({{ getPercent(result.value?.overallEvaluation?.nonverbal?.gestureCount, result.value?.overallEvaluation?.nonverbal?.totalCount) }}%)
                    </span>
                  </span>
                </div>
                <div>
                  <span class="font-medium text-gray-700">시선:</span>
                  <span class="ml-2 text-gray-900">
                    {{ result.value?.overallEvaluation?.nonverbal?.gazeCount ?? '-' }}
                    <span v-if="result.value?.overallEvaluation?.nonverbal?.totalCount">
                      / {{ result.value?.overallEvaluation?.nonverbal?.totalCount }} ({{ getPercent(result.value?.overallEvaluation?.nonverbal?.gazeCount, result.value?.overallEvaluation?.nonverbal?.totalCount) }}%)
                    </span>
                  </span>
                </div>
                <div>
                  <span class="font-medium text-gray-700">점수:</span>
                  <span class="ml-2 text-gray-900">{{ result.value?.overallEvaluation?.nonverbal?.score ?? '-' }}</span>
                </div>
                <div>
                  <span class="font-medium text-gray-700">총점(최대점수):</span>
                  <span class="ml-2 text-gray-900">{{ result.value?.overallEvaluation?.nonverbal?.maxScore ?? '-' }}</span>
                </div>
                <div class="w-full mt-2">
                  <span class="font-medium text-gray-700">사유:</span>
                  <span class="ml-2 text-gray-900">{{ result.value?.overallEvaluation?.nonverbal?.reason ?? '-' }}</span>
                </div>
              </div>
            </div>
            <!-- 전체 총점 및 사유 -->
            <div class="mt-6">
              <div>
                <span class="font-semibold text-gray-700">총점:</span>
                <span class="ml-2 text-gray-900">{{ result.value?.overallEvaluation?.totalScore ?? '-' }}</span>
                <span class="mx-2 text-gray-500">/</span>
                <span class="text-gray-900">{{ result.value?.overallEvaluation?.totalMaxScore ?? '-' }}</span>
              </div>
              <div class="mt-2">
                <span class="font-semibold text-gray-700">총점에 대한 전체 사유:</span>
                <span class="ml-2 text-gray-900">{{ result.value?.overallEvaluation?.totalReason ?? '-' }}</span>
              </div>
            </div>
          </div>
        </div>
        <!-- 면접 질문 및 답변 -->
        <div id="interview-content" class="mb-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-6">면접 내용 요약</h3>
          <div class="space-y-6">
            <div v-for="(question, qIdx) in result.questions" :key="qIdx"
              class="bg-gray-50 rounded-lg p-6">
              <div class="mb-4">
                <h4 class="text-lg font-semibold text-gray-900 mb-2">
                  Q{{ qIdx + 1 }}. {{ question }}
                </h4>
                <p class="text-gray-700 pl-6">A: {{ result.answers[qIdx] }}</p>
              </div>
            </div>
          </div>
        </div>
        <!-- 다운로드 버튼 -->
        <div id="download-section" class="mt-12 text-center">
          <button @click="emitDownload"
            class="bg-red-600 text-white px-12 py-4 rounded-lg hover:bg-red-700 text-xl font-bold shadow-lg transform transition hover:scale-105 !rounded-button whitespace-nowrap cursor-pointer inline-flex items-center gap-3">
            <i class="fas fa-file-pdf text-2xl"></i>
            면접 결과 리포트 다운로드
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineProps, defineEmits, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

// 카테고리별 기본 아이콘/색상 세팅
const competencyConfig = [
  { key: 'SUPEX', label: 'SUPEX', icon: 'fas fa-star', color: 'text-red-600', bg: 'bg-red-100' },
  { key: 'VWBE', label: 'VWBE', icon: 'fas fa-bolt', color: 'text-orange-600', bg: 'bg-orange-100' },
  { key: 'Passionate', label: 'Passionate', icon: 'fas fa-fire', color: 'text-yellow-600', bg: 'bg-yellow-100' },
  { key: 'Proactive', label: 'Proactive', icon: 'fas fa-running', color: 'text-green-600', bg: 'bg-green-100' },
  { key: 'Professional', label: 'Professional', icon: 'fas fa-user-tie', color: 'text-blue-600', bg: 'bg-blue-100' },
  { key: 'People', label: 'People', icon: 'fas fa-users', color: 'text-purple-600', bg: 'bg-purple-100' },
  { key: '기술.직무', label: '기술/직무', icon: 'fas fa-cogs', color: 'text-pink-600', bg: 'bg-pink-100' },
  { key: '도메인 전문성', label: '도메인 전문성', icon: 'fas fa-brain', color: 'text-gray-600', bg: 'bg-gray-100' }
];

const props = defineProps<{
  interviewResults: any[]
  selectedCandidates: string[]
  initialTab?: number
}>();

const emit = defineEmits(['close', 'download']);

const tab = ref(props.initialTab ?? 0);
const result = computed(() => props.interviewResults[tab.value]);

// 폴링 관련 변수 및 함수
let pollingInterval: any = null;

async function fetchAllResults() {
  const ids = props.selectedCandidates.join(',');
  const response = await axios.get(`http://localhost:8000/api/v1/results?interviewee_ids=${ids}`);
  const results = response.data.results;
  for (let i = 0; i < props.selectedCandidates.length; i++) {
    const candidateId = props.selectedCandidates[i];
    const found = results.find((r: any) => r.interviewee_id == candidateId);
    if (found) {
      props.interviewResults[i] = found;
    }
  }
}

async function checkAllInterviewComplete() {
  try {
    const ids = props.selectedCandidates.join(',');
    const response = await axios.get(`http://localhost:8000/api/v1/results/statuses?interviewee_ids=${ids}`);
    const statuses = response.data;
    // 모두 DONE인지 확인
    const allDone = statuses.every((item: any) => item.status === 'DONE');
    if (allDone) {
      if (pollingInterval) clearInterval(pollingInterval);
      pollingInterval = null;
      // 결과 일괄 갱신
      await fetchAllResults();
    }
  } catch (err) {
    console.error('[폴링 오류]', err);
  }
}

function startPolling() {
  if (pollingInterval) clearInterval(pollingInterval);
  pollingInterval = setInterval(checkAllInterviewComplete, 1000); // 1초마다 폴링
}

function getEvaluationText(key: string, score: number | null) {
  if (score == null) return '평가 데이터가 없습니다.'
  switch (key) {
    case 'SUPEX':
      if (score >= 14) return 'SUPEX 정신이 충만하며, 자기 분야에 최고가 되려는 경향을 확실히 보임'
      if (score >= 11) return 'SUPEX 마인드가 우수하며, 도전정신이 뚜렷함'
      if (score >= 8)  return 'SUPEX 가치관이 평균 이상이나, 더 적극적인 자세가 필요함'
      if (score >= 4)  return 'SUPEX에 대한 이해와 실천이 다소 부족함'
      return 'SUPEX에 대한 관심과 실천 의지가 매우 부족함'
    case 'VWBE':
      if (score >= 14) return 'VWBE 실천이 탁월하며, 조직 내 소통과 협업이 매우 원활함'
      if (score >= 11) return 'VWBE 역량이 우수하며, 팀워크가 잘 발휘됨'
      if (score >= 8)  return 'VWBE 마인드가 평균 수준이나, 더 적극적인 협업이 필요함'
      if (score >= 4)  return 'VWBE 실천이 다소 미흡함'
      return 'VWBE에 대한 이해와 실천이 매우 부족함'
    case 'Passionate':
      if (score >= 14) return '열정적으로 업무에 임하며, 높은 동기부여를 보임'
      if (score >= 11) return '업무에 대한 열정이 뚜렷함'
      if (score >= 8)  return '열정이 평균 수준이나, 더 적극적인 태도가 필요함'
      if (score >= 4)  return '업무에 대한 열정이 다소 부족함'
      return '업무에 대한 열정과 의지가 매우 부족함'
    case 'Proactive':
      if (score >= 14) return '매우 적극적으로 문제를 해결하고, 주도적으로 행동함'
      if (score >= 11) return '적극적으로 업무에 임하며, 주도성이 우수함'
      if (score >= 8)  return '주도성은 평균 수준이나, 더 능동적인 자세가 필요함'
      if (score >= 4)  return '주도적 행동이 다소 부족함'
      return '주도성 및 적극성이 매우 부족함'
    case 'Professional':
      if (score >= 14) return '전문성이 매우 뛰어나며, 높은 수준의 업무 역량을 보임'
      if (score >= 11) return '전문성이 우수하며, 신뢰를 주는 업무 태도를 보임'
      if (score >= 8)  return '전문성은 평균 수준이나, 더 깊은 역량 개발이 필요함'
      if (score >= 4)  return '전문성 및 업무 이해도가 다소 부족함'
      return '전문성 및 업무 이해도가 매우 부족함'
    case 'People':
      if (score >= 14) return '대인관계가 매우 원만하며, 조직 내 신뢰가 높음'
      if (score >= 11) return '대인관계가 우수하며, 협업이 잘 이루어짐'
      if (score >= 8)  return '대인관계는 평균 수준이나, 더 원활한 소통이 필요함'
      if (score >= 4)  return '대인관계 및 소통 능력이 다소 부족함'
      return '대인관계 및 소통 능력이 매우 부족함'
    case '기술.직무':
      if (score >= 14) return '직무 관련 기술력이 매우 뛰어나며, 실무 역량이 탁월함'
      if (score >= 11) return '직무 역량이 우수하며, 실무에 강점을 보임'
      if (score >= 8)  return '직무 역량은 평균 수준이나, 추가 역량 개발이 필요함'
      if (score >= 4)  return '직무 역량이 다소 부족함'
      return '직무 역량 및 기술 이해도가 매우 부족함'
    case '도메인 전문성':
      if (score >= 14) return '도메인 전문성이 매우 뛰어나며, 깊은 이해를 보임'
      if (score >= 11) return '도메인 전문성이 우수함'
      if (score >= 8)  return '도메인 전문성은 평균 수준이나, 더 깊은 이해가 필요함'
      if (score >= 4)  return '도메인 전문성이 다소 부족함'
      return '도메인 전문성 및 이해도가 매우 부족함'
    default:
      return '평가 데이터가 없습니다.'
  }
}

function getPercent(count: number | null | undefined, total: number | null | undefined): string {
  if (!total || total === 0 || count == null) return '-';
  return ((count / total) * 100).toFixed(1);
}

// 목차
const tocSections = [
  { id: 'basic-info', title: '기본 정보' },
  { id: 'total-score', title: '종합 점수' },
  { id: 'competency-evaluation', title: '역량별 평가' },
  { id: 'interview-content', title: '면접 내용 요약' },
  { id: 'overall-evaluation', title: '종합 평가' },
  { id: 'download-section', title: '리포트 다운로드' }
];
const showTocDropdown = ref(false);
function toggleTocDropdown() {
  showTocDropdown.value = !showTocDropdown.value;
}
function scrollToSection(sectionId: string) {
  const el = document.getElementById(sectionId);
  if (el) el.scrollIntoView({ behavior: 'smooth' });
  showTocDropdown.value = false;
}

function setTab(idx: number) {
  tab.value = idx;
}
function emitClose() {
  emit('close');
  router.push('/');
}
function emitDownload() {
  emit('download', tab.value);
}

// 드롭다운 외부 클릭시 닫기
onMounted(() => {
  startPolling();
  document.addEventListener('click', (event) => {
    const target = event.target as HTMLElement;
    if (!target.closest('.relative') && showTocDropdown.value) {
      showTocDropdown.value = false;
    }
  });
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
});

watch(tab, () => {
  startPolling();
});
</script>

<style scoped>
/* 스크롤바 등 스타일 보강은 여기에! */
</style>
