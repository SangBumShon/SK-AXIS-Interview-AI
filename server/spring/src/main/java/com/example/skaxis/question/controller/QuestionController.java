package com.example.skaxis.question.controller;

import com.example.skaxis.question.dto.QuestionCreateRequest;
import com.example.skaxis.question.dto.QuestionUpdateRequest;
import com.example.skaxis.question.model.Question;
import com.example.skaxis.question.service.QuestionService;

import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/questions")
public class QuestionController {
    private final QuestionService questionService;

    @GetMapping
    public ResponseEntity<?> getAllQuestions(
            @RequestParam(required = false) Long interview_id,
            @RequestParam(required = false) String type) {
        if (interview_id != null && interview_id <= 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("message", "Invalid interview_id"));
        }
        if (type != null && !List.of("공통질문", "개별질문").contains(type)) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("message", "Invalid type. Allowed values are: 공통질문, 개별질문"));
        }
        return ResponseEntity.ok(questionService.getAllQuestions(interview_id, type));
    }

    @PostMapping
    public ResponseEntity<?> createQuestion(@RequestBody QuestionCreateRequest request) {
        Question createdQuestion = questionService.createQuestion(request);
        if (createdQuestion == null) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("message", "Failed to create question. Please check the request data."));
        }
        return new ResponseEntity<>(createdQuestion, HttpStatus.CREATED);
    }

    @PutMapping("/{question_id}")
    public ResponseEntity<?> updateQuestion(
            @PathVariable("question_id") Long questionId,
            @RequestBody QuestionUpdateRequest request) {
        if (questionId == null || questionId <= 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("message", "Invalid question_id"));
        }
        if (request.getContent() == null || request.getContent().isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("message", "Question content is required"));
        }
        if (request.getType() != null && !List.of("공통질문", "개별질문").contains(request.getType())) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("message", "Invalid type. Allowed values are: 공통질문, 개별질문"));
        }
        Question updatedQuestion = questionService.updateQuestion(questionId, request);
        return ResponseEntity.ok(updatedQuestion);
    }

    @DeleteMapping("/{question_id}")
    public ResponseEntity<?> deleteQuestion(@PathVariable("question_id") Long questionId) {
        if (questionId == null || questionId <= 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("message", "Invalid question_id"));
        }
        questionService.deleteQuestion(questionId);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
