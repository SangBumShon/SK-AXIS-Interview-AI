package com.example.skaxis.question.repository;

import com.example.skaxis.question.model.Question;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface QuestionRepository extends JpaRepository<Question, Long> {
    List<Question> findByInterviewId(Long interviewId);
    List<Question> findByType(String type);
    List<Question> findByInterviewIdAndType(Long interviewId, String type);
}
