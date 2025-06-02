package com.example.skaxis.util.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

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