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
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
              <div class="spinbox-group">
                <input 
                  type="number" 
                  v-model="subCriterion.weight" 
                  @input="validateSubWeights(criterion)"
                  class="spinbox-input spinbox-input-sub"
                  min="0"
                  max="100"
                >
                <div class="spinbox-btns">
                  <button type="button" @click="incrementSubWeight(criterion, subCriterion)" class="spinbox-btn spinbox-btn-up">
                    <i class="fas fa-chevron-up"></i>
                  </button>
                  <button type="button" @click="decrementSubWeight(criterion, subCriterion)" class="spinbox-btn spinbox-btn-down">
                    <i class="fas fa-chevron-down"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="subCriteriaSums[index] !== 100" class="text-red-500 text-sm mt-2">
            합계가 100이 아닙니다. (현재: {{ subCriteriaSums[index] }})
          </div>
        </div>
      </div>
      <div class="flex justify-between items-center mt-8">
        <div class="flex items-center gap-2">
          <span class="text-lg font-medium">총 가중치:</span>
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
import { ref, computed } from 'vue';
const evaluationCriteria = ref([
  {
    name: '인성',
    description: '지원자의 성격, 태도, 가치관 등을 평가',
    weight: 30,
    icon: 'fa-user',
    bgColor: 'bg-blue-100 text-blue-600',
    subCriteria: [
      { name: '성실성', weight: 35 },
      { name: '책임감', weight: 35 },
      { name: '팀워크', weight: 30 }
    ]
  },
  {
    name: '직무 적합도',
    description: '직무 수행에 필요한 지식과 경험 평가',
    weight: 40,
    icon: 'fa-briefcase',
    bgColor: 'bg-green-100 text-green-600',
    subCriteria: [
      { name: '전문 지식', weight: 40 },
      { name: '실무 경험', weight: 35 },
      { name: '문제 해결력', weight: 25 }
    ]
  },
  {
    name: '커뮤니케이션',
    description: '의사소통 능력과 표현력 평가',
    weight: 20,
    icon: 'fa-comments',
    bgColor: 'bg-yellow-100 text-yellow-600',
    subCriteria: [
      { name: '논리성', weight: 40 },
      { name: '명확성', weight: 30 },
      { name: '경청력', weight: 30 }
    ]
  },
  {
    name: '발전 가능성',
    description: '학습 능력과 성장 잠재력 평가',
    weight: 10,
    icon: 'fa-chart-line',
    bgColor: 'bg-purple-100 text-purple-600',
    subCriteria: [
      { name: '학습 의지', weight: 40 },
      { name: '적응력', weight: 30 },
      { name: '창의성', weight: 30 }
    ]
  }
]);
const totalWeight = computed(() => {
  return evaluationCriteria.value.reduce((sum, criterion) => sum + Number(criterion.weight), 0);
});
const subCriteriaSums = computed(() =>
  evaluationCriteria.value.map(criterion =>
    criterion.subCriteria.reduce((sum, sub) => sum + Number(sub.weight), 0)
  )
);
const canSave = computed(() =>
  totalWeight.value === 100 &&
  subCriteriaSums.value.every(sum => sum === 100)
);
const validateWeights = () => {
  evaluationCriteria.value.forEach(criterion => {
    if (criterion.weight < 0) criterion.weight = 0;
    if (criterion.weight > 100) criterion.weight = 100;
  });
};
const validateSubWeights = (criterion: any) => {
  const totalSubWeight = criterion.subCriteria.reduce((sum: number, sub: any) => sum + Number(sub.weight), 0);
  if (totalSubWeight !== 100) {
    criterion.subCriteria.forEach((sub: any) => {
      if (sub.weight < 0) sub.weight = 0;
      if (sub.weight > 100) sub.weight = 100;
    });
  }
};
const resetWeights = () => {
  evaluationCriteria.value = evaluationCriteria.value.map(criterion => ({
    ...criterion,
    weight: 25,
    subCriteria: criterion.subCriteria.map((sub: any) => ({
      ...sub,
      weight: Math.floor(100 / criterion.subCriteria.length)
    }))
  }));
};
const saveWeights = () => {
  if (totalWeight.value !== 100) {
    alert('총 가중치가 100%가 되어야 합니다.');
    return;
  }
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
const incrementSubWeight = (criterion: any, subCriterion: any) => {
  if (subCriterion.weight < 100) {
    subCriterion.weight++;
    validateSubWeights(criterion);
  }
};
const decrementSubWeight = (criterion: any, subCriterion: any) => {
  if (subCriterion.weight > 0) {
    subCriterion.weight--;
    validateSubWeights(criterion);
  }
};
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
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}
</style> 