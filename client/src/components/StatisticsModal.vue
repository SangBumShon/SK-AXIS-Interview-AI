<template>
  <!-- 통계 분석 모달 - 고도화 버전 -->
  <div class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-3xl shadow-2xl max-w-7xl w-full mx-4 relative animate-slideUp max-h-[95vh]" ref="modalRef">
      <!-- 헤더 -->
      <div class="bg-gradient-to-r from-red-500 to-orange-500 p-8 text-white relative">
        <!-- 배경 패턴 -->
        <div class="absolute inset-0 opacity-10">
          <div class="absolute top-4 right-4 w-32 h-32 border border-white rounded-full"></div>
          <div class="absolute bottom-4 left-4 w-24 h-24 border border-white rounded-full"></div>
          <div class="absolute top-1/2 left-1/3 w-16 h-16 border border-white rounded-full"></div>
        </div>
        
        <div class="relative z-10 flex justify-between items-center">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
              <i class="fas fa-chart-line text-3xl"></i>
            </div>
            <div>
              <h2 class="text-3xl font-bold mb-2">면접 통계 분석</h2>
              <p class="text-white text-opacity-90">데이터 기반 면접 인사이트를 확인하세요</p>
            </div>
          </div>
          
          <div class="flex items-center gap-4">
            <!-- 커스텀 드롭다운 -->
            <div class="relative" ref="dropdownRef">
              <button 
                @click="toggleDropdown"
                class="bg-white bg-opacity-20 backdrop-blur-sm rounded-xl px-4 py-3 text-white font-medium cursor-pointer hover:bg-opacity-30 transition-all duration-200 flex items-center gap-3 min-w-32"
              >
                <span>{{ getPeriodLabel(statisticsFilter.period) }}</span>
                <i class="fas fa-chevron-down transition-transform duration-200" :class="{ 'rotate-180': isDropdownOpen }"></i>
              </button>
              
              <!-- 드롭다운 메뉴 - Teleport로 body에 렌더링 -->
              <Teleport to="body">
                <div 
                  v-if="isDropdownOpen"
                  class="fixed bg-white rounded-xl shadow-2xl border border-gray-100 z-[10000] min-w-[150px]"
                  :style="dropdownStyle"
                >
                  <button
                    v-for="option in periodOptions"
                    :key="option.value"
                    @click="selectPeriod(option.value)"
                    class="w-full px-4 py-3 text-left text-gray-700 hover:bg-gray-50 transition-colors duration-150 font-medium block whitespace-nowrap first:rounded-t-xl last:rounded-b-xl"
                    :class="{ 'bg-red-50 text-red-600': statisticsFilter.period === option.value }"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </Teleport>
            </div>
            
            <!-- 닫기 버튼 -->
            <button 
              @click="$emit('close')" 
              class="w-12 h-12 bg-white bg-opacity-20 backdrop-blur-sm rounded-xl flex items-center justify-center hover:bg-opacity-30 transition-all duration-200 group"
            >
              <i class="fas fa-times text-xl group-hover:rotate-90 transition-transform duration-200"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 컨텐츠 -->
      <div class="p-8 overflow-y-auto max-h-[calc(95vh-200px)] bg-gradient-to-br from-gray-50 to-white" ref="reportContentRef">
        <!-- 요약 통계 카드들 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center">
                <i class="fas fa-users text-blue-600 text-xl"></i>
              </div>
              <div>
                <p class="text-gray-600 text-sm font-medium">총 면접자</p>
                <p class="text-3xl font-bold text-gray-900" ref="totalCandidatesRef">{{ totalCandidates }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-green-100 rounded-2xl flex items-center justify-center">
                <i class="fas fa-chart-line text-green-600 text-xl"></i>
              </div>
              <div>
                <p class="text-gray-600 text-sm font-medium">평균 점수</p>
                <p class="text-3xl font-bold text-gray-900" ref="avgScoreRef">{{ averageScore.toFixed(1) }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-purple-100 rounded-2xl flex items-center justify-center">
                <i class="fas fa-trophy text-purple-600 text-xl"></i>
              </div>
              <div>
                <p class="text-gray-600 text-sm font-medium">최고 점수</p>
                <p class="text-3xl font-bold text-gray-900" ref="maxScoreRef">{{ maxScore }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 차트 섹션 -->
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
          <!-- 면접자 점수 분포 -->
          <div class="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
            <div class="bg-gradient-to-r from-blue-50 to-blue-100 p-6 border-b border-blue-200">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center">
                  <i class="fas fa-chart-bar text-white"></i>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-gray-900">면접자 점수 분포</h3>
                  <p class="text-blue-700 text-sm">점수 구간별 면접자 수</p>
                </div>
              </div>
            </div>
            <div class="p-6">
              <div class="h-80" ref="scoreDistributionChartRef"></div>
            </div>
          </div>

          <!-- 역량별 평균 면접 점수 -->
          <div class="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
            <div class="bg-gradient-to-r from-green-50 to-green-100 p-6 border-b border-green-200">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center">
                  <i class="fas fa-radar-chart text-white"></i>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-gray-900">역량별 평균 점수</h3>
                  <p class="text-green-700 text-sm">6개 핵심 역량 분석</p>
                </div>
              </div>
            </div>
            <div class="p-6">
              <div class="h-80" ref="avgScoreChartRef"></div>
            </div>
          </div>
        </div>

        <!-- 액션 버튼 -->
        <div class="flex justify-end gap-4">
          <button 
            @click="downloadReport" 
            class="px-6 py-3 bg-blue-100 text-blue-700 rounded-xl hover:bg-blue-200 transition-all duration-200 font-medium flex items-center gap-2 hover:shadow-lg"
          >
            <i class="fas fa-file-alt"></i>
            JSON 다운로드
          </button>
          <button 
            @click="shareResults" 
            class="px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-200 shadow-lg hover:shadow-xl font-medium flex items-center gap-2"
          >
            <i class="fas fa-share-alt"></i>
            결과 공유
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';
import type { ECharts } from 'echarts';

interface Props {
  statisticsFilter: {
    period: string;
  };
}

const props = defineProps<Props>();
const emits = defineEmits(['close', 'updateStatisticsFilter']);

// 드롭다운 상태 관리
const isDropdownOpen = ref(false);
const dropdownRef = ref<HTMLElement | null>(null);
const dropdownStyle = ref({});

// 기간 옵션
const periodOptions = [
  { value: 'all', label: '전체 기간' },
  { value: 'month', label: '이번 달' },
  { value: 'quarter', label: '이번 분기' },
  { value: 'year', label: '올해' }
];

// 드롭다운 토글 (위치 계산 포함)
const toggleDropdown = (event: Event) => {
  event.stopPropagation();
  isDropdownOpen.value = !isDropdownOpen.value;
  
  if (isDropdownOpen.value && dropdownRef.value) {
    // 드롭다운 버튼의 위치 계산
    const rect = dropdownRef.value.getBoundingClientRect();
    dropdownStyle.value = {
      position: 'fixed',
      top: `${rect.bottom + 8}px`,
      left: `${rect.left}px`,
      minWidth: `${rect.width}px`
    };
  }
};

// 기간 선택
const selectPeriod = (period: string) => {
  emits('updateStatisticsFilter', { ...props.statisticsFilter, period });
  isDropdownOpen.value = false;
};

// 기간 라벨 가져오기
const getPeriodLabel = (period: string) => {
  const option = periodOptions.find(opt => opt.value === period);
  return option ? option.label : '전체 기간';
};

// 외부 클릭 시 드롭다운 닫기
const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isDropdownOpen.value = false;
  }
};

// 통계 데이터
const candidatesData = ref([]);
const totalCandidates = ref(0);
const averageScore = ref(0);
const maxScore = ref(0);

// ref 추가
const reportContentRef = ref<HTMLElement | null>(null);
const modalRef = ref<HTMLElement | null>(null);

// 차트 ref
const scoreDistributionChartRef = ref<HTMLElement | null>(null);
const avgScoreChartRef = ref<HTMLElement | null>(null);

// 차트 인스턴스
let scoreDistributionChart: ECharts | null = null;
let avgScoreChart: ECharts | null = null;

// 데이터 로딩 및 통계 계산
const loadData = async () => {
  try {
    const res = await axios.get('http://3.38.218.18:8080/api/v1/interviewees/simple');
    let data = res.data.data;
    
    // props.statisticsFilter.period에 따른 필터링 로직 추가
    if (props.statisticsFilter.period !== 'all') {
      // 필터링 로직 구현
    }
    
    candidatesData.value = data;
    
    // 통계 계산
    const scores = candidatesData.value.map((item: any) => item.score ?? 0).filter(score => score > 0);
    totalCandidates.value = candidatesData.value.length;
    averageScore.value = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
    maxScore.value = scores.length > 0 ? Math.max(...scores) : 0;
    
  } catch (error) {
    console.error('데이터 로딩 실패:', error);
    // 더미 데이터로 대체
    totalCandidates.value = 67;
    averageScore.value = 75.8;
    maxScore.value = 95;
  }
};

const downloadReport = () => {
  // 통계 데이터를 JSON 형태로 준비
  const reportData = {
    generatedAt: new Date().toISOString(),
    summary: {
      totalCandidates: totalCandidates.value,
      averageScore: averageScore.value,
      maxScore: maxScore.value
    },
    candidates: candidatesData.value
  };

  // JSON 파일로 다운로드
  const dataStr = JSON.stringify(reportData, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `면접통계리포트_${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  // 성공 알림
  showNotification('리포트가 성공적으로 다운로드되었습니다.', 'success');
};

// 차트 초기화 함수
const initCharts = async () => {
  await loadData();
  
  // 점수 분포 차트
  if (scoreDistributionChartRef.value) {
    scoreDistributionChart = echarts.init(scoreDistributionChartRef.value);
    
    const bins = [0, 0, 0, 0, 0];
    const scores = candidatesData.value.map((item: any) => item.score ?? 0).filter(score => score > 0);
    
    scores.forEach((score: number) => {
      if (score >= 1 && score <= 20) bins[0]++;
      else if (score >= 21 && score <= 40) bins[1]++;
      else if (score >= 41 && score <= 60) bins[2]++;
      else if (score >= 61 && score <= 80) bins[3]++;
      else if (score >= 81 && score <= 100) bins[4]++;
    });

    scoreDistributionChart.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(0,0,0,0.8)',
        borderColor: 'transparent',
        textStyle: { color: '#fff' },
        formatter: (params: any) => {
          const data = params[0];
          return `점수 구간: ${data.name}점<br/>면접자 수: ${data.value}명`;
        }
      },
      grid: {
        left: '5%',
        right: '5%',
        top: '10%',
        bottom: '15%'
      },
      xAxis: {
        type: 'category',
        data: ['1-20', '21-40', '41-60', '61-80', '81-100'],
        axisLabel: {
          color: '#666',
          fontSize: 12
        },
        axisLine: {
          lineStyle: { color: '#e0e0e0' }
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          color: '#666',
          fontSize: 12
        },
        axisLine: {
          lineStyle: { color: '#e0e0e0' }
        },
        splitLine: {
          lineStyle: { color: '#f0f0f0' }
        }
      },
      series: [{
        data: bins,
        type: 'bar',
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#60a5fa' },
            { offset: 1, color: '#3b82f6' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#93c5fd' },
              { offset: 1, color: '#60a5fa' }
            ])
          }
        }
      }]
    });
  }

  // 역량별 평균 점수 레이더 차트
  if (avgScoreChartRef.value) {
    avgScoreChart = echarts.init(avgScoreChartRef.value);
    avgScoreChart.setOption({
      tooltip: {
        backgroundColor: 'rgba(0,0,0,0.8)',
        borderColor: 'transparent',
        textStyle: { color: '#fff' }
      },
      radar: {
        indicator: [
          { name: 'SUPEX', max: 100 },
          { name: 'VWBE', max: 100 },
          { name: 'Passionate', max: 100 },
          { name: 'Proactive', max: 100 },
          { name: 'Professional', max: 100 },
          { name: 'People', max: 100 }
        ],
        radius: '70%',
        nameGap: 20,
        name: {
          textStyle: {
            color: '#666',
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        splitArea: {
          areaStyle: {
            color: ['rgba(34, 197, 94, 0.1)', 'rgba(34, 197, 94, 0.05)']
          }
        },
        axisLine: {
          lineStyle: { color: '#22c55e' }
        },
        splitLine: {
          lineStyle: { color: '#22c55e', opacity: 0.3 }
        }
      },
      series: [{
        type: 'radar',
        data: [{
          value: [85, 75, 90, 80, 70, 88],
          name: '평균 점수',
          areaStyle: {
            color: new echarts.graphic.RadialGradient(0.1, 0.6, 1, [
              { offset: 0, color: 'rgba(34, 197, 94, 0.4)' },
              { offset: 1, color: 'rgba(34, 197, 94, 0.1)' }
            ])
          },
          lineStyle: {
            color: '#22c55e',
            width: 3
          },
          itemStyle: {
            color: '#22c55e',
            borderWidth: 2,
            borderColor: '#fff'
          }
        }]
      }]
    });
  }
};

// 결과 공유 함수
const shareResults = async () => {
  const shareText = `면접 통계 결과
📊 총 면접자: ${totalCandidates.value}명
📈 평균 점수: ${averageScore.value.toFixed(1)}점
🏆 최고 점수: ${maxScore.value}점

#면접통계 #SKAXIS`;

  try {
    if (navigator.share) {
      // Web Share API 사용 (모바일에서 지원)
      await navigator.share({
        title: 'SK AXIS 면접 통계',
        text: shareText,
        url: window.location.href
      });
      showNotification('통계 결과가 공유되었습니다.', 'success');
    } else {
      // 클립보드에 복사
      await navigator.clipboard.writeText(shareText);
      showNotification('통계 결과가 클립보드에 복사되었습니다.', 'success');
    }
  } catch (error) {
    console.error('공유 실패:', error);
    // 수동으로 텍스트 선택
    const textArea = document.createElement('textarea');
    textArea.value = shareText;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      showNotification('통계 결과가 클립보드에 복사되었습니다.', 'success');
    } catch (err) {
      showNotification('공유에 실패했습니다. 수동으로 복사해주세요.', 'error');
    }
    document.body.removeChild(textArea);
  }
};

// 알림 표시 함수 (info 타입 추가)
const showNotification = (message: string, type: 'success' | 'error' | 'info') => {
  const notification = document.createElement('div');
  notification.className = 'fixed top-4 right-4 z-50 transform transition-all duration-300 ease-in-out';
  
  let bgColor, icon;
  switch (type) {
    case 'success':
      bgColor = 'bg-green-500';
      icon = 'fa-check-circle';
      break;
    case 'error':
      bgColor = 'bg-red-500';
      icon = 'fa-exclamation-triangle';
      break;
    case 'info':
      bgColor = 'bg-blue-500';
      icon = 'fa-info-circle';
      break;
  }
  
  const title = type === 'success' ? '성공!' : type === 'error' ? '오류!' : '알림';
  
  notification.innerHTML = `
    <div class="${bgColor} text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 max-w-md">
      <div class="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
        <i class="fas ${icon}"></i>
      </div>
      <div>
        <div class="font-semibold">${title}</div>
        <div class="text-sm opacity-90">${message}</div>
      </div>
      <button class="ml-4 text-white hover:text-gray-200 opacity-70 hover:opacity-100 transition-opacity">
        <i class="fas fa-times"></i>
      </button>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  // 애니메이션 효과
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
    notification.style.opacity = '1';
  }, 100);
  
  // 자동 제거 및 클릭 제거
  const removeNotification = () => {
    notification.style.transform = 'translateX(100%)';
    notification.style.opacity = '0';
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 300);
  };
  
  const closeButton = notification.querySelector('button');
  if (closeButton) {
    closeButton.addEventListener('click', removeNotification);
  }
  
  // info 타입은 조금 더 오래 표시
  const autoRemoveTime = type === 'info' ? 6000 : 4000;
  setTimeout(removeNotification, autoRemoveTime);
};

// 차트 업데이트 함수
// const updateCharts = () => {
//   // 차트 업데이트 로직 (필터링 제거로 단순화)
//   initCharts();
// };

onMounted(() => {
  initCharts();
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// 컴포넌트 언마운트 시 차트 해제
// const cleanup = () => {
//   if (scoreDistributionChart) {
//     scoreDistributionChart.dispose();
//   }
//   if (avgScoreChart) {
//     avgScoreChart.dispose();
//   }
// };
</script>

<style scoped>
/* 애니메이션 */
@keyframes slideUp {
  from { 
    opacity: 0; 
    transform: translateY(30px) scale(0.95); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0) scale(1); 
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slideUp {
  animation: slideUp 0.4s ease-out;
}

.animate-slideDown {
  animation: slideDown 0.2s ease-out;
}

/* 호버 효과 */
.hover\:-translate-y-1:hover {
  transform: translateY(-0.25rem);
}

/* 스크롤바 스타일링 */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
}

/* 셀렉트 박스 커스텀 */
select {
  background-image: none;
}

/* 그라데이션 배경 */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}

/* 차트 컨테이너 호버 효과 */
.bg-white:hover {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* 드롭다운 z-index 보장 */
.relative {
  position: relative;
}

/* 드롭다운 메뉴가 다른 요소들 위에 표시되도록 */
.z-\[9999\] {
  z-index: 9999 !important;
}
</style>