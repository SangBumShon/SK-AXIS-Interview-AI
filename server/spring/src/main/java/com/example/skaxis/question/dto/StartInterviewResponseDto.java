package com.example.skaxis.question.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;
import java.util.Map;


@Data
@NoArgsConstructor
@AllArgsConstructor
public class StartInterviewResponseDto {
    private Map<String, List<QuestionDto>> questionsPerInterviewee;
    private String status;
}