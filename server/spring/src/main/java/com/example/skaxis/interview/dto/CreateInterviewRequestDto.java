package com.example.skaxis.interview.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreateInterviewRequestDto {
    private String roomNo;
    private int round;
    private String scheduledAt;
    private int orderNo;
    private String status;
    private Long[] intervieweeIds;
}
