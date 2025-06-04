package com.example.skaxis.interviewresult.model;

import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interviewee.model.Interviewee;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "interview_result")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InterviewResult {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "result_id")
    private Long resultId;
    
    @Column(name = "interview_id", nullable = false)
    private Long interviewId;
    
    @Column(name = "interviewee_id", nullable = false)
    private Long intervieweeId;
    
    @Column(name = "score")
    private Integer score;
    
    @Column(name = "comment", columnDefinition = "TEXT")
    private String comment;
    
    @Column(name = "pdf_path")
    private String pdfPath;
    
    @Column(name = "excel_path")
    private String excelPath;
    
    @Column(name = "stt_path")
    private String sttPath;
    
    // 면접과의 관계
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "interview_id", insertable = false, updatable = false)
    private Interview interview;
    
    // 지원자와의 관계
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "interviewee_id", insertable = false, updatable = false)
    private Interviewee interviewee;
}
