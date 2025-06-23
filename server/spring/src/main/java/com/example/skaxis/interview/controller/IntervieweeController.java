package com.example.skaxis.interview.controller;

import com.example.skaxis.interview.dto.InterviewScheduleResponseDto;
import com.example.skaxis.interview.dto.SimpleInterviewScheduleResponseDto;
import com.example.skaxis.interview.dto.interviewee.IntervieweeListResponseDto;
import com.example.skaxis.interview.service.IntervieweeService;

<<<<<<< HEAD
=======

>>>>>>> origin/front-ai-face
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
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

@RestController
@RequestMapping("/api/v1/interviewees")
@RequiredArgsConstructor
@Tag(name = "면접 대상자 관리", description = "면접 대상자 정보 및 일정 관리 API")
public class IntervieweeController {
<<<<<<< HEAD

=======
    
>>>>>>> origin/front-ai-face
    private final IntervieweeService intervieweeService;

    @GetMapping("/simple")
    @Operation(summary = "면접 대상자 목록 조회", description = "필터 조건에 따라 면접 대상자 목록을 조회합니다.")
    @ApiResponses(value = {
<<<<<<< HEAD
            @ApiResponse(responseCode = "200", description = "조회 성공", content = @Content(schema = @Schema(implementation = IntervieweeListResponseDto.class))),
            @ApiResponse(responseCode = "400", description = "잘못된 요청")
    })
    public ResponseEntity<IntervieweeListResponseDto> getInterviewees(
            @Parameter(description = "면접 날짜 (YYYY-MM-DD)", example = "") @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date,
            @Parameter(description = "면접 상태", example = "") @RequestParam(required = false) String status,
            @Parameter(description = "직무", example = "") @RequestParam(required = false) String position) {

        IntervieweeListResponseDto response = intervieweeService.getInterviewees(date, status, position);
=======
        @ApiResponse(responseCode = "200", description = "조회 성공",
                content = @Content(schema = @Schema(implementation = IntervieweeListResponseDto.class))),
        @ApiResponse(responseCode = "400", description = "잘못된 요청")
    })
    public ResponseEntity<IntervieweeListResponseDto> getInterviewees(
            @Parameter(description = "면접 날짜 (YYYY-MM-DD)", example = "2024-01-15")
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date,
            @Parameter(description = "면접 상태", example = "SCHEDULED")
            @RequestParam(required = false) String status,
            @Parameter(description = "직무", example = "백엔드 개발자")
            @RequestParam(required = false) String position) {

        IntervieweeListResponseDto response = null;
//                intervieweeService.getInterviewees(date, status, position);
>>>>>>> origin/front-ai-face
        return ResponseEntity.ok(response);
    }

    @GetMapping("/interviews")
    @Operation(summary = "날짜별 면접 일정 조회", description = "특정 날짜의 면접 일정 정보를 조회합니다.")
    @ApiResponses(value = {
<<<<<<< HEAD
            @ApiResponse(responseCode = "200", description = "조회 성공", content = @Content(schema = @Schema(implementation = SimpleInterviewScheduleResponseDto.class))),
            @ApiResponse(responseCode = "400", description = "잘못된 요청")
    })
    public ResponseEntity<SimpleInterviewScheduleResponseDto> getInterviewSchedule(
            @Parameter(description = "면접 날짜 (YYYY-MM-DD)", example = "2024-01-15", required = true) @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {

        SimpleInterviewScheduleResponseDto response = intervieweeService.getSimpleInterviewScheduleByDate(date);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/interviews/all")
    @Operation(summary = "전체 면접 일정 조회", description = "모든 날짜의 면접 일정 정보를 조회합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "조회 성공", content = @Content(schema = @Schema(implementation = SimpleInterviewScheduleResponseDto.class))),
            @ApiResponse(responseCode = "400", description = "잘못된 요청")
    })
    public ResponseEntity<SimpleInterviewScheduleResponseDto> getAllInterviewSchedules(
            @Parameter(description = "면접 상태별 필터 (SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED)", required = false) @RequestParam(required = false) String status) {
=======
        @ApiResponse(responseCode = "200", description = "조회 성공",
                content = @Content(schema = @Schema(implementation = SimpleInterviewScheduleResponseDto.class))),
        @ApiResponse(responseCode = "400", description = "잘못된 요청")
    })
    public ResponseEntity<SimpleInterviewScheduleResponseDto> getInterviewSchedule(
            @Parameter(description = "면접 날짜 (YYYY-MM-DD)", example = "2024-01-15", required = true)
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        
        SimpleInterviewScheduleResponseDto response = intervieweeService.getSimpleInterviewScheduleByDate(date);
        return ResponseEntity.ok(response);
    }
    @GetMapping("/interviews/all")
    @Operation(summary = "전체 면접 일정 조회", description = "모든 날짜의 면접 일정 정보를 조회합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "조회 성공",
                    content = @Content(schema = @Schema(implementation = SimpleInterviewScheduleResponseDto.class))),
            @ApiResponse(responseCode = "400", description = "잘못된 요청")
    })
    public ResponseEntity<SimpleInterviewScheduleResponseDto> getAllInterviewSchedules(
            @Parameter(description = "면접 상태별 필터 (SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED)", required = false)
            @RequestParam (required = false) String status) {
>>>>>>> origin/front-ai-face
        System.out.println("조회 필터 status = " + status);
        SimpleInterviewScheduleResponseDto response = intervieweeService.getAllSimpleInterviewSchedules(status);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/interviews/detailed")
    @Operation(summary = "상세한 날짜별 면접 일정 조회", description = "특정 날짜의 면접 일정 정보를 상세한 형식으로 조회합니다.")
    @ApiResponses(value = {
<<<<<<< HEAD
            @ApiResponse(responseCode = "200", description = "조회 성공", content = @Content(schema = @Schema(implementation = InterviewScheduleResponseDto.class))),
            @ApiResponse(responseCode = "400", description = "잘못된 요청")
    })
    public ResponseEntity<InterviewScheduleResponseDto> getDetailedInterviewSchedule(
            @Parameter(description = "면접 날짜 (YYYY-MM-DD)", example = "2024-01-15", required = true) @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {

=======
        @ApiResponse(responseCode = "200", description = "조회 성공",
                content = @Content(schema = @Schema(implementation = InterviewScheduleResponseDto.class))),
        @ApiResponse(responseCode = "400", description = "잘못된 요청")
    })
    public ResponseEntity<InterviewScheduleResponseDto> getDetailedInterviewSchedule(
            @Parameter(description = "면접 날짜 (YYYY-MM-DD)", example = "2024-01-15", required = true)
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        
>>>>>>> origin/front-ai-face
        InterviewScheduleResponseDto response = intervieweeService.getInterviewScheduleByDate(date);
        return ResponseEntity.ok(response);
    }
}