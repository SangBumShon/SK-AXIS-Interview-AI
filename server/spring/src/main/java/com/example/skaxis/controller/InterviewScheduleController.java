package com.example.skaxis.controller;

import com.example.skaxis.dto.InterviewScheduleResponseDto;
import com.example.skaxis.service.InterviewScheduleService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;

@RestController
@RequestMapping("/api/interview-schedule")
@RequiredArgsConstructor
@Tag(name = "면접 일정 관리", description = "면접 일정 조회 및 관리 API")
public class InterviewScheduleController {
    
    private final InterviewScheduleService interviewScheduleService;
    
    @GetMapping
    @Operation(summary = "날짜별 면접 일정 조회", description = "특정 날짜의 면접 일정 정보를 조회합니다.")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "조회 성공",
                content = @Content(schema = @Schema(implementation = InterviewScheduleResponseDto.class))),
        @ApiResponse(responseCode = "400", description = "잘못된 요청")
    })
    public ResponseEntity<InterviewScheduleResponseDto> getInterviewSchedule(
            @Parameter(description = "면접 날짜 (YYYY-MM-DD)", example = "2024-01-15", required = true)
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        
        InterviewScheduleResponseDto response = interviewScheduleService.getInterviewScheduleByDate(date);
        return ResponseEntity.ok(response);
    }
}