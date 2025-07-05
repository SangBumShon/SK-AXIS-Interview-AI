<template>
  <!-- 시스템 설정(평가 기준 설정) 뷰 -->
  <div class="p-8">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900">시스템 설정</h2>
      <div class="flex items-center gap-4">
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <i class="fas fa-times text-2xl"></i>
        </button>
      </div>
    </div>
    <!-- 평가 기준 설정 -->
    <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
      <h3 class="text-lg font-bold text-gray-900 mb-4">면접 평가 기준 설정</h3>
      <p class="text-gray-600 mb-6">각 평가 항목의 가중치를 설정합니다. 모든 항목의 합은 100%여야 합니다.</p>
      
      <!-- 로딩 상태 표시 -->
      <div v-if="isLoading" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
        <span class="ml-3 text-gray-600">가중치 설정을 불러오는 중...</span>
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-for="(criterion, index) in evaluationCriteria" :key="index" class="bg-gray-50 rounded-lg p-6 col-span-1">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full flex items-center justify-center" :class="criterion.bgColor">
                <i class="fas" :class="criterion.icon"></i>
              </div>
              <div>
                <h4 class="font-medium text-gray-900">{{ criterion.name }}</h4>
                <p class="text-sm text-gray-500">{{ criterion.description }}</p>
              </div>
            </div>
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
          </div>
          <div class="space-y-3 mt-4 flex flex-col">
            <div v-for="(subCriterion, subIndex) in criterion.subCriteria" :key="subIndex" class="flex items-center justify-between gap-2">
              <span class="text-gray-700">{{ subCriterion.name }}</span>
              <input 
                type="number" 
                v-model="subCriterion.weight" 
                class="spinbox-input spinbox-input-sub"
                min="0"
                max="100"
                disabled
              >
            </div>
          </div>
          <!-- 하위 항목들은 고정값이므로 합계 검증 메시지 제거 -->
        </div>
      </div>
      <div v-if="!isLoading" class="flex justify-between items-center mt-8">
        <div class="flex items-center gap-2">
          <span class="text-lg font-medium">총 점수:</span>
          <span :class="totalWeight === 100 ? 'text-green-600' : 'text-red-600'" class="text-lg font-bold">
            {{ totalWeight }}%
          </span>
        </div>
        <div class="flex gap-4">
          <button @click="resetWeights" class="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors">
            초기화
          </button>
          <button 
            @click="saveWeights" 
            :disabled="!canSave"
            :class="{'opacity-50 cursor-not-allowed': !canSave}"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            저장하기
          </button>
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
    icon: 'fa-user',
    bgColor: 'bg-blue-100 text-blue-600',
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
    bgColor: 'bg-green-100 text-green-600',
    subCriteria: [
      { name: '직무 역량', weight: 0 },
      { name: '도메인 이해도', weight: 0 }
    ]
  },
  {
    name: '비언어적',
    description: '표정, 태도, 자세 등',
    weight: 0,
    icon: 'fa-comments',
    bgColor: 'bg-yellow-100 text-yellow-600',
    subCriteria: [
      { name: '비언어적 평가', weight: 0 }
    ]
  }
]);

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
// 하위 항목들은 고정값이므로 합계 계산 제거
const canSave = computed(() =>
  totalWeight.value === 100 // 총 합이 100%가 되어야 함
);
const validateWeights = () => {
  evaluationCriteria.value.forEach(criterion => {
    if (criterion.weight < 0) criterion.weight = 0;
    if (criterion.weight > 100) criterion.weight = 100;
  });
};
// 하위 항목들은 고정값이므로 검증 함수 제거
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
const currentConfigId = ref<number | null>(null);

const saveWeights = async () => {
  if (totalWeight.value !== 100) {
    alert('총 점수가 100%가 되어야 합니다.');
    return;
  }

  if (!currentConfigId.value) {
    alert('저장할 설정을 찾을 수 없습니다.');
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

    // 저장 성공 메시지 표시
    const successModal = document.createElement('div');
    successModal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    successModal.innerHTML = `
      <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center relative animate-fadeIn">
        <div class="mb-6">
          <div class="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
            <i class="fas fa-check text-green-500 text-3xl"></i>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">저장 완료</h3>
          <p class="text-gray-600">평가 기준이 성공적으로 저장되었습니다.</p>
        </div>
        <button class="w-full bg-red-600 text-white py-2 rounded-md font-medium hover:bg-red-700 transition-colors">
          확인
        </button>
      </div>
    `;
    document.body.appendChild(successModal);
    const closeButton = successModal.querySelector('button');
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        document.body.removeChild(successModal);
      });
    }
  } catch (error) {
    console.error('❌ 저장 실패:', error);
    
    // 저장 실패 메시지 표시
    const errorModal = document.createElement('div');
    errorModal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    errorModal.innerHTML = `
      <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center relative animate-fadeIn">
        <div class="mb-6">
          <div class="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
            <i class="fas fa-exclamation-triangle text-red-500 text-3xl"></i>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">저장 실패</h3>
          <p class="text-gray-600">평가 기준 저장 중 오류가 발생했습니다.</p>
        </div>
        <button class="w-full bg-red-600 text-white py-2 rounded-md font-medium hover:bg-red-700 transition-colors">
          확인
        </button>
      </div>
    `;
    document.body.appendChild(errorModal);
    const closeButton = errorModal.querySelector('button');
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        document.body.removeChild(errorModal);
      });
    }
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
// 하위 항목들은 고정값이므로 증감 함수들 제거
</script>
<style scoped>
/* 필요한 스타일 */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fadeIn {
  animation: fadeIn 0.3s ease-in-out;
}
.spinbox-group {
  display: flex;
  align-items: stretch;
}
.spinbox-input {
  width: 6rem;
  min-width: 3.5rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem 0 0 0.375rem;
  text-align: right;
  background: #fff;
  font-size: 1rem;
  outline: none;
}
.spinbox-btns {
  display: flex;
  flex-direction: column;
  border: 1px solid #d1d5db;
  border-left: none;
  border-radius: 0 0.375rem 0.375rem 0;
  background: #f9fafb;
  overflow: hidden;
  height: 100%;
}
.spinbox-btn {
  flex: 1 1 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  width: 2rem;
  min-height: 1.25rem;
  color: #6b7280;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background 0.15s;
  font-size: 0.85rem;
}
.spinbox-btn-up {
  border-bottom: 1px solid #e5e7eb;
}
.spinbox-btn:active, .spinbox-btn:hover {
  background: #f3f4f6;
  color: #111827;
}
.spinbox-btn i {
  font-size: 0.85rem;
}
/* 소분류 input은 더 작게 */
.spinbox-input.spinbox-input-sub {
  width: 4.5rem;
  font-size: 0.95rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: #f3f4f6;
  color: #6b7280;
  cursor: not-allowed;
  text-align: right;
}
</style> 