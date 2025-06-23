package com.example.skaxis.interview.dto.interviewee;

<<<<<<< HEAD
import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interview.model.InterviewInterviewee;
import com.example.skaxis.interview.model.Interviewee;
=======
>>>>>>> origin/front-ai-face
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

<<<<<<< HEAD
=======
import java.time.LocalDate;
>>>>>>> origin/front-ai-face
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

<<<<<<< HEAD
=======
import com.example.skaxis.interview.model.Interviewee;

>>>>>>> origin/front-ai-face
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IntervieweeResponseDto {
<<<<<<< HEAD
    private Long interviewId;
    private Long intervieweeId;
    private String name;
    private LocalDateTime scheduledAt;
    private Interview.InterviewStatus status;
    private Integer score;
    private String interviewers;
    private String roomNo;
    private String comment;
    private LocalDateTime createdAt;

    public static IntervieweeResponseDto from(InterviewInterviewee interviewInterviewee) {
        Interview interview = interviewInterviewee.getInterview();
        Interviewee interviewee = interviewInterviewee.getInterviewee();

        return IntervieweeResponseDto.builder()
                .interviewId(interview.getInterviewId())
                .intervieweeId(interviewee.getIntervieweeId())
                .name(interviewee.getName())
                .scheduledAt(interview.getScheduledAt())
                .status(interview.getStatus())
                .score(interviewInterviewee.getScore())
                .interviewers(interview.getInterviewers())
                .roomNo(interview.getRoomNo())
                .comment(interviewInterviewee.getComment())
                .createdAt(interviewInterviewee.getCreatedAt())
                .build();
    }

    public static List<IntervieweeResponseDto> fromList(List<InterviewInterviewee> interviewInterviewees) {
        return interviewInterviewees.stream()
=======
    private Long intervieweeId;
    private String applicantName;
    private String applicantId;
    private LocalDate interviewDate;
    private String interviewStatus;
    private Integer score;
    private String interviewer;
    private String interviewLocation;
    private LocalDateTime createdAt;
    
    public static IntervieweeResponseDto from(Interviewee interviewee) {
        return IntervieweeResponseDto.builder()
                .intervieweeId(interviewee.getIntervieweeId())
                .score(interviewee.getScore())
                .createdAt(interviewee.getCreatedAt())
                .build();
    }
    
    public static List<IntervieweeResponseDto> fromList(List<Interviewee> interviewees) {
        return interviewees.stream()
>>>>>>> origin/front-ai-face
                .map(IntervieweeResponseDto::from)
                .collect(Collectors.toList());
    }
}