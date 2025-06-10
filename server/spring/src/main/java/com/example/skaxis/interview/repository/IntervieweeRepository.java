package com.example.skaxis.interview.repository;

import com.example.skaxis.interview.model.InterviewInterviewee;
import com.example.skaxis.interview.model.Interviewee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface IntervieweeRepository extends JpaRepository<Interviewee, Long> {
    List<InterviewInterviewee> findByIntervieweeId(Long intervieweeId);

    Optional<Interviewee> findByName(String name);

    boolean existsByName(String name);
}