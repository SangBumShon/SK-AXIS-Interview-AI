<<<<<<< HEAD
import axios from 'axios';

// 환경에 따른 API URL 설정
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api/spring'  // Docker 환경에서는 nginx 프록시 경로
  : 'http://localhost:8080/api/v1';  // 개발 환경에서는 직접 접근
=======
interface Interviewee {
  name: string;
  id: number;
}
>>>>>>> origin/front-ai-face

interface InterviewSchedule {
  interviewDate: number[];
  timeRange: string;
  roomName: string;
  interviewers: string[];
<<<<<<< HEAD
  interviewees: string[];
=======
  interviewees: Interviewee[];
>>>>>>> origin/front-ai-face
}

interface ScheduleResponse {
  schedules: InterviewSchedule[];
  message: string;
}

<<<<<<< HEAD
export const getInterviewSchedules = async (date: string): Promise<ScheduleResponse> => {
  try {
    // 수정: schedule/all 엔드포인트 사용
    const response = await axios.get<ScheduleResponse>(`${API_BASE_URL}/interviews/schedule/all`, {
      params: { date }
    });
    return response.data;
=======
interface ApiResponse {
  data: Array<{
    intervieweeId: number;
    applicantName: string;
    applicantId: number | null;
    interviewDate: number[];
    interviewStatus: string;
    score: number;
    interviewer: string;
    interviewLocation: string;
    createdAt: number[];
  }>;
  totalCount: number;
}

export const getInterviewSchedules = async (date: string): Promise<ScheduleResponse> => {
  try {
    const response = await fetch(`http://3.38.218.18:8080/api/v1/interviews/simple?date=${date}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const apiResponse: ApiResponse = await response.json();
    
    // API 응답을 기존 인터페이스에 맞게 변환
    const scheduleMap = new Map<string, InterviewSchedule>();
    
    apiResponse.data.forEach(item => {
      // 날짜 배열을 문자열로 변환
      const dateStr = item.interviewDate.join('-');
      
      // 시간대는 임시로 기본값 사용 (API에서 시간 정보가 없으므로)
      const timeRange = '09:00 - 10:00'; // 기본값
      
      const key = `${item.interviewLocation}_${timeRange}`;
      
      if (!scheduleMap.has(key)) {
        scheduleMap.set(key, {
          interviewDate: item.interviewDate,
          timeRange: timeRange,
          roomName: item.interviewLocation,
          interviewers: item.interviewer.split(', ').filter(name => name.trim()),
          interviewees: []
        });
      }
      
      // 지원자 추가 (id와 name 모두 포함)
      const schedule = scheduleMap.get(key)!;
      if (!schedule.interviewees.find(e => e.id === item.intervieweeId)) {
        schedule.interviewees.push({
          name: item.applicantName,
          id: item.intervieweeId // 또는 applicantId
        });
      }
    });
    
    return {
      schedules: Array.from(scheduleMap.values()),
      message: '면접 일정 조회 성공'
    };
>>>>>>> origin/front-ai-face
  } catch (error) {
    console.error('면접 일정 조회 중 오류 발생:', error);
    throw error;
  }
<<<<<<< HEAD
};
=======
};
>>>>>>> origin/front-ai-face
