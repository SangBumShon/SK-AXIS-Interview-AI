package com.example.skaxis.dto;

import com.example.skaxis.entity.Interviewee;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class IntervieweeResponseDto {
    private String applicantName;
    private String applicantId;
    private String position;
    private LocalDate interviewDate;
    private String interviewStatus;
    private Integer score;
    private String interviewer;
    private String interviewLocation;
    
    public static IntervieweeResponseDto from(Interviewee interviewee) {
        return new IntervieweeResponseDto(
            interviewee.getApplicantName(),
            interviewee.getApplicantId(),
            interviewee.getPosition(),
            interviewee.getInterviewDate(),
            interviewee.getInterviewStatus() != null ? interviewee.getInterviewStatus().name() : null,
            interviewee.getScore(),
            interviewee.getInterviewer(),
            interviewee.getInterviewLocation()
        );
    }
    
    public static List<IntervieweeResponseDto> fromList(List<Interviewee> interviewees) {
        return interviewees.stream()
                .map(IntervieweeResponseDto::from)
                .collect(Collectors.toList());
    }
}