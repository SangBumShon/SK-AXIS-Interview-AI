package com.example.skaxis.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import com.example.skaxis.user.model.User;

@Entity
@Table(name = "interview_interviewer")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InterviewerAssignment {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "interview_interviewer_id")
    private Long id;
    
    @Column(name = "interview_id", nullable = false)
    private Long interviewId;
    
    @Column(name = "user_name", nullable = false)
    private String userName;
    
    // 면접과의 관계
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "interview_id", insertable = false, updatable = false)
    private Interview interview;
    
    // 면접관(사용자)과의 관계
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_name", insertable = false, updatable = false)
    private User user;
}