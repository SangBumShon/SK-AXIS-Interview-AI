package com.example.skaxis.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "interview_table")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
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
    
    @Column(name = "order_no")
    private Integer orderNo;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    private InterviewStatus status;
    
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    
    // 면접-면접관 관계 (다대다)
    @OneToMany(mappedBy = "interview", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<InterviewerAssignment> interviewerAssignments;
    
    // 면접-면접 대상자 관계 (다대다)
    @OneToMany(mappedBy = "interview", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<InterviewResult> interviewResults;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (status == null) {
            status = InterviewStatus.SCHEDULED;
        }
    }
    
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