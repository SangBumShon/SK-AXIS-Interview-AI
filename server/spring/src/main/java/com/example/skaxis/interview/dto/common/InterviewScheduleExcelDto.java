package com.example.skaxis.interview.dto.common;

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
    private LocalDate interviewDate;
    private LocalTime startTime;
    private LocalTime endTime;
    private String roomName;
    private List<String> interviewerNames;
    private List<String> intervieweeNames;
}