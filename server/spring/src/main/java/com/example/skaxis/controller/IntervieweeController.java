package com.example.skaxis.controller;

import com.example.skaxis.dto.*;
import com.example.skaxis.service.IntervieweeService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDate;
import java.util.Map;

@RestController
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class IntervieweeController {
    
    private final IntervieweeService intervieweeService;
    
    @GetMapping("/interviewees")
    public ResponseEntity<IntervieweeListResponseDto> getInterviewees(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String position) {
        
        try {
            IntervieweeListResponseDto response = intervieweeService.getInterviewees(date, status, position);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("면접자 목록 조회 중 오류 발생", e);
            return ResponseEntity.badRequest().build();
        }
    }
    
    @PostMapping("/upload/excel")
    public ResponseEntity<?> uploadExcelFile(@RequestParam("file") MultipartFile file) {
        try {
            FileUploadResponseDto response = intervieweeService.uploadExcelFile(file);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            log.error("파일 업로드 중 오류 발생", e);
            return ResponseEntity.internalServerError().body(Map.of("error", "서버 오류가 발생했습니다."));
        }
    }
    
    @PostMapping("/parse/excel")
    public ResponseEntity<?> parseExcelFile(@RequestBody ExcelParseRequestDto request) {
        try {
            ExcelParseResponseDto response = intervieweeService.parseExcelFile(request.getFilePath());
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        } catch (RuntimeException e) {
            if (e.getMessage().contains("파일을 찾을 수 없음")) {
                return ResponseEntity.notFound().build();
            }
            log.error("Excel 파싱 중 오류 발생", e);
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            log.error("Excel 파싱 중 예상치 못한 오류 발생", e);
            return ResponseEntity.internalServerError().body(Map.of("error", "서버 오류가 발생했습니다."));
        }
    }
}