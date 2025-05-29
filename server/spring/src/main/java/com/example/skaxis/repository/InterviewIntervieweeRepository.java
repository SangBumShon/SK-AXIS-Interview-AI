package com.example.skaxis.repository;

import com.example.skaxis.entity.InterviewInterviewee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface InterviewIntervieweeRepository extends JpaRepository<InterviewInterviewee, Long> {
    
    List<InterviewInterviewee> findByInterviewId(Long interviewId);
    
    List<InterviewInterviewee> findByIntervieweeId(Long intervieweeId);
    
    List<InterviewInterviewee> findByInterviewIdAndIntervieweeId(Long interviewId, Long intervieweeId);
}