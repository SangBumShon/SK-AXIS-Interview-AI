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
    const response = await fetch(`http://3.38.218.18:8080/api/v1/interviews/simple?date=${date}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    return response.json();
  } catch (error) {
    console.error('면접 일정 조회 중 오류 발생:', error);
    throw error;
  }
};