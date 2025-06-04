package com.example.skaxis.interview.service;

import com.example.skaxis.interview.dto.CreateInterviewRequestDto;
import com.example.skaxis.interview.dto.GetInterviewByIdResponseDto;
import com.example.skaxis.interview.dto.GetInterviewsResponseDto;
import com.example.skaxis.interview.dto.UpdateInterviewRequestDto;
import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interview.repository.InterviewRepository;
import com.example.skaxis.interviewee.model.Interviewee;
import com.example.skaxis.interviewee.repository.IntervieweeRepository;
import com.example.skaxis.interviewinterviewee.model.InterviewInterviewee;
import com.example.skaxis.interviewinterviewer.model.InterviewerAssignment;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import java.util.List;

import org.springframework.stereotype.Service;

import com.example.skaxis.user.model.User;
import com.example.skaxis.user.repository.UserRepository;

@Service
@RequiredArgsConstructor
@Slf4j
public class InterviewService {
    private final InterviewRepository interviewRepository;
    private final IntervieweeRepository intervieweeRepository;
    private final UserRepository userRepository;

    public GetInterviewsResponseDto getAllInterviews() {
        List<Interview> interviewList = interviewRepository.findAll();

        GetInterviewsResponseDto getInterviewsResponseDto = new GetInterviewsResponseDto();
        for (Interview interview : interviewList) {
            GetInterviewsResponseDto.InterviewSession interviewSession = new GetInterviewsResponseDto.InterviewSession();
            interviewSession.setInterviewId(interview.getInterviewId());
            interviewSession.setRoomNo(interview.getRoomNo());
            interviewSession.setRound(interview.getRound());
            interviewSession.setScheduledAt(interview.getScheduledAt().toString());
            interviewSession.setOrderNo(interview.getOrderNo());
            interviewSession.setStatus(interview.getStatus().name());
            interviewSession.setCreatedAt(interview.getCreatedAt().toString());

            List<Interviewee> intervieweeList = interview.getInterviewInterviewees()
                .stream()
                .map(i -> i.getInterviewee())
                .toList();
            interviewSession.setInterviewees(intervieweeList.toArray(new Interviewee[0]));

            List<User> interviewerList = interview.getInterviewerAssignments()
                .stream()
                .map(a -> a.getUser())
                .toList();
            interviewSession.setInterviewers(interviewerList.toArray(new User[0]));
            
            getInterviewsResponseDto.getInterviewSessions().add(interviewSession);
        }
        return getInterviewsResponseDto;
    }

    public void createInterview(CreateInterviewRequestDto createInterviewRequestDto) {
        Interview interview = new Interview();
        interview.setRoomNo(createInterviewRequestDto.getRoomNo());
        interview.setRound(createInterviewRequestDto.getRound());
        interview.setScheduledAt(java.time.LocalDateTime.parse(createInterviewRequestDto.getScheduledAt()));
        interview.setOrderNo(createInterviewRequestDto.getOrderNo());
        interview.setStatus(Interview.InterviewStatus.SCHEDULED);

        interviewRepository.save(interview);
    }

    public void deleteInterview(Long interviewId) {
        interviewRepository.deleteById(interviewId);
    }

    public void updateInterview(UpdateInterviewRequestDto updateInterviewRequestDto, Long interviewId) {
        Interview interview = interviewRepository.findById(interviewId)
            .orElseThrow(() -> new RuntimeException("Interview not found"));

        if (updateInterviewRequestDto.getRoomNo() != null) {
            interview.setRoomNo(updateInterviewRequestDto.getRoomNo());
        }
        if (updateInterviewRequestDto.getRound() != null) {
            interview.setRound(updateInterviewRequestDto.getRound());
        }
        if (updateInterviewRequestDto.getScheduledAt() != null) {   
            interview.setScheduledAt(java.time.LocalDateTime.parse(updateInterviewRequestDto.getScheduledAt()));
        }
        if (updateInterviewRequestDto.getOrderNo() != null) {
            interview.setOrderNo(updateInterviewRequestDto.getOrderNo());
        }
        if (updateInterviewRequestDto.getStatus() != null) {
            interview.setStatus(Interview.InterviewStatus.valueOf(updateInterviewRequestDto.getStatus()));
        }
        if (updateInterviewRequestDto.getIntervieweeIds() != null) {
            for (Long intervieweeId : updateInterviewRequestDto.getIntervieweeIds()) {
                Interviewee interviewee = intervieweeRepository.findById(intervieweeId)
                    .orElseThrow(() -> new RuntimeException("Interviewee not found with ID: " + intervieweeId));
                InterviewInterviewee interviewInterviewee = new InterviewInterviewee();
                interviewInterviewee.setInterview(interview);
                interviewInterviewee.setInterviewee(interviewee);
                interview.getInterviewInterviewees().add(interviewInterviewee);
                //TODO: Handle score, comment, pdfPath, excelPath, sttPath if needed
            }
        }

        if (updateInterviewRequestDto.getInterviewerIds() != null) {
            for (Long interviewerId : updateInterviewRequestDto.getInterviewerIds()) {
                User interviewer = userRepository.findById(interviewerId)
                    .orElseThrow(() -> new RuntimeException("Interviewer not found with ID: " + interviewerId));
                InterviewerAssignment interviewerAssignment = new InterviewerAssignment();
                interviewerAssignment.setInterview(interview);
                interviewerAssignment.setUser(interviewer);
                interview.getInterviewerAssignments().add(interviewerAssignment);
                //TODO: Handle additional fields if needed
            }
        }

        interviewRepository.save(interview);
    }

    public GetInterviewByIdResponseDto getInterviewById(Long interviewId) {
        Interview interview = interviewRepository.findById(interviewId)
            .orElseThrow(() -> new RuntimeException("Interview not found with ID: " + interviewId));
        GetInterviewByIdResponseDto getInterviewByIdResponseDto = new GetInterviewByIdResponseDto();
        getInterviewByIdResponseDto.setInterviewId(interview.getInterviewId());
        getInterviewByIdResponseDto.setRoomNo(interview.getRoomNo());
        getInterviewByIdResponseDto.setRound(interview.getRound());
        getInterviewByIdResponseDto.setScheduledAt(interview.getScheduledAt().toString());
        getInterviewByIdResponseDto.setOrderNo(interview.getOrderNo());
        getInterviewByIdResponseDto.setStatus(interview.getStatus().name());
        getInterviewByIdResponseDto.setCreatedAt(interview.getCreatedAt().toString());
        getInterviewByIdResponseDto.setInterviewees(interview.getInterviewInterviewees()
            .stream()
            .map(i -> new GetInterviewByIdResponseDto.IntervieweeDto(
                i.getInterviewee().getIntervieweeId(),
                i.getInterviewee().getName(),
                i.getInterviewee().getApplicantCode(),
                i.getCreatedAt().toString()))
            .toArray(GetInterviewByIdResponseDto.IntervieweeDto[]::new));
        getInterviewByIdResponseDto.setInterviewers(interview.getInterviewerAssignments()
            .stream()
            .map(i -> new GetInterviewByIdResponseDto.InterviewerDto(
                i.getUser().getUserId(),
                i.getUser().getUserName(),
                i.getUser().getName(),
                i.getUser().getUserType().getValue(),
                i.getUser().getCreatedAt().toString()))
            .toArray(GetInterviewByIdResponseDto.InterviewerDto[]::new));
        
        return getInterviewByIdResponseDto;
    }
}