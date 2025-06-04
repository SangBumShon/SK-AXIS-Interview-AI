package com.example.skaxis.question.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class MultipleIntervieweeQuestionsRequest {
    private List<Long> interviewee_ids;
}
