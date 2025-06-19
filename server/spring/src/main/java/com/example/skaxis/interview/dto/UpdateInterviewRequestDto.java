package com.example.skaxis.interview.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateInterviewRequestDto {
    private String roomNo;
    private Integer round;
    private String scheduledAt;
    private Integer orderNo;
    private String status;
    private Long[] intervieweeIds;
}
