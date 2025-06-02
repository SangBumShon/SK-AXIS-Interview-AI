package com.example.skaxis.interviewinterviewee.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interviewee.model.Interviewee;

@Entity
@Table(name = "interview_interviewee")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InterviewInterviewee {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "interview_interviewee_id")
    private Long id;
    
    @Column(name = "interview_id", nullable = false)
    private Long interviewId;
    
    @Column(name = "interviewee_id", nullable = false)
    private Long intervieweeId;
    
    @Column(name = "score")
    private Integer score;
    
    @Column(name = "comment", columnDefinition = "TEXT")
    private String comment;
    
    @Column(name = "pdf_path", length = 255)
    private String pdfPath;
    
    @Column(name = "excel_path", length = 255)
    private String excelPath;
    
    @Column(name = "stt_path", length = 255)
    private String sttPath;
    
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    
    // 면접과의 관계
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "interview_id", insertable = false, updatable = false)
    private Interview interview;
    
    // 면접 대상자와의 관계
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "interviewee_id", insertable = false, updatable = false)
    private Interviewee interviewee;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}