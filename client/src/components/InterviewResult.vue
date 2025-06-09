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
        <!-- 역량별 평가 (5개 항목, 아이콘별 색상) -->
        <div id="competency-evaluation" class="mb-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-6">역량별 평가</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="(item, i) in fixedKeywordList" :key="i" class="bg-gray-50 rounded-lg p-6">
              <div class="flex justify-between items-center mb-4">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 rounded-full flex items-center justify-center"
                    :class="item.bgClass">
                    <i :class="item.icon + ' text-2xl ' + item.iconColor"></i>
                  </div>
                  <h4 class="text-lg font-semibold text-gray-900">{{ item.category }}</h4>
                </div>
                <div class="flex items-center gap-2">
                  <div class="text-2xl font-bold" :class="item.textColor">
                    {{ item.score ?? '-' }}
                  </div>
                  <span class="text-gray-500">/ 100</span>
                </div>
              </div>
              <p class="text-gray-700">{{ item.reason ?? '해당 평가 항목에 대한 데이터가 없습니다.' }}</p>
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
        <!-- 종합 평가 -->
        <div id="overall-evaluation" class="mb-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-6">종합 평가</h3>
          <div class="bg-gray-50 rounded-lg p-6">
            <p class="text-gray-700 leading-relaxed">{{ result.feedback }}</p>
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
import { ref, computed, defineProps, defineEmits, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 카테고리별 기본 아이콘/색상 세팅
const competencyConfig = [
  {
    category: '문제 해결 능력',
    icon: 'fas fa-lightbulb',
    iconColor: 'text-green-600',
    bgClass: 'bg-green-100',
    textColor: 'text-green-600'
  },
  {
    category: '커뮤니케이션',
    icon: 'fas fa-comments',
    iconColor: 'text-blue-600',
    bgClass: 'bg-blue-100',
    textColor: 'text-blue-600'
  },
  {
    category: '전문성',
    icon: 'fas fa-code',
    iconColor: 'text-purple-600',
    bgClass: 'bg-purple-100',
    textColor: 'text-purple-600'
  },
  {
    category: '팀워크',
    icon: 'fas fa-users',
    iconColor: 'text-orange-600',
    bgClass: 'bg-orange-100',
    textColor: 'text-orange-600'
  },
  {
    category: '리더십',
    icon: 'fas fa-crown',
    iconColor: 'text-yellow-600',
    bgClass: 'bg-yellow-100',
    textColor: 'text-yellow-600'
  }
];

const props = defineProps<{
  interviewResults: any[]
  selectedCandidates: string[]
  initialTab?: number
}>();

const emit = defineEmits(['close', 'download']);

const tab = ref(props.initialTab ?? 0);
const result = computed(() => props.interviewResults[tab.value]);

// 항목이 빠져있어도 5개 항목을 모두 채워서 보여줌
const fixedKeywordList = computed(() => {
  // 실제 받은 평가 배열
  const evalArr = result.value?.evaluationKeywords || [];
  // 5개 고정 카테고리 loop
  return competencyConfig.map(conf => {
    const found = evalArr.find((e: { category: string; score?: number; reason?: string }) => e.category === conf.category);
    return {
      ...conf,
      score: found?.score ?? null,
      reason: found?.reason ?? null
    };
  });
});

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
  document.addEventListener('click', (event) => {
    const target = event.target as HTMLElement;
    if (!target.closest('.relative') && showTocDropdown.value) {
      showTocDropdown.value = false;
    }
  });
});
</script>

<style scoped>
/* 스크롤바 등 스타일 보강은 여기에! */
</style>
