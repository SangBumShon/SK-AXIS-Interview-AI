package com.example.skaxis.service;

import com.example.skaxis.dto.InterviewScheduleResponseDto;
import com.example.skaxis.dto.PersonDto;
import com.example.skaxis.dto.RoomDto;
import com.example.skaxis.dto.TimeSlotDto;
import com.example.skaxis.entity.*;
import com.example.skaxis.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import com.example.skaxis.user.repository.UserRepository;
import com.example.skaxis.user.Role;
import com.example.skaxis.user.model.User;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class InterviewScheduleService {
    
    private final InterviewRepository interviewRepository;
    private final IntervieweeRepository intervieweeRepository;
    private final InterviewerAssignmentRepository interviewerAssignmentRepository;
    private final UserRepository userRepository;
    private final InterviewIntervieweeRepository interviewIntervieweeRepository;
    
    public InterviewScheduleResponseDto getInterviewScheduleByDate(LocalDate date) {
        try {
            // 해당 날짜의 면접 일정 조회
            List<Interview> interviews = interviewRepository.findByScheduledDate(date);
            
            // 해당 날짜의 면접 대상자 조회
            List<Interviewee> interviewees = intervieweeRepository.findByInterviewDateOrderByTime(date);
            
            // 면접실 정보 생성 (하드코딩된 데이터 또는 DB에서 조회)
            List<RoomDto> rooms = Arrays.asList(
                new RoomDto("room1", "면접실 1"),
                new RoomDto("room2", "면접실 2"),
                new RoomDto("room3", "면접실 3")
            );
            
            // 시간대별 면접 일정 생성
            List<TimeSlotDto> timeSlots = createTimeSlots(interviews, interviewees);
            
            // 관련된 모든 사람들 정보 생성
            List<PersonDto> people = createPeopleList(interviews, interviewees);
            
            return new InterviewScheduleResponseDto(
                rooms,
                timeSlots,
                people,
                "면접 일정이 성공적으로 조회되었습니다."
            );
            
        } catch (Exception e) {
            log.error("면접 일정 조회 중 오류 발생: {}", e.getMessage());
            return new InterviewScheduleResponseDto(
                new ArrayList<>(),
                new ArrayList<>(),
                new ArrayList<>(),
                "면접 일정 조회 중 오류가 발생했습니다: " + e.getMessage()
            );
        }
    }
    
    private List<TimeSlotDto> createTimeSlots(List<Interview> interviews, List<Interviewee> interviewees) {
        Map<String, TimeSlotDto> timeSlotMap = new HashMap<>();
        
        // 면접별로 시간대 생성
        for (Interview interview : interviews) {
            String timeRange = formatTimeRange(interview.getScheduledAt());
            String slotKey = interview.getRoomId() + "_" + timeRange;
            
            TimeSlotDto timeSlot = timeSlotMap.computeIfAbsent(slotKey, k -> {
                TimeSlotDto slot = new TimeSlotDto();
                slot.setId("ts_" + interview.getInterviewId());
                slot.setRoomId(interview.getRoomId() != null ? interview.getRoomId() : "room1");
                slot.setTimeRange(timeRange);
                slot.setInterviewerIds(new ArrayList<>());
                slot.setCandidateIds(new ArrayList<>());
                return slot;
            });
            
            // 면접관 정보 추가
            List<InterviewerAssignment> assignments = interviewerAssignmentRepository.findByInterviewId(interview.getInterviewId());
            for (InterviewerAssignment assignment : assignments) {
                String interviewerId = "i" + assignment.getUserName();
                if (!timeSlot.getInterviewerIds().contains(interviewerId)) {
                    timeSlot.getInterviewerIds().add(interviewerId);
                }
            }
            
            // 면접 대상자 정보 추가
            
            // 수정해야 할 코드
            List<InterviewInterviewee> results = interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());
            for (InterviewInterviewee result : results) {
            String candidateId = "c" + result.getIntervieweeId();
            if (!timeSlot.getCandidateIds().contains(candidateId)) {
            timeSlot.getCandidateIds().add(candidateId);
            }
            }
        }
        
        // 면접 대상자만 있는 경우 (면접이 아직 생성되지 않은 경우)
        for (Interviewee interviewee : interviewees) {
            if (interviewee.getInterviewDate() != null) {
                String timeRange = "09:00 - 10:00"; // 기본 시간대
                String roomId = "room1"; // 기본 면접실
                String slotKey = roomId + "_" + timeRange;
                
                TimeSlotDto timeSlot = timeSlotMap.computeIfAbsent(slotKey, k -> {
                    TimeSlotDto slot = new TimeSlotDto();
                    slot.setId("ts_interviewee_" + interviewee.getIntervieweeId());
                    slot.setRoomId(roomId);
                    slot.setTimeRange(timeRange);
                    slot.setInterviewerIds(Arrays.asList("i1", "i2", "i3")); // 기본 면접관들
                    slot.setCandidateIds(new ArrayList<>());
                    return slot;
                });
                
                String candidateId = "c" + interviewee.getIntervieweeId();
                if (!timeSlot.getCandidateIds().contains(candidateId)) {
                    timeSlot.getCandidateIds().add(candidateId);
                }
            }
        }
        
        return new ArrayList<>(timeSlotMap.values());
    }
    
    private List<PersonDto> createPeopleList(List<Interview> interviews, List<Interviewee> interviewees) {
        List<PersonDto> people = new ArrayList<>();
        
        // 면접관 정보 추가
        List<User> interviewers = userRepository.findByUserType(Role.INTERVIEWER);
        for (User interviewer : interviewers) {
            people.add(new PersonDto(
                "i" + interviewer.getUserName(),
                interviewer.getName(),
                "interviewer"
            ));
        }
        
        // 면접 대상자 정보 추가
        for (Interviewee interviewee : interviewees) {
            people.add(new PersonDto(
                "c" + interviewee.getIntervieweeId(),
                interviewee.getApplicantName(),
                "candidate"
            ));
        }
        
        return people;
    }
    
    private String formatTimeRange(java.time.LocalDateTime scheduledAt) {
        DateTimeFormatter timeFormatter = DateTimeFormatter.ofPattern("HH:mm");
        String startTime = scheduledAt.format(timeFormatter);
        String endTime = scheduledAt.plusHours(1).format(timeFormatter); // 1시간 후를 종료 시간으로 가정
        return startTime + " - " + endTime;
    }
}