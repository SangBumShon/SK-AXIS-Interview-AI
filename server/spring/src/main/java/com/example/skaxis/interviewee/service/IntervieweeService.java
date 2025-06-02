package com.example.skaxis.interviewee.service;

import com.example.skaxis.interview.dto.InterviewScheduleItemDto;
import com.example.skaxis.interview.dto.InterviewScheduleResponseDto;
import com.example.skaxis.interview.dto.SimpleInterviewScheduleResponseDto;
import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interview.repository.InterviewRepository;
import com.example.skaxis.interviewee.model.Interviewee;
import com.example.skaxis.interviewee.repository.IntervieweeRepository;
import com.example.skaxis.interviewinterviewee.model.InterviewInterviewee;
import com.example.skaxis.interviewinterviewee.repository.InterviewIntervieweeRepository;
import com.example.skaxis.user.repository.UserRepository;
import com.example.skaxis.util.dto.PersonDto;
import com.example.skaxis.util.dto.RoomDto;
import com.example.skaxis.util.dto.TimeSlotDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class IntervieweeService {

    private final IntervieweeRepository intervieweeRepository;
    private final InterviewRepository interviewRepository;
    private final UserRepository userRepository;
    private final InterviewIntervieweeRepository interviewIntervieweeRepository;

    // 기본 CRUD 작업
    public List<Interviewee> getAllInterviewees() {
        return intervieweeRepository.findAll();
    }

    public Optional<Interviewee> getIntervieweeById(Long id) {
        return intervieweeRepository.findById(id);
    }

    public Optional<Interviewee> getIntervieweeByName(String name) {
        return intervieweeRepository.findByName(name);
    }

    public boolean existsByName(String name) {
        return intervieweeRepository.existsByName(name);
    }

    public Interviewee saveInterviewee(Interviewee interviewee) {
        return intervieweeRepository.save(interviewee);
    }

    public Interviewee createInterviewee(String name) {
        Interviewee interviewee = Interviewee.builder()
                .name(name)
                .createdAt(LocalDateTime.now())
                .build();
        return intervieweeRepository.save(interviewee);
    }

    public void deleteInterviewee(Long id) {
        intervieweeRepository.deleteById(id);
    }

    // 면접 일정 관련 기능들
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
            
            // 면접실이 없는 경우 기본 면접실 제공
            if (rooms.isEmpty()) {
                List<String> allRoomIds = interviewRepository.findDistinctRoomIds();
                rooms = allRoomIds.stream()
                    .map(roomId -> new RoomDto(roomId, "면접실 " + roomId))
                    .collect(Collectors.toList());
            }
            
            // 시간대별 면접 정보 생성
            List<TimeSlotDto> timeSlots = createTimeSlots(interviews, interviewees);
            
            // 사람 정보 생성 (면접관 + 지원자)
            List<PersonDto> people = createPeople(interviews, interviewees);
            
            return new InterviewScheduleResponseDto(rooms, timeSlots, people, "면접 일정이 성공적으로 조회되었습니다.");
            
        } catch (Exception e) {
            log.error("면접 일정 조회 중 오류 발생: {}", e.getMessage(), e);
            return new InterviewScheduleResponseDto(new ArrayList<>(), new ArrayList<>(), new ArrayList<>(), 
                "면접 일정 조회 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    public SimpleInterviewScheduleResponseDto getSimpleInterviewScheduleByDate(LocalDate date) {
        try {
            // 해당 날짜의 면접 일정 조회
            List<Interview> interviews = interviewRepository.findByScheduledDate(date);
            
            List<InterviewScheduleItemDto> schedules = new ArrayList<>();
            
            for (Interview interview : interviews) {
                // 면접관 이름들 파싱 (Interview 엔티티의 interviewers 필드에서)
                List<String> interviewerNames = parseInterviewers(interview.getInterviewers());
                
                // 해당 면접의 지원자들 조회
                List<InterviewInterviewee> interviewInterviewees = 
                    interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());
                
                List<String> interviewees = new ArrayList<>();
                for (InterviewInterviewee ii : interviewInterviewees) {
                    Interviewee interviewee = intervieweeRepository.findById(ii.getIntervieweeId())
                        .orElse(null);
                    if (interviewee != null && interviewee.getName() != null) {
                        interviewees.add(interviewee.getName());
                    }
                }
                
                // 시간 범위 포맷팅
                String timeRange = formatSimpleTimeRange(interview.getScheduledAt(), interview.getScheduledEndAt());
                
                InterviewScheduleItemDto scheduleItem = InterviewScheduleItemDto.builder()
                    .interviewDate(date)
                    .timeRange(timeRange)
                    .roomName(interview.getRoomId())
                    .interviewers(interviewerNames)
                    .interviewees(interviewees)
                    .build();
                    
                schedules.add(scheduleItem);
            }
            
            return SimpleInterviewScheduleResponseDto.builder()
                .schedules(schedules)
                .message("면접 일정이 성공적으로 조회되었습니다.")
                .build();
                
        } catch (Exception e) {
            log.error("면접 일정 조회 중 오류 발생: {}", e.getMessage(), e);
            return SimpleInterviewScheduleResponseDto.builder()
                .schedules(new ArrayList<>())
                .message("면접 일정 조회 중 오류가 발생했습니다: " + e.getMessage())
                .build();
        }
    }

    private List<TimeSlotDto> createTimeSlots(List<Interview> interviews, List<Interviewee> interviewees) {
        Map<String, TimeSlotDto> timeSlotMap = new HashMap<>();
        
        // 면접별로 시간대 생성
        for (Interview interview : interviews) {
            String timeRange = formatTimeRange(interview.getScheduledAt());
            String timeSlotId = "ts_" + interview.getInterviewId();
            
            // 해당 면접의 면접관들 (Interview 엔티티의 interviewers 필드에서 파싱)
            List<String> interviewerIds = parseInterviewers(interview.getInterviewers());
            
            // 해당 면접의 지원자들
            List<InterviewInterviewee> interviewInterviewees = 
                interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());
            List<String> candidateIds = new ArrayList<>();
            
            for (InterviewInterviewee ii : interviewInterviewees) {
                candidateIds.add("c" + ii.getIntervieweeId());
            }
            
            TimeSlotDto timeSlot = new TimeSlotDto(
                timeSlotId,
                interview.getRoomId(),
                timeRange,
                interviewerIds.stream().map(name -> "i_" + name.hashCode()).collect(Collectors.toList()),
                candidateIds
            );
            
            timeSlotMap.put(timeSlotId, timeSlot);
        }
        
        return new ArrayList<>(timeSlotMap.values());
    }

    private List<PersonDto> createPeople(List<Interview> interviews, List<Interviewee> interviewees) {
        List<PersonDto> people = new ArrayList<>();
        
        // 지원자 정보 추가
        for (Interviewee interviewee : interviewees) {
            people.add(new PersonDto(
                "c" + interviewee.getIntervieweeId(),
                interviewee.getName() != null ? interviewee.getName() : "이름 없음",
                "candidate"
            ));
        }
        
        // 면접관 정보 추가 (Interview 엔티티의 interviewers 필드에서)
        for (Interview interview : interviews) {
            List<String> interviewerNames = parseInterviewers(interview.getInterviewers());
            for (String interviewerName : interviewerNames) {
                String interviewerId = "i_" + interviewerName.hashCode();
                // 중복 제거
                boolean exists = people.stream().anyMatch(p -> p.getId().equals(interviewerId));
                if (!exists) {
                    people.add(new PersonDto(interviewerId, interviewerName, "interviewer"));
                }
            }
        }
        
        return people;
    }

    private List<String> parseInterviewers(String interviewersString) {
        if (interviewersString == null || interviewersString.trim().isEmpty()) {
            return new ArrayList<>();
        }
        return Arrays.asList(interviewersString.split(",\\s*"));
    }

    private String formatTimeRange(LocalDateTime scheduledAt) {
        if (scheduledAt == null) return "시간 미정";
        
        DateTimeFormatter timeFormatter = DateTimeFormatter.ofPattern("HH:mm");
        String startTime = scheduledAt.format(timeFormatter);
        String endTime = scheduledAt.plusHours(1).format(timeFormatter); // 1시간 후를 종료 시간으로 가정
        return startTime + " - " + endTime;
    }

    private String formatSimpleTimeRange(LocalDateTime start, LocalDateTime end) {
        if (start == null) return "시간 미정";
        
        DateTimeFormatter timeFormatter = DateTimeFormatter.ofPattern("HH:mm");
        String startTime = start.format(timeFormatter);
        
        if (end != null) {
            String endTime = end.format(timeFormatter);
            return startTime + "~" + endTime;
        } else {
            return startTime + "~";
        }
    }
}