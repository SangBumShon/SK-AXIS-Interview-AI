import axios from 'axios';

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
    const response = await axios.get<ScheduleResponse>(`http://localhost:8080/api/interviewees/schedule`, {
      params: { date }
    });
    return response.data;
  } catch (error) {
    console.error('면접 일정 조회 중 오류 발생:', error);
    throw error;
  }
}; 