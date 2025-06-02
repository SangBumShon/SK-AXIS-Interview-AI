package com.example.skaxis.interviewee.controller;

import com.example.skaxis.interview.dto.InterviewScheduleResponseDto;
import com.example.skaxis.interview.service.InterviewScheduleService;
import com.example.skaxis.interviewee.dto.IntervieweeListResponseDto;
import com.example.skaxis.interviewee.service.IntervieweeService;
import com.example.skaxis.util.dto.ExcelParseRequestDto;
import com.example.skaxis.util.dto.ExcelParseResponseDto;
import com.example.skaxis.util.dto.FileUploadResponseDto;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.time.LocalDate;

@RestController
@RequestMapping("/api/interviewees")
@RequiredArgsConstructor
@Tag(name = "면접 대상자 관리", description = "면접 대상자 정보 및 일정 관리 API")
public class IntervieweeController {
    
    private final IntervieweeService intervieweeService;
    private final InterviewScheduleService interviewScheduleService;
    
    @GetMapping
    @Operation(summary = "면접 대상자 목록 조회", description = "필터 조건에 따라 면접 대상자 목록을 조회합니다.")
    @ApiResponses(value = {
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
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/schedule")
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
    
    @PostMapping(value = "/excel/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "Excel 파일 업로드", description = "면접 대상자 정보가 포함된 Excel 파일을 업로드합니다.")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "업로드 성공",
                content = @Content(schema = @Schema(implementation = FileUploadResponseDto.class))),
        @ApiResponse(responseCode = "400", description = "잘못된 파일 형식")
    })
    public ResponseEntity<FileUploadResponseDto> uploadExcelFile(
            @Parameter(description = "업로드할 Excel 파일 (.xlsx, .xls)")
            @RequestParam("file") MultipartFile file) throws IOException {
        
        FileUploadResponseDto response = intervieweeService.uploadExcelFile(file);
        return ResponseEntity.ok(response);
    }
    
    @PostMapping("/excel/parse")
    @Operation(summary = "Excel 파일 파싱 및 저장", description = "업로드된 Excel 파일을 파싱하여 데이터베이스에 저장합니다.")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "파싱 및 저장 성공",
                content = @Content(schema = @Schema(implementation = ExcelParseResponseDto.class))),
        @ApiResponse(responseCode = "400", description = "파일 경로가 잘못됨"),
        @ApiResponse(responseCode = "500", description = "파싱 중 오류 발생")
    })
    public ResponseEntity<ExcelParseResponseDto> parseExcelFile(
            @RequestBody ExcelParseRequestDto request) {
        
        ExcelParseResponseDto response = intervieweeService.parseExcelFile(request.getFilePath());
        return ResponseEntity.ok(response);
    }
}