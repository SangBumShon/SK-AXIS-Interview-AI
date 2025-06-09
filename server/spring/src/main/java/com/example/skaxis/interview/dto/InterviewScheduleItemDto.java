package com.example.skaxis.interview.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InterviewScheduleItemDto {
    private LocalDate interviewDate;     // 면접날짜
    private String timeRange;            // 면접시간 (예: "09:00~09:30")
    private String roomName;             // 면접호실 (예: "면접실1")
    private String status;
    private List<String> interviewers;   // 면접관 이름들
    private List<String> interviewees;     // 지원자 이름들
}