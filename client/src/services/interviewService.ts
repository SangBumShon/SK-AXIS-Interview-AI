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
      
      // 지원자 추가
      const schedule = scheduleMap.get(key)!;
      if (!schedule.interviewees.includes(item.applicantName)) {
        schedule.interviewees.push(item.applicantName);
      }
    });
    
    return {
      schedules: Array.from(scheduleMap.values()),
      message: '면접 일정 조회 성공'
    };
  } catch (error) {
    console.error('면접 일정 조회 중 오류 발생:', error);
    throw error;
  }
};