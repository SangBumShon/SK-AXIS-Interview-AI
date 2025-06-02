package com.example.skaxis.util.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FileUploadResponseDto {
    private String message;
    private String filePath;
    private String fileName;
    private LocalDateTime uploadTime;
    private Integer successCount;
    private Integer errorCount;
    private List<String> errors;
}