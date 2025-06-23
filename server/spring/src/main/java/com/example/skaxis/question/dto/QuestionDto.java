package com.example.skaxis.question.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class QuestionDto {
    private int questionId;
    private String type; // "공통질문" 또는 "개별질문"
    private String content;
}