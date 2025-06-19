package com.example.skaxis.interview.controller;


import com.example.skaxis.interview.dto.common.FileUploadResponseDto;
import com.example.skaxis.interview.service.IntervieweeService;
import com.example.skaxis.interview.service.MediaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/api/v1/uploads")
@RequiredArgsConstructor
@Tag(name = "미디어 파일 관리", description = "STT 파일 업로드 및 관리 API")
public class MediaController {
    
    private final MediaService mediaService;
    
    @PostMapping(value = "/stt", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "STT 파일 업로드", description = "음성 인식 결과 파일을 업로드합니다.")
    public ResponseEntity<?> uploadSttFile(
            @Parameter(description = "업로드할 STT 파일")
            @RequestParam("file") MultipartFile file,
            @Parameter(description = "면접 결과 ID")
            @RequestParam("interviewResultId") Long interviewResultId) throws IOException {
        if (file.isEmpty() || !file.getOriginalFilename().endsWith(".txt")) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Invalid file type. Please upload a valid STT text file.");
        }
        if (file.getSize() == 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("File is empty. Please upload a valid file.");
        }
        if (interviewResultId == null || interviewResultId <= 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Invalid interview result ID.");
        }

        FileUploadResponseDto response = mediaService.uploadSttFile(file, interviewResultId);
        return ResponseEntity.ok(response);
    }

    @PostMapping(value = "/interview-schedule", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "면접 일정 엑셀 파일 업로드", description = "면접 일정이 포함된 엑셀 파일을 업로드합니다.")
    public ResponseEntity<?> uploadInterviewScheduleExcel(
            @Parameter(description = "업로드할 면접 일정 엑셀 파일 (.xlsx, .xls)")
            @RequestParam("file") MultipartFile file) throws IOException {
        if (file.isEmpty() || (!file.getOriginalFilename().endsWith(".xlsx") && !file.getOriginalFilename().endsWith(".xls"))) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Invalid file type. Please upload a valid Excel file.");
        }
        if (file.getSize() == 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("File is empty. Please upload a valid file.");
        }
        FileUploadResponseDto response = mediaService.uploadAndProcessInterviewScheduleExcel(file);
        return ResponseEntity.ok(response);
    }
}

