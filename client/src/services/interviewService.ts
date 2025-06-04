import axios from 'axios';

export interface InterviewSchedule {
  interviewDate: number[];
  timeRange: string;
  roomName: string;
  interviewers: string[];
  interviewees: string[];
}

export interface ScheduleResponse {
  schedules: InterviewSchedule[];
  message: string;
}

export const getInterviewSchedules = async (date: string): Promise<ScheduleResponse> => {
  try {
    const token = 
    localStorage.getItem('authToken'); // 여기 값을 수정해서 토큰값을 넣는다.    
    const response = await axios.get<ScheduleResponse>(`http://localhost:8080/api/interviewees/schedule`, {
      params: { date },
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('면접 일정 조회 중 오류 발생:', error);
    throw error;
  }
};