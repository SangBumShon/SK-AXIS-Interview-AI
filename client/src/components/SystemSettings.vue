<template>
  <!-- 시스템 설정(평가 기준 설정) 뷰 - 고도화 버전 -->
  <div class="container mx-auto px-6 py-8 bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen">
    <!-- 헤더 -->
    <div class="flex justify-between items-center mb-8 border-b border-gray-200 pb-6">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center shadow-lg">
          <i class="fas fa-cog text-white text-xl"></i>
        </div>
        <div>
          <h2 class="text-3xl font-bold text-gray-900">시스템 설정</h2>
          <p class="text-gray-600 mt-1">면접 평가 기준과 가중치를 설정하세요</p>
        </div>
      </div>
      <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 p-2 rounded-full hover:bg-white transition-all duration-200">
        <i class="fas fa-times text-2xl"></i>
      </button>
    </div>

    <!-- 평가 기준 설정 -->
    <div class="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
      <!-- 섹션 헤더 -->
      <div class="bg-gradient-to-r from-gray-50 to-white p-8 border-b border-gray-100">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <i class="fas fa-balance-scale text-blue-600"></i>
          </div>
          <div>
            <h3 class="text-2xl font-bold text-gray-900">면접 평가 기준 설정</h3>
            <p class="text-gray-600 mt-1">각 평가 항목의 가중치를 설정합니다. 모든 항목의 합은 100%여야 합니다.</p>
          </div>
        </div>
        
        <!-- 진행률 표시 -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-medium text-gray-700">총 가중치 설정</span>
            <span :class="totalWeight === 100 ? 'text-green-600' : 'text-red-600'" class="text-lg font-bold">
              {{ totalWeight }}%
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div 
              class="h-full transition-all duration-500 ease-out rounded-full"
              :class="totalWeight === 100 ? 'bg-gradient-to-r from-green-500 to-green-600' : totalWeight > 100 ? 'bg-gradient-to-r from-red-500 to-red-600' : 'bg-gradient-to-r from-blue-500 to-blue-600'"
              :style="{ width: Math.min(totalWeight, 100) + '%' }"
            ></div>
          </div>
          <div class="flex justify-between text-xs text-gray-500 mt-2">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>
      </div>

      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="flex items-center justify-center py-16">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-red-600 mb-4"></div>
          <span class="text-gray-600 font-medium">가중치 설정을 불러오는 중...</span>
        </div>
      </div>

      <!-- 평가 기준 카드들 -->
      <div v-else class="p-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          <div 
            v-for="(criterion, index) in evaluationCriteria" 
            :key="index" 
            class="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
          >
            <!-- 카드 헤더 -->
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center gap-4">
                <div class="w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg" :class="criterion.bgColor">
                  <i class="fas text-xl" :class="criterion.icon"></i>
                </div>
                <div>
                  <h4 class="text-xl font-bold text-gray-900">{{ criterion.name }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ criterion.description }}</p>
                </div>
              </div>
            </div>

            <!-- 메인 가중치 설정 -->
            <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-6">
              <div class="flex items-center justify-between mb-4">
                <span class="text-lg font-semibold text-gray-800">메인 가중치</span>
                <div class="flex items-center gap-3">
                  <div class="spinbox-group">
                    <input 
                      type="number" 
                      v-model="criterion.weight" 
                      @input="validateWeights"
                      class="spinbox-input"
                      min="0"
                      max="100"
                    >
                    <div class="spinbox-btns">
                      <button type="button" @click="incrementWeight(criterion)" class="spinbox-btn spinbox-btn-up">
                        <i class="fas fa-chevron-up"></i>
                      </button>
                      <button type="button" @click="decrementWeight(criterion)" class="spinbox-btn spinbox-btn-down">
                        <i class="fas fa-chevron-down"></i>
                      </button>
                    </div>
                  </div>
                  <span class="text-2xl font-bold text-gray-900">%</span>
                </div>
              </div>
              
              <!-- 가중치 시각적 표시 -->
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-full rounded-full transition-all duration-300"
                  :class="getWeightBarColor(criterion.weight)"
                  :style="{ width: criterion.weight + '%' }"
                ></div>
              </div>
            </div>

            <!-- 하위 항목들 -->
            <div class="space-y-3">
              <h5 class="text-sm font-semibold text-gray-700 uppercase tracking-wider">세부 항목 (고정값)</h5>
              <div v-for="(subCriterion, subIndex) in criterion.subCriteria" :key="subIndex" class="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100">
                <span class="text-gray-700 font-medium">{{ subCriterion.name }}</span>
                <div class="flex items-center gap-2">
                  <input 
                    type="number" 
                    v-model="subCriterion.weight" 
                    class="spinbox-input-sub"
                    min="0"
                    max="100"
                    disabled
                  >
                  <span class="text-sm font-semibold text-gray-600">점</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 액션 버튼들 -->
        <div class="flex justify-between items-center mt-12 p-6 bg-gray-50 rounded-2xl">
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full" :class="totalWeight === 100 ? 'bg-green-500' : 'bg-red-500'"></div>
              <span class="text-sm font-medium text-gray-700">
                {{ totalWeight === 100 ? '가중치 설정이 완료되었습니다' : '가중치 합계가 100%가 되어야 합니다' }}
              </span>
            </div>
          </div>
          
          <div class="flex gap-4">
            <button 
              @click="resetWeights" 
              class="px-6 py-3 text-gray-700 bg-white border-2 border-gray-300 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 font-medium flex items-center gap-2"
            >
              <i class="fas fa-undo"></i>
              초기화
            </button>
            <button 
              @click="saveWeights" 
              :disabled="!canSave"
              :class="[
                'px-8 py-3 rounded-xl font-medium transition-all duration-200 flex items-center gap-2',
                canSave 
                  ? 'bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5' 
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              ]"
            >
              <i class="fas fa-save"></i>
              {{ canSave ? '저장하기' : '100%를 맞춰주세요' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { weightConfigService } from '../services/weightConfigService';

const isLoading = ref(true);

const evaluationCriteria = ref([
  {
    name: '인성',
    description: 'SUPEX, VWBE, Passionate, Proactive, Professional, People',
    weight: 0,
    icon: 'fa-heart',
    bgColor: 'bg-gradient-to-br from-blue-400 to-blue-600 text-white',
    subCriteria: [
      { name: 'SUPEX', weight: 0 },
      { name: 'VWBE', weight: 0 },
      { name: 'Passionate', weight: 0 },
      { name: 'Proactive', weight: 0 },
      { name: 'Professional', weight: 0 },
      { name: 'People', weight: 0 }
    ]
  },
  {
    name: '직무/도메인',
    description: '직무 역량, 도메인 이해도',
    weight: 0,
    icon: 'fa-briefcase',
    bgColor: 'bg-gradient-to-br from-green-400 to-green-600 text-white',
    subCriteria: [
      { name: '직무 역량', weight: 0 },
      { name: '도메인 이해도', weight: 0 }
    ]
  },
  {
    name: '비언어적',
    description: '표정, 태도, 자세 등',
    weight: 0,
    icon: 'fa-smile',
    bgColor: 'bg-gradient-to-br from-purple-400 to-purple-600 text-white',
    subCriteria: [
      { name: '비언어적 평가', weight: 0 }
    ]
  }
]);

const currentConfigId = ref<number | null>(null);

// 가중치 바 색상 계산
const getWeightBarColor = (weight: number) => {
  if (weight >= 80) return 'bg-gradient-to-r from-red-500 to-red-600';
  if (weight >= 60) return 'bg-gradient-to-r from-orange-500 to-orange-600';
  if (weight >= 40) return 'bg-gradient-to-r from-yellow-500 to-yellow-600';
  if (weight >= 20) return 'bg-gradient-to-r from-green-500 to-green-600';
  return 'bg-gradient-to-r from-blue-500 to-blue-600';
};

// API에서 가중치 정보를 가져와서 초기화하는 함수
const loadWeightConfig = async () => {
  try {
    console.log('🔄 API 호출 시작: 가중치 설정 로딩 중...');
    isLoading.value = true;
    const activeConfig = await weightConfigService.getActiveWeightConfig();
    console.log('✅ API 응답 받음:', activeConfig);
    
    if (activeConfig) {
      console.log('📊 가중치 설정 적용 중...');
      
      // configId 저장
      currentConfigId.value = activeConfig.weightConfigId;
      console.log('🆔 설정 ID:', currentConfigId.value);
      
      // 인성 (verbalWeight)
      const verbalWeight = activeConfig.verbalWeight;
      evaluationCriteria.value[0].weight = verbalWeight;
      console.log(`👤 인성 가중치 설정: ${verbalWeight}%`);
      // 하위 항목들은 고정값으로 설정
      evaluationCriteria.value[0].subCriteria.forEach(sub => {
        sub.weight = 15; // 고정값
      });
      
      // 직무/도메인 (domainWeight)
      const domainWeight = activeConfig.domainWeight;
      evaluationCriteria.value[1].weight = domainWeight;
      console.log(`💼 직무/도메인 가중치 설정: ${domainWeight}%`);
      // 하위 항목들은 고정값으로 설정
      evaluationCriteria.value[1].subCriteria.forEach(sub => {
        sub.weight = 15; // 고정값
      });
      
      // 비언어적 (nonverbalWeight)
      const nonverbalWeight = activeConfig.nonverbalWeight;
      evaluationCriteria.value[2].weight = nonverbalWeight;
      console.log(`😊 비언어적 가중치 설정: ${nonverbalWeight}%`);
      evaluationCriteria.value[2].subCriteria[0].weight = 15; // 고정값
      
      console.log('✅ 가중치 설정 완료!');
      console.log('📋 최종 설정:', {
        인성: verbalWeight + '%',
        직무도메인: domainWeight + '%',
        비언어적: nonverbalWeight + '%',
        총합: (verbalWeight + domainWeight + nonverbalWeight) + '%'
      });
    } else {
      console.warn('⚠️ 활성화된 가중치 설정이 없습니다.');
    }
  } catch (error) {
    console.error('❌ API 호출 실패:', error);
    // 에러 발생 시 기본값으로 초기화
    resetWeights();
  } finally {
    isLoading.value = false;
    console.log('🏁 로딩 완료');
  }
};

// 컴포넌트 마운트 시 API 호출
onMounted(() => {
  loadWeightConfig();
});

const totalWeight = computed(() => {
  return evaluationCriteria.value.reduce((sum, criterion) => sum + Number(criterion.weight), 0);
});

const canSave = computed(() =>
  totalWeight.value === 100 // 총 합이 100%가 되어야 함
);

const validateWeights = () => {
  evaluationCriteria.value.forEach(criterion => {
    if (criterion.weight < 0) criterion.weight = 0;
    if (criterion.weight > 100) criterion.weight = 100;
  });
};

const resetWeights = async () => {
  try {
    await loadWeightConfig();
  } catch (error) {
    console.error('Failed to reset weights:', error);
    // API 호출 실패 시 기본값으로 초기화
    evaluationCriteria.value = evaluationCriteria.value.map(criterion => ({
      ...criterion,
      weight: criterion.name === '인성' ? 90 : criterion.name === '직무/도메인' ? 30 : 15,
      subCriteria: criterion.subCriteria.map((sub: any) => ({
        ...sub,
        weight: criterion.name === '인성' ? 15 : criterion.name === '직무/도메인' ? 15 : 15
      }))
    }));
  }
};

const saveWeights = async () => {
  if (totalWeight.value !== 100) {
    showNotification('총 점수가 100%가 되어야 합니다.', 'error');
    return;
  }

  if (!currentConfigId.value) {
    showNotification('저장할 설정을 찾을 수 없습니다.', 'error');
    return;
  }

  try {
    console.log('💾 저장 시작...');
    
    const requestData = {
      verbalWeight: evaluationCriteria.value[0].weight,
      domainWeight: evaluationCriteria.value[1].weight,
      nonverbalWeight: evaluationCriteria.value[2].weight,
      validWeightSum: totalWeight.value === 100
    };

    console.log('📤 전송할 데이터:', requestData);

    const updatedConfig = await weightConfigService.updateWeightConfig(currentConfigId.value, requestData);
    
    console.log('✅ 저장 완료:', updatedConfig);
    showNotification('평가 기준이 성공적으로 저장되었습니다.', 'success');

  } catch (error) {
    console.error('❌ 저장 실패:', error);
    showNotification('평가 기준 저장 중 오류가 발생했습니다.', 'error');
  }
};

const incrementWeight = (criterion: any) => {
  if (criterion.weight < 100) {
    criterion.weight++;
    validateWeights();
  }
};

const decrementWeight = (criterion: any) => {
  if (criterion.weight > 0) {
    criterion.weight--;
    validateWeights();
  }
};

// 알림 표시 함수 개선
const showNotification = (message: string, type: 'success' | 'error') => {
  const notification = document.createElement('div');
  notification.className = 'fixed top-4 right-4 z-50 transform transition-all duration-300 ease-in-out';
  
  const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';
  const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
  
  notification.innerHTML = `
    <div class="${bgColor} text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 max-w-md">
      <div class="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
        <i class="fas ${icon}"></i>
      </div>
      <div>
        <div class="font-semibold">${type === 'success' ? '성공!' : '오류!'}</div>
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
  
  setTimeout(removeNotification, 4000);
};
</script>

<style scoped>
/* 숨겨진 스핀 버튼 */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* 애니메이션 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fadeIn {
  animation: fadeIn 0.6s ease-out;
}

/* 커스텀 스핀박스 스타일 */
.spinbox-group {
  display: flex;
  align-items: stretch;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border-radius: 0.75rem;
  overflow: hidden;
}

.spinbox-input {
  width: 5rem;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem 0 0 0.75rem;
  text-align: center;
  background: white;
  font-size: 1.125rem;
  font-weight: 600;
  outline: none;
  transition: all 0.2s ease;
  color: #1f2937;
}

.spinbox-input:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.spinbox-btns {
  display: flex;
  flex-direction: column;
  border: 2px solid #e5e7eb;
  border-left: none;
  border-radius: 0 0.75rem 0.75rem 0;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  overflow: hidden;
}

.spinbox-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  width: 2.5rem;
  color: #6b7280;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.spinbox-btn-up {
  border-bottom: 1px solid #e5e7eb;
}

.spinbox-btn:hover {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  transform: scale(1.05);
}

.spinbox-btn:active {
  transform: scale(0.95);
}

/* 하위 항목 input 스타일 */
.spinbox-input-sub {
  width: 4rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
  text-align: center;
  font-size: 0.875rem;
  font-weight: 500;
}

/* 호버 효과 */
.hover\:-translate-y-1:hover {
  transform: translateY(-0.25rem);
}

.hover\:-translate-y-0\.5:hover {
  transform: translateY(-0.125rem);
}

/* 그라데이션 효과 */
.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}

.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

/* 스크롤바 스타일링 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
}
</style>