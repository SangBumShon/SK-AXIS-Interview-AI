package com.example.skaxis.interview.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

import com.example.skaxis.interview.model.InterviewInterviewee;

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

    @Column(name = "score")
    private Integer score;
    
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    
    // 면접-면접 대상자 관계
    @OneToMany(mappedBy = "interviewee", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<InterviewInterviewee> interviewInterviewees;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}