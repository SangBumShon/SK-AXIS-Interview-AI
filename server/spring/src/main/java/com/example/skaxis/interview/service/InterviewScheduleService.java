/*
package com.example.skaxis.interview.service;

// 이 서비스는 IntervieweeService로 통합되었습니다.
// 모든 기능이 IntervieweeService로 이동되었으므로 이 파일은 더 이상 사용되지 않습니다.

import com.example.skaxis.interview.dto.InterviewScheduleResponseDto;
import com.example.skaxis.interview.dto.SimpleInterviewScheduleResponseDto;
import com.example.skaxis.interview.dto.InterviewScheduleItemDto;
import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interview.repository.InterviewRepository;
import com.example.skaxis.interviewee.model.Interviewee;
import com.example.skaxis.interviewee.repository.IntervieweeRepository;
import com.example.skaxis.interviewinterviewee.model.InterviewInterviewee;
import com.example.skaxis.interviewinterviewee.repository.InterviewIntervieweeRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import com.example.skaxis.user.repository.UserRepository;
import com.example.skaxis.util.dto.PersonDto;
import com.example.skaxis.util.dto.RoomDto;
import com.example.skaxis.util.dto.TimeSlotDto;
import com.example.skaxis.user.Role;
import com.example.skaxis.user.model.User;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;
@Service
@RequiredArgsConstructor
@Slf4j
public class InterviewScheduleService {
    
    private final InterviewRepository interviewRepository;
    private final IntervieweeRepository intervieweeRepository;
    private final UserRepository userRepository;
    private final InterviewIntervieweeRepository interviewIntervieweeRepository;
    
    public InterviewScheduleResponseDto getInterviewScheduleByDate(LocalDate date) {
        try {
            // 해당 날짜의 면접 일정 조회
            List<Interview> interviews = interviewRepository.findByScheduledDate(date);
            
            // 해당 날짜의 면접에 참여하는 면접 대상자들을 Interview를 통해 조회
            List<Interviewee> interviewees = new ArrayList<>();
            for (Interview interview : interviews) {
                List<InterviewInterviewee> interviewInterviewees =
                    interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());

                for (InterviewInterviewee ii : interviewInterviewees) {
                    Interviewee interviewee = intervieweeRepository.findById(ii.getIntervieweeId())
                        .orElse(null);
                    if (interviewee != null && !interviewees.contains(interviewee)) {
                        interviewees.add(interviewee);
                    }
                }
            }
            
            // 데이터베이스에서 해당 날짜의 면접실 정보 동적 생성
            List<String> roomIds = interviewRepository.findDistinctRoomIdsByDate(date);
            List<RoomDto> rooms = roomIds.stream()
                .map(roomId -> new RoomDto(roomId, "면접실 " + roomId))
                .collect(Collectors.toList());

            // 만약 해당 날짜에 면접실이 없다면 전체 면접실 조회
            if (rooms.isEmpty()) {
                List<String> allRoomIds = interviewRepository.findDistinctRoomIds();
                rooms = allRoomIds.stream()
                    .map(roomId -> new RoomDto(roomId, "면접실 " + roomId))
                    .collect(Collectors.toList());
            }
            
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
            
            // 면접관 정보 추가 (Interview 엔티티의 interviewer 필드에서)
            if (interview.getInterviewers() != null && !interview.getInterviewers().isEmpty()) {
                // 면접관이 쉼표로 구분된 문자열인 경우 파싱
                String[] interviewerNames = interview.getInterviewers().split(",");
                for (int i = 0; i < interviewerNames.length; i++) {
                    String interviewerId = "i" + (i + 1); // 또는 실제 면접관 ID 로직
                    if (!timeSlot.getInterviewerIds().contains(interviewerId)) {
                        timeSlot.getInterviewerIds().add(interviewerId);
                    }
                }
            }
            
            // 해당 면접에 참여하는 면접 대상자 정보 추가
            List<InterviewInterviewee> interviewInterviewees = interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());
            for (InterviewInterviewee ii : interviewInterviewees) {
                String candidateId = "c" + ii.getIntervieweeId();
                if (!timeSlot.getCandidateIds().contains(candidateId)) {
                    timeSlot.getCandidateIds().add(candidateId);
                }
            }
        }
        
        // 기존의 interviewee 기반 로직은 제거
        // (면접 일정은 Interview 엔티티에서만 관리)
        
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
                interviewee.getName(),
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
*/