package com.example.skaxis.interview.service;

import com.example.skaxis.interview.dto.CreateInterviewRequestDto;
import com.example.skaxis.interview.dto.GetInterviewByIdResponseDto;
import com.example.skaxis.interview.dto.GetInterviewsResponseDto;
import com.example.skaxis.interview.dto.UpdateInterviewRequestDto;
import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interview.model.InterviewInterviewee;
import com.example.skaxis.interview.model.Interviewee;
import com.example.skaxis.interview.repository.InterviewRepository;
import com.example.skaxis.interview.repository.IntervieweeRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.ArrayList;
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
    
            // 면접관 정보를 문자열로만 처리 (User 엔티티 사용하지 않음)
            String interviewersStr = interview.getInterviewers();
            if (interviewersStr != null && !interviewersStr.isEmpty()) {
                interviewersStr.split(",");
                // User 배열 대신 문자열 배열로 처리하거나, 더미 User 객체 생성
                // GetInterviewsResponseDto.InterviewSession의 setInterviewers가 User[] 타입을 받는다면
                // 더미 User 객체를 생성해야 합니다
                interviewSession.setInterviewers(new User[0]); // 임시로 빈 배열 설정
            } else {
                interviewSession.setInterviewers(new User[0]);
            }
    
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
            // InterviewerAssignment 대신 문자열로 저장
            List<String> interviewerNames = new ArrayList<>();
            for (Long interviewerId : updateInterviewRequestDto.getInterviewerIds()) {
                User interviewer = userRepository.findById(interviewerId)
                    .orElseThrow(() -> new RuntimeException("Interviewer not found with ID: " + interviewerId));
                interviewerNames.add(interviewer.getName());
            }
            interview.setInterviewers(String.join(",", interviewerNames));
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
        
        // 면접관 정보를 문자열로만 처리 (User 엔티티 사용하지 않음)
        String interviewersStr = interview.getInterviewers();
        if (interviewersStr != null && !interviewersStr.isEmpty()) {
            String[] interviewerNames = interviewersStr.split(",");
            List<GetInterviewByIdResponseDto.InterviewerDto> interviewerDtos = new ArrayList<>();
            for (int i = 0; i < interviewerNames.length; i++) {
                String name = interviewerNames[i].trim();
                // User 엔티티를 사용하지 않으므로 더미 데이터로 설정
                interviewerDtos.add(new GetInterviewByIdResponseDto.InterviewerDto(
                    (long) (i + 1), // 더미 userId
                    name, // userName으로 name 사용
                    name, // name
                    "INTERVIEWER", // 기본 userType
                    LocalDateTime.now().toString() // 더미 createdAt
                ));
            }
            getInterviewByIdResponseDto.setInterviewers(interviewerDtos.toArray(new GetInterviewByIdResponseDto.InterviewerDto[0]));
        } else {
            getInterviewByIdResponseDto.setInterviewers(new GetInterviewByIdResponseDto.InterviewerDto[0]);
        }
        
        return getInterviewByIdResponseDto;
    }

    // 공통 유틸리티 메서드들
    public Interview findInterviewById(Long interviewId) {
        return interviewRepository.findById(interviewId)
            .orElseThrow(() -> new RuntimeException("Interview not found with ID: " + interviewId));
    }

    public boolean existsById(Long interviewId) {
        return interviewRepository.existsById(interviewId);
    }

    public List<Interview> findInterviewsByDate(LocalDate date) {
        return interviewRepository.findByScheduledDate(date);
    }

    public List<String> findDistinctRoomIdsByDate(LocalDate date) {
        return interviewRepository.findDistinctRoomIdsByDate(date);
    }

    public List<String> findDistinctRoomIds() {
        return interviewRepository.findDistinctRoomIds();
    }

    public List<Interview> findByStatusOrderByScheduledAt(Interview.InterviewStatus status) {
        return interviewRepository.findByStatusOrderByScheduledAt(status);
    }

    public List<Interview> findAllOrderByScheduledAt() {
        return interviewRepository.findAllOrderByScheduledAt();
    }
}