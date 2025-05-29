package com.example.skaxis.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ExcelParseResponseDto {
    private String message;
    private Integer processedCount;
    private Integer successCount;
    private Integer errorCount;
    private List<ParseError> errors;
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ParseError {
        private Integer row;
        private String errorMessage;
    }
}