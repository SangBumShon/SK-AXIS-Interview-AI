package com.example.skaxis.controller;

import com.example.skaxis.dto.ExcelParseRequestDto;
import com.example.skaxis.dto.ExcelParseResponseDto;
import com.example.skaxis.dto.FileUploadResponseDto;
import com.example.skaxis.service.IntervieweeService;
import com.example.skaxis.service.MediaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/api/media")
@RequiredArgsConstructor
@Tag(name = "미디어 파일 관리", description = "STT 파일 업로드 및 관리 API")
public class MediaController {
    
    private final MediaService mediaService;
    private final IntervieweeService intervieweeService;
    
    @PostMapping(value = "/upload/stt", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "STT 파일 업로드", description = "음성 인식 결과 파일을 업로드합니다.")
    public ResponseEntity<FileUploadResponseDto> uploadSttFile(
            @Parameter(description = "업로드할 STT 파일")
            @RequestParam("file") MultipartFile file,
            @Parameter(description = "면접 결과 ID")
            @RequestParam("interviewResultId") Long interviewResultId) throws IOException {
        
        FileUploadResponseDto response = mediaService.uploadSttFile(file, interviewResultId);
        return ResponseEntity.ok(response);
    }

    @PostMapping(value = "/upload/excel", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
public ResponseEntity<FileUploadResponseDto> uploadExcelFile(
        @RequestParam("file") MultipartFile file) throws IOException {
    
    FileUploadResponseDto response = intervieweeService.uploadExcelFile(file);
    return ResponseEntity.ok(response);
}
@PostMapping("/parse/excel")
public ResponseEntity<ExcelParseResponseDto> parseExcelFile(
        @RequestBody ExcelParseRequestDto request) {
    
    ExcelParseResponseDto response = intervieweeService.parseExcelFile(request.getFilePath());
    return ResponseEntity.ok(response);
}
}