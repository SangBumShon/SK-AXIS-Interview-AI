package com.example.skaxis.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InterviewScheduleExcelDto {
    private LocalDate interviewDate;        // 면접날짜
    private LocalTime startTime;            // 시작시간
    private LocalTime endTime;              // 종료시간
    private String roomName;                // 면접 호실
    private List<String> interviewerNames;  // 면접관 이름들
    private List<String> intervieweeNames;  // 지원자 이름들
}