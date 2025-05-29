package com.example.skaxis.dto;

import com.example.skaxis.entity.InterviewResult;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InterviewResultResponseDto {
    private Long id;
    private Long interviewId;
    private Long intervieweeId;
    private Integer score;
    private String comment;
    private String pdfPath;
    private String excelPath;
    private String mp3Path;
    private String mp4Path;
    private String sttPath;
    private LocalDateTime createdAt;
    
    public static InterviewResultResponseDto from(InterviewResult interviewResult) {
        return InterviewResultResponseDto.builder()
                .id(interviewResult.getId())
                .interviewId(interviewResult.getInterviewId())
                .intervieweeId(interviewResult.getIntervieweeId())
                .score(interviewResult.getScore())
                .comment(interviewResult.getComment())
                .pdfPath(interviewResult.getPdfPath())
                .excelPath(interviewResult.getExcelPath())
                .mp3Path(interviewResult.getMp3Path())
                .mp4Path(interviewResult.getMp4Path())
                .sttPath(interviewResult.getSttPath())
                .createdAt(interviewResult.getCreatedAt())
                .build();
    }
    
    public static List<InterviewResultResponseDto> fromList(List<InterviewResult> interviewResults) {
        return interviewResults.stream()
                .map(InterviewResultResponseDto::from)
                .collect(Collectors.toList());
    }
}