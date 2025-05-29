package com.example.skaxis.repository;

import com.example.skaxis.entity.InterviewResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface InterviewResultRepository extends JpaRepository<InterviewResult, Long> {
    
    List<InterviewResult> findByInterviewId(Long interviewId);
    
    List<InterviewResult> findByIntervieweeId(Long intervieweeId);
    
    List<InterviewResult> findByInterviewIdAndIntervieweeId(Long interviewId, Long intervieweeId);
}