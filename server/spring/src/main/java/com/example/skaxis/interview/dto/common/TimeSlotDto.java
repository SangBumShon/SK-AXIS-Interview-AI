package com.example.skaxis.interview.dto.common;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TimeSlotDto {
    private String id;
    private String roomId;
    private String timeRange;
    private List<String> interviewerIds;
    private List<String> candidateIds;
}