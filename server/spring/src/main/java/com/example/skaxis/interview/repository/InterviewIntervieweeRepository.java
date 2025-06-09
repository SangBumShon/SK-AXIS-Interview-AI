package com.example.skaxis.interview.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.skaxis.interview.model.InterviewInterviewee;

import java.util.List;

@Repository
public interface InterviewIntervieweeRepository extends JpaRepository<InterviewInterviewee, Long> {
    
    List<InterviewInterviewee> findByInterviewId(Long interviewId);

    List<InterviewInterviewee> findByIntervieweeId(Long intervieweeId);
}