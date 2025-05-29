package com.example.skaxis.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FileUploadResponseDto {
    private String message;
    private String filePath;
    private String fileName;
    private LocalDateTime uploadTime;
}