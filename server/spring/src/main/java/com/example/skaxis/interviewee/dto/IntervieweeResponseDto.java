package com.example.skaxis.interviewee.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

import com.example.skaxis.interviewee.model.Interviewee;

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
                .applicantName(interviewee.getApplicantName())
                .applicantId(interviewee.getApplicantId())
                .position(interviewee.getPosition())
                .interviewDate(interviewee.getInterviewDate())
                .interviewStatus(interviewee.getInterviewStatus() != null ? 
                    interviewee.getInterviewStatus().getDescription() : null)
                .score(interviewee.getScore())
                .interviewer(interviewee.getInterviewer())
                .interviewLocation(interviewee.getInterviewLocation())
                .createdAt(interviewee.getCreatedAt())
                .build();
    }
    
    public static List<IntervieweeResponseDto> fromList(List<Interviewee> interviewees) {
        return interviewees.stream()
                .map(IntervieweeResponseDto::from)
                .collect(Collectors.toList());
    }
}