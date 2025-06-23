package com.example.skaxis.interview.repository;

import org.springframework.data.jpa.repository.JpaRepository;
<<<<<<< HEAD
import com.example.skaxis.interview.model.InterviewInterviewee;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface InterviewIntervieweeRepository extends JpaRepository<InterviewInterviewee, Long> {
    List<InterviewInterviewee> findByInterviewId(Long interviewId);
    List<InterviewInterviewee> findByIntervieweeId(Long intervieweeId);
    List<InterviewInterviewee> findByInterviewIdIn(List<Long> interviewIds); // 이 메서드를 추가하세요.

    @Query("SELECT ii FROM InterviewInterviewee ii JOIN FETCH ii.interview JOIN FETCH ii.interviewee")
    List<InterviewInterviewee> findAllWithInterviewAndInterviewee();
=======
import org.springframework.stereotype.Repository;

import com.example.skaxis.interview.model.InterviewInterviewee;

import java.util.List;

@Repository
public interface InterviewIntervieweeRepository extends JpaRepository<InterviewInterviewee, Long> {
    
    List<InterviewInterviewee> findByInterviewId(Long interviewId);

    List<InterviewInterviewee> findByIntervieweeId(Long intervieweeId);
>>>>>>> origin/front-ai-face
}