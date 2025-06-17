// // 환경에 따른 API URL 설정
// const API_BASE_URL = process.env.NODE_ENV === 'production' 
//   ? '/api/spring'  // Docker 환경에서는 nginx 프록시 경로
//   : 'http://localhost:8080/api/v1';  // 개발 환경에서는 직접 접근

interface InterviewSchedule {
  interviewDate: number[];
  timeRange: string;
  roomName: string;
  interviewers: string[];
  interviewees: string[];
}

interface ScheduleResponse {
  schedules: InterviewSchedule[];
  message: string;
}

export const getInterviewSchedules = async (date: string): Promise<ScheduleResponse> => {
  try {
    // 수정: schedule/all 엔드포인트 사용
    const response = await fetch('http://sk-axis-springboot:8080/api/v1/schedule/all', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ date })
    });

    return response.json();
  } catch (error) {
    console.error('면접 일정 조회 중 오류 발생:', error);
    throw error;
  }
};

