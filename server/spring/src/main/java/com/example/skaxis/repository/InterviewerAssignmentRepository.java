package com.example.skaxis.repository;

import com.example.skaxis.entity.InterviewerAssignment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface InterviewerAssignmentRepository extends JpaRepository<InterviewerAssignment, Long> {
    
    List<InterviewerAssignment> findByInterviewId(Long interviewId);
    
    List<InterviewerAssignment> findByUserId(Long userId);
}