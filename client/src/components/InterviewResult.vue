<template>
  <div class="min-h-screen bg-white py-8 px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">면접 결과</h1>
          <router-link to="/" class="text-[#FF7A00] hover:text-[#E60012]">
            <i class="fas fa-arrow-left mr-2"></i>대시보드로 돌아가기
          </router-link>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Candidate Info -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div class="flex justify-between items-start">
          <div>
            <h2 class="text-xl font-semibold text-gray-900">{{ candidateName }}님의 면접 결과</h2>
            <p class="text-gray-600 mt-1">면접 일시: {{ formattedDate }}</p>
          </div>
          <div class="flex space-x-4">
            <button @click="downloadPdf" class="!rounded-button whitespace-nowrap px-4 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200">
              <i class="fas fa-download mr-2"></i>PDF 다운로드
            </button>
            <button @click="sendEmail" class="!rounded-button whitespace-nowrap px-4 py-2 bg-[#FF7A00] text-white hover:bg-[#e66e00]">
              <i class="fas fa-envelope mr-2"></i>이메일 전송
            </button>
          </div>
        </div>
      </div>

      <!-- Score Section -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <!-- Overall Score -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">종합 점수</h3>
          <div class="flex items-center justify-center">
            <div class="relative w-48 h-48">
              <div ref="scoreChart" class="w-full h-full"></div>
            </div>
          </div>
        </div>

        <!-- Assessment Categories -->
        <div class="bg-white rounded-lg shadow-sm p-6 lg:col-span-2">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">평가 항목</h3>
          <div class="space-y-4">
            <div v-for="(category, index) in assessmentCategories" :key="index" class="flex items-center">
              <div class="w-32 text-sm text-gray-600">{{ category.name }}</div>
              <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-[#FF7A00] rounded-full"
                  :style="{ width: `${category.score}%` }"
                ></div>
              </div>
              <div class="w-16 text-right text-sm font-medium text-gray-900">{{ category.score }}%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Assessment -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Strengths -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">강점</h3>
          <ul class="space-y-2">
            <li v-for="(strength, index) in strengths" :key="index" class="flex items-start">
              <i class="fas fa-check-circle text-green-500 mt-1 mr-2"></i>
              <span class="text-gray-700">{{ strength }}</span>
            </li>
          </ul>
        </div>

        <!-- Areas for Improvement -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">개선 사항</h3>
          <ul class="space-y-2">
            <li v-for="(area, index) in areasForImprovement" :key="index" class="flex items-start">
              <i class="fas fa-exclamation-circle text-[#FF7A00] mt-1 mr-2"></i>
              <span class="text-gray-700">{{ area }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Overall Assessment -->
      <div class="bg-white rounded-lg shadow-sm p-6 mt-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">종합 평가</h3>
        <p class="text-gray-700 whitespace-pre-line">{{ overallAssessment }}</p>
      </div>

      <!-- Interviewer Notes -->
      <div class="bg-white rounded-lg shadow-sm p-6 mt-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">면접관 코멘트</h3>
        <div class="space-y-4">
          <div v-for="(note, index) in interviewerNotes" :key="index" class="border-l-4 border-[#FF7A00] pl-4">
            <p class="text-gray-700">{{ note }}</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue';
import * as echarts from 'echarts';
import { useRoute } from 'vue-router';

const route = useRoute();

// Data
const score = ref(78);
const candidateName = ref(route.query.candidateName as string || 'Michael Johnson');
const interviewDate = ref(new Date().toLocaleDateString('en-US', {
  year: 'numeric',
  month: 'long',
  day: 'numeric'
}));
const formattedDate = computed(() => new Date().toLocaleDateString('en-US', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric'
}));

const overallAssessment = ref(`지원자는 전반적으로 우수한 역량을 보여주었습니다. 특히 기술적 전문성과 의사소통 능력이 뛰어나며, 팀 프로젝트 경험도 풍부합니다. 문제 해결에 대한 창의적인 접근 방식이 인상적이었습니다.

다만, 일부 기술적 영역에서 추가적인 학습이 필요해 보이며, 프레젠테이션 스킬과 시간 관리 능력에서 개선의 여지가 있습니다. 이러한 부분들을 보완한다면 더욱 뛰어난 성과를 낼 수 있을 것으로 기대됩니다.

전반적으로 이 직무에 적합한 역량을 갖추고 있으며, 회사의 문화와도 잘 맞을 것으로 판단됩니다.`);

const strengths = ref([
  '기술적 전문성이 뛰어남',
  '명확하고 논리적인 의사소통',
  '프로젝트 경험 풍부',
  '팀 협업 능력이 우수함',
  '문제 해결에 대한 창의적 접근'
]);

const areasForImprovement = ref([
  '일부 기술적 영역에서 추가 학습 필요',
  '프레젠테이션 스킬 향상 필요',
  '시간 관리 능력 개선 필요'
]);

const assessmentCategories = ref([
  { name: '전문성', score: 85 },
  { name: '의사소통', score: 90 },
  { name: '문제해결', score: 75 },
  { name: '팀워크', score: 80 },
  { name: '적응력', score: 88 }
]);

const interviewerNotes = ref([
  '기술적 질문에 대해 깊이 있는 이해를 보여줌',
  '실무 경험을 바탕으로 한 구체적인 사례 제시가 인상적',
  '팀 프로젝트 경험에서 리더십 역량이 돋보임',
  '회사에 대한 이해도가 높고 지원 동기가 명확함'
]);

const scoreChart = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;

onMounted(() => {
  if (scoreChart.value) {
    chart = echarts.init(scoreChart.value);
    
    const option = {
      series: [
        {
          type: 'gauge',
          startAngle: 90,
          endAngle: -270,
          pointer: {
            show: false
          },
          progress: {
            show: true,
            overlap: false,
            roundCap: true,
            clip: false,
            itemStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: '#E60012' // SK Group red
                  },
                  {
                    offset: 1,
                    color: '#FF7A00' // Orange
                  }
                ]
              }
            }
          },
          axisLine: {
            lineStyle: {
              width: 12,
              color: [
                [1, '#E8E8E8']
              ]
            }
          },
          splitLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            show: false
          },
          data: [
            {
              value: score.value,
              name: 'Score',
              title: {
                show: true,
                offsetCenter: [0, '30%'],
                fontSize: 14,
                color: '#666'
              },
              detail: {
                show: true,
                offsetCenter: [0, '-10%'],
                fontSize: 24,
                fontWeight: 'bold',
                color: '#FF7A00',
                formatter: '{value}/100'
              }
            }
          ],
          animation: false
        }
      ]
    };
    
    chart.setOption(option);
  }
});

// Methods
const downloadPdf = () => {
  // In a real application, this would generate and download a PDF
  alert('Downloading interview results as PDF...');
};

const sendEmail = () => {
  // In a real application, this would send an email
  alert('Sending interview results via email...');
};
</script>

<style scoped>
/* Pretendard 폰트 적용 */
:root {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
  background-color: white;
}

/* 전체 배경색 하얀색으로 설정 */
body {
  background-color: white;
}

/* 전체 텍스트에 Pretendard 폰트 적용 */
* {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}

/* Custom styles that can't be handled by Tailwind */
.rounded-button {
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

/* Ensure the chart container maintains aspect ratio */
.chart-container {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
}

.chart-container > div {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style> 