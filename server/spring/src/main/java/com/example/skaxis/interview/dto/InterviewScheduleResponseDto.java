package com.example.skaxis.interview.dto;

public class InterviewScheduleResponseDto {
    private Long interviewId;
    private String candidateName;
    private String interviewDate;
    private String interviewTime;

    public InterviewScheduleResponseDto() {}

    public InterviewScheduleResponseDto(Long interviewId, String candidateName, String interviewDate, String interviewTime) {
        this.interviewId = interviewId;
        this.candidateName = candidateName;
        this.interviewDate = interviewDate;
        this.interviewTime = interviewTime;
    }

    public Long getInterviewId() { return interviewId; }
    public void setInterviewId(Long interviewId) { this.interviewId = interviewId; }

    public String getCandidateName() { return candidateName; }
    public void setCandidateName(String candidateName) { this.candidateName = candidateName; }

    public String getInterviewDate() { return interviewDate; }
    public void setInterviewDate(String interviewDate) { this.interviewDate = interviewDate; }

    public String getInterviewTime() { return interviewTime; }
    public void setInterviewTime(String interviewTime) { this.interviewTime = interviewTime; }
}
