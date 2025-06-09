package com.example.skaxis.interview.dto.interviewee;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class IntervieweeListResponseDto {
    private List<IntervieweeResponseDto> data;
    private Integer totalCount;
}