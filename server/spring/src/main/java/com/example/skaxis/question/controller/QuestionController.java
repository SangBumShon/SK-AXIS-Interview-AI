package com.example.skaxis.question.controller;

import com.example.skaxis.question.dto.QuestionCreateRequest;
import com.example.skaxis.question.dto.QuestionUpdateRequest;
import com.example.skaxis.question.model.Question;
import com.example.skaxis.question.service.QuestionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/questions")
public class QuestionController {

    private final QuestionService questionService;

    @Autowired
    public QuestionController(QuestionService questionService) {
        this.questionService = questionService;
    }

    @GetMapping
    public ResponseEntity<List<Question>> getAllQuestions(
            @RequestParam(required = false) Long interview_id,
            @RequestParam(required = false) String type) {
        return ResponseEntity.ok(questionService.getAllQuestions(interview_id, type));
    }

    @PostMapping
    public ResponseEntity<Question> createQuestion(@RequestBody QuestionCreateRequest request) {
        Question createdQuestion = questionService.createQuestion(request);
        return new ResponseEntity<>(createdQuestion, HttpStatus.CREATED);
    }

    @PutMapping("/{question_id}")
    public ResponseEntity<Question> updateQuestion(
            @PathVariable("question_id") Long questionId,
            @RequestBody QuestionUpdateRequest request) {
        Question updatedQuestion = questionService.updateQuestion(questionId, request);
        return ResponseEntity.ok(updatedQuestion);
    }

    @DeleteMapping("/{question_id}")
    public ResponseEntity<Void> deleteQuestion(@PathVariable("question_id") Long questionId) {
        questionService.deleteQuestion(questionId);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
