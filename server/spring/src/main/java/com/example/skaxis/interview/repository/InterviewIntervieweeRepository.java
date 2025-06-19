package com.example.skaxis.interview.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.example.skaxis.interview.model.InterviewInterviewee;
import java.util.List;

public interface InterviewIntervieweeRepository extends JpaRepository<InterviewInterviewee, Long> {
    List<InterviewInterviewee> findByInterviewId(Long interviewId);
    List<InterviewInterviewee> findByIntervieweeId(Long intervieweeId);
    List<InterviewInterviewee> findByInterviewIdIn(List<Long> interviewIds); // 이 메서드를 추가하세요.
}