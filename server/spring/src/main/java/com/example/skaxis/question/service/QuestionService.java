package com.example.skaxis.question.service;

import com.example.skaxis.question.dto.QuestionCreateRequest;
import com.example.skaxis.question.dto.QuestionUpdateRequest;
import com.example.skaxis.question.model.Question;
import com.example.skaxis.question.repository.QuestionRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class QuestionService {

    private final QuestionRepository questionRepository;

    public List<Question> getAllQuestions(Long interviewId, String type) {
        if (interviewId != null && type != null) {
            return questionRepository.findByInterviewIdAndType(interviewId, type);
        } else if (interviewId != null) {
            return questionRepository.findByInterviewId(interviewId);
        } else if (type != null) {
            return questionRepository.findByType(type);
        } else {
            return questionRepository.findAll();
        }
    }

    @Transactional
    public Question createQuestion(QuestionCreateRequest request) {
        Question question = Question.builder()
                .interviewId(request.getInterview_id())
                .type(request.getType())
                .content(request.getContent())
                .build();
        
        return questionRepository.save(question);
    }

    @Transactional
    public Question updateQuestion(Long questionId, QuestionUpdateRequest request) {
        Question question = questionRepository.findById(questionId)
                .orElseThrow(() -> new EntityNotFoundException("질문을 찾을 수 없습니다. ID: " + questionId));
        
        if (request.getType() != null) {
            question.setType(request.getType());
        }
        
        if (request.getContent() != null) {
            question.setContent(request.getContent());
        }
        
        return questionRepository.save(question);
    }

    @Transactional
    public void deleteQuestion(Long questionId) {
        if (!questionRepository.existsById(questionId)) {
            throw new EntityNotFoundException("질문을 찾을 수 없습니다. ID: " + questionId);
        }
        
        questionRepository.deleteById(questionId);
    }
}
