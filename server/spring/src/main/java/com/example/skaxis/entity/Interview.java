package com.example.skaxis.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;


@Entity
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "interview")
public class Interview {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "interview_id")
    private Long interviewId;
    
    @Column(name = "room_id", length = 20)
    private String roomId;
    
    @Column(name = "round", nullable = false)
    private Integer round;
    
    @Column(name = "scheduled_at", nullable = false)
    private LocalDateTime scheduledAt;
    
    @Column(name = "scheduled_end_at", nullable = false)
    private LocalDateTime scheduledEndAt;
    
    @Column(name = "order_no")
    private Integer orderNo;
    
    // 면접관 정보를 단순 문자열로 저장 (쉼표로 구분)
    @Column(name = "interviewers", length = 500)
    private String interviewers;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    private InterviewStatus status;
    
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    
    // 면접-면접 대상자 관계만 유지
    @OneToMany(mappedBy = "interview", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<InterviewInterviewee> interviewInterviewees;
    
    // ... 기존 메서드들 유지
}