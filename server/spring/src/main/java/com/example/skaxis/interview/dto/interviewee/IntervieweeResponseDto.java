package com.example.skaxis.interview.dto.interviewee;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

import com.example.skaxis.interview.model.Interviewee;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IntervieweeResponseDto {
    private Long intervieweeId;
    private String applicantName;
    private String applicantId;
    private String position;
    private LocalDate interviewDate;
    private String interviewStatus;
    private Integer score;
    private String interviewer;
    private String interviewLocation;
    private LocalDateTime createdAt;
    
    public static IntervieweeResponseDto from(Interviewee interviewee) {
        return IntervieweeResponseDto.builder()
                .intervieweeId(interviewee.getIntervieweeId())
                .score(interviewee.getScore())
                .createdAt(interviewee.getCreatedAt())
                .build();
    }
    
    public static List<IntervieweeResponseDto> fromList(List<Interviewee> interviewees) {
        return interviewees.stream()
                .map(IntervieweeResponseDto::from)
                .collect(Collectors.toList());
    }
}