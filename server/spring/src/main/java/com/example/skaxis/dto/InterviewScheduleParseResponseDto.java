package com.example.skaxis.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InterviewScheduleParseResponseDto {
    private int successCount;               // 성공한 일정 수
    private int errorCount;                 // 실패한 일정 수
    private List<String> errors;            // 오류 메시지들
    private String message;                 // 전체 결과 메시지
}