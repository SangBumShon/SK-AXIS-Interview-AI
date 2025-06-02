package com.example.skaxis.interviewinterviewer.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.skaxis.interviewinterviewer.model.InterviewerAssignment;

import java.util.List;

@Repository
public interface InterviewerAssignmentRepository extends JpaRepository<InterviewerAssignment, Long> {
    
    List<InterviewerAssignment> findByInterviewId(Long interviewId);
}