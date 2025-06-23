package com.example.skaxis.interview.dto;

import javax.management.relation.Role;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class GetInterviewByIdResponseDto {
    private Long interviewId;
    private String roomNo;
    private Integer round;
    private String scheduledAt;
    private Integer orderNo;
    private String status;
    private String createdAt;
    private IntervieweeDto[] interviewees;
    private InterviewerDto[] interviewers;

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class IntervieweeDto {
        private Long intervieweeId;
        private String name;
//        private String applicantCode;
        private String createdAt;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class InterviewerDto {
        private Long userId;
        private String userName;
        private String name;
        private String userType;
        private String createdAt;
    }
}
