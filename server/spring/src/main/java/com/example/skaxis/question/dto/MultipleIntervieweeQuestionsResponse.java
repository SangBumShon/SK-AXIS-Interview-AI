package com.example.skaxis.question.dto;

import com.example.skaxis.question.model.Question;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MultipleIntervieweeQuestionsResponse {
    private Map<String, List<Question>> questions_per_interviewee;
}
