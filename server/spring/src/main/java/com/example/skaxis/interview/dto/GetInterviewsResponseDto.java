package com.example.skaxis.interview.dto;

import com.example.skaxis.user.model.User;
import com.example.skaxis.interviewee.model.Interviewee;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetInterviewsResponseDto {
    private List<InterviewSession> interviewSessions;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class InterviewSession {
        @JsonProperty("interview_id")
        private Long interviewId;

        @JsonProperty("room_no")
        private String roomNo;

        private int round;

        @JsonProperty("scheduled_at")
        private String scheduledAt;

        @JsonProperty("order_no")
        private int orderNo;

        private String status;

        @JsonProperty("created_at")
        private String createdAt;

        private Interviewee[] interviewees;

        private User[] interviewers;
    }
}