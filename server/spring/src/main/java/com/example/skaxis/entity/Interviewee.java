package com.example.skaxis.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "interviewees")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Interviewee {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "applicant_name", nullable = false)
    private String applicantName;
    
    @Column(name = "applicant_id", unique = true, nullable = false)
    private String applicantId;
    
    @Column(name = "position", nullable = false)
    private String position;
    
    @Column(name = "interview_date")
    private LocalDate interviewDate;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "interview_status")
    private InterviewStatus interviewStatus;
    
    @Column(name = "score")
    private Integer score;
    
    @Column(name = "interviewer")
    private String interviewer;
    
    @Column(name = "interview_location")
    private String interviewLocation;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
    
    public enum InterviewStatus {
        대기중, 진행중, 완료, 취소
    }
}