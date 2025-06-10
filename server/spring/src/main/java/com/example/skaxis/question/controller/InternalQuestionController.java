package com.example.skaxis.question.controller;

import com.example.skaxis.question.dto.MultipleIntervieweeQuestionsRequest;
import com.example.skaxis.question.dto.MultipleIntervieweeQuestionsResponse;
import com.example.skaxis.question.model.Question;
import com.example.skaxis.question.service.InternalQuestionService;

import lombok.RequiredArgsConstructor;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/internal")
public class InternalQuestionController {
    private final InternalQuestionService internalQuestionService;

    /**
     * 다중 지원자 질문 5개 조회 API (FastAPI → Spring Boot)
     * @param request 면접자 ID 목록
     * @return 면접자별 질문 목록
     */
    @PostMapping("/interviewees/questions")
    public ResponseEntity<?> getMultipleIntervieweeQuestions(
            @RequestBody MultipleIntervieweeQuestionsRequest request) {
        if (request.getInterviewee_ids() == null || request.getInterviewee_ids().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("message", "Invalid request data: interviewee_ids is required"));
        }
        
        Map<String, List<Question>> questionsPerInterviewee = 
                internalQuestionService.getQuestionsForMultipleInterviewees(request.getInterviewee_ids());
        
        MultipleIntervieweeQuestionsResponse response = MultipleIntervieweeQuestionsResponse.builder()
                .questions_per_interviewee(questionsPerInterviewee)
                .build();
        
        return ResponseEntity.ok(response);
    }
}
