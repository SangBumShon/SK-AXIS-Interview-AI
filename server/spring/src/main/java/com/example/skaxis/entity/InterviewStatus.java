package com.example.skaxis.entity;

import lombok.Getter;

// InterviewStatus enum
@Getter
public enum InterviewStatus {
    SCHEDULED("예정"),
    IN_PROGRESS("진행중"),
    COMPLETED("완료"),
    CANCELLED("취소");

    private final String description;

    InterviewStatus(String description) {
        this.description = description;
    }

}