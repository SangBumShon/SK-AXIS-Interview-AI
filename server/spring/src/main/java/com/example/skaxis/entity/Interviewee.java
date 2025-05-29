package com.example.skaxis.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "interviewee")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Interviewee {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "interviewee_id")
    private Long intervieweeId;
    
    @Column(name = "name", nullable = false, length = 50)
    private String name;
    
    @Column(name = "applicant_code", unique = true, length = 20)
    private String applicantCode;
    
    // 새로 추가된 필드들
    @Column(name = "applicant_name", nullable = false, length = 100)
    private String applicantName;
    
    @Column(name = "applicant_id", unique = true, nullable = false, length = 50)
    private String applicantId;
    
    @Column(name = "position", nullable = false, length = 100)
    private String position;
    
    @Column(name = "interview_date")
    private LocalDate interviewDate;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "interview_status")
    private InterviewStatus interviewStatus;
    
    @Column(name = "score")
    private Integer score;
    
    @Column(name = "interviewer", length = 100)
    private String interviewer;
    
    @Column(name = "interview_location", length = 200)
    private String interviewLocation;
    
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    
    // 면접-면접 대상자 관계
    @OneToMany(mappedBy = "interviewee", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<InterviewInterviewee> interviewInterviewees;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
    
    // InterviewStatus enum
    public enum InterviewStatus {
        SCHEDULED("예정"),
        IN_PROGRESS("진행중"),
        COMPLETED("완료"),
        CANCELLED("취소");
        
        private final String description;
        
        InterviewStatus(String description) {
            this.description = description;
        }
        
        public String getDescription() {
            return description;
        }
    }
}