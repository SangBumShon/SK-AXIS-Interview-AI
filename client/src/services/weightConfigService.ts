interface WeightConfig {
  weightConfigId: number;
  verbalWeight: number;
  domainWeight: number;
  nonverbalWeight: number;
  isActive: boolean;
  createdAt: number[];
}

interface UpdateWeightConfigRequest {
  verbalWeight: number;
  domainWeight: number;
  nonverbalWeight: number;
  validWeightSum: boolean;
}

export const weightConfigService = {
  async getAllWeightConfigs(): Promise<WeightConfig[]> {
    try {
      console.log('🌐 API 요청: http://3.38.218.18:8080/api/v1/weight-config/all');
      const response = await fetch('http://3.38.218.18:8080/api/v1/weight-config/all');
      console.log('📡 HTTP 상태:', response.status, response.statusText);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('📦 API 응답 데이터:', data);
      return data;
    } catch (error) {
      console.error('❌ API 호출 중 오류 발생:', error);
      throw error;
    }
  },

  async getActiveWeightConfig(): Promise<WeightConfig | null> {
    try {
      console.log('🔍 활성화된 가중치 설정 검색 중...');
      const configs = await this.getAllWeightConfigs();
      const activeConfig = configs.find(config => config.isActive);
      
      if (activeConfig) {
        console.log('✅ 활성화된 설정 발견:', activeConfig);
      } else {
        console.log('⚠️ 활성화된 설정이 없습니다.');
      }
      
      return activeConfig || null;
    } catch (error) {
      console.error('❌ 활성 설정 검색 중 오류:', error);
      throw error;
    }
  },

  async updateWeightConfig(configId: number, requestData: UpdateWeightConfigRequest): Promise<WeightConfig> {
    try {
      console.log('🔄 가중치 설정 업데이트 시작:', { configId, requestData });
      
      const response = await fetch(`http://3.38.218.18:8080/api/v1/weight-config/${configId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });
      
      console.log('📡 PUT 요청 HTTP 상태:', response.status, response.statusText);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const updatedConfig = await response.json();
      console.log('✅ 가중치 설정 업데이트 성공:', updatedConfig);
      return updatedConfig;
    } catch (error) {
      console.error('❌ 가중치 설정 업데이트 실패:', error);
      throw error;
    }
  }
}; 