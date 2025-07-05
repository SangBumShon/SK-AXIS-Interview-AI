<template>
  <!-- 통계 분석 모달 -->
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-8 max-w-6xl w-full mx-4 relative animate-fadeIn overflow-auto max-h-[90vh]">
      <button @click="$emit('close')" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
        <i class="fas fa-times"></i>
      </button>
      <div class="mb-8">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">면접 통계 분석</h2>
          <div class="flex items-center gap-4">
            <div class="relative">
              <select :value="statisticsFilter.period" @change="updateFilter('period', ($event.target as HTMLSelectElement).value)" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500">
                <option value="all">전체 기간</option>
                <option value="month">이번 달</option>
                <option value="quarter">이번 분기</option>
                <option value="year">올해</option>
              </select>
            </div>
          </div>
        </div>
        <!-- Statistics Dashboard -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- 면접자 점수 분포 -->
          <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-800">면접자 점수 분포</h3>
            <div class="h-80" ref="scoreDistributionChartRef"></div>
          </div>
          <!-- 역량별 평균 면접 점수 -->
          <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-800">역량별 평균 면접 점수</h3>
            <div class="h-80" ref="avgScoreChartRef"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { defineProps, defineEmits, ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

const props = defineProps<{ statisticsFilter: any }>();
const emits = defineEmits(['close', 'updateStatisticsFilter']);

// 필터 업데이트 함수
function updateFilter(key: string, value: string) {
  emits('updateStatisticsFilter', { ...props.statisticsFilter, [key]: value });
}

// 차트 ref
const scoreDistributionChartRef = ref(null);
const avgScoreChartRef = ref(null);

let scoreDistributionChart = null;
let avgScoreChart = null;

// 차트 초기화 함수
const initCharts = async () => {
  // 면접자 점수 데이터 fetch
  const bins = [0, 0, 0, 0, 0];
  try {
    const res = await axios.get('http://3.38.218.18:8080/api/v1/interviewees/simple');
    const scores = res.data.data.map((item: any) => item.score ?? 0);
    scores.forEach((score: number) => {
      if (score >= 1 && score <= 20) bins[0]++;
      else if (score >= 21 && score <= 40) bins[1]++;
      else if (score >= 41 && score <= 60) bins[2]++;
      else if (score >= 61 && score <= 80) bins[3]++;
      else if (score >= 81 && score <= 100) bins[4]++;
    });
  } catch (e) {
    // 에러 시 더미 데이터 유지
  }

  if (scoreDistributionChartRef.value) {
    scoreDistributionChart = echarts.init(scoreDistributionChartRef.value);
    scoreDistributionChart.setOption({

      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['1-20', '21-40', '41-60', '61-80', '81-100']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: bins,
          type: 'bar'
        }
      ]
    });
  }

  if (avgScoreChartRef.value) {
    avgScoreChart = echarts.init(avgScoreChartRef.value);
    avgScoreChart.setOption({
  
      tooltip: {
        trigger: 'axis'
      },
      radar: {
        indicator: [
          { name: 'SUPEX', max: 100 },
          { name: 'VWBE', max: 100 },
          { name: 'Passionate', max: 100 },
          { name: 'Proactive', max: 100 },
          { name: 'Professional', max: 100 },
          { name: 'People', max: 100 }
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

// 차트 업데이트 함수(필요시)
const updateCharts = () => {
  // 여기에 차트 데이터 업데이트 로직 추가
};

onMounted(() => {
  initCharts();
});

watch(() => props.statisticsFilter, () => {
  updateCharts();
}, { deep: true });
</script>
<style scoped>
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fadeIn {
  animation: fadeIn 0.3s ease-in-out;
}
</style> 