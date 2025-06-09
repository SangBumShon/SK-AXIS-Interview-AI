package com.example.skaxis.interview.repository;

import com.example.skaxis.interview.model.InterviewResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface InterviewResultRepository extends JpaRepository<InterviewResult, Long> {
    Optional<InterviewResult> findByInterviewIdAndIntervieweeId(Long interviewId, Long intervieweeId);
}
