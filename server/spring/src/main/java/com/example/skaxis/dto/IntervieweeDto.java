package com.example.skaxis.dto;

import com.example.skaxis.entity.InterviewStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

// 내부 DTO 클래스
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IntervieweeDto {
    private String name;
    private String position;
    private LocalDate interviewDate;
    private InterviewStatus interviewStatus;
    private Integer score;
    private String interviewer;
    private String interviewLocation;
}
