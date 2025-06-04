package com.example.skaxis.interviewresult.repository;

import com.example.skaxis.interviewresult.model.InterviewResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface InterviewResultRepository extends JpaRepository<InterviewResult, Long> {
    Optional<InterviewResult> findByInterviewIdAndIntervieweeId(Long interviewId, Long intervieweeId);
}
