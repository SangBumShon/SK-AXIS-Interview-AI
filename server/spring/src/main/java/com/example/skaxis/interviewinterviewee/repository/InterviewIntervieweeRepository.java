package com.example.skaxis.interviewinterviewee.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.skaxis.interviewinterviewee.model.InterviewInterviewee;

import java.util.List;

@Repository
public interface InterviewIntervieweeRepository extends JpaRepository<InterviewInterviewee, Long> {
    
    List<InterviewInterviewee> findByInterviewId(Long interviewId);

    List<InterviewInterviewee> findByIntervieweeId(Long intervieweeId);
}