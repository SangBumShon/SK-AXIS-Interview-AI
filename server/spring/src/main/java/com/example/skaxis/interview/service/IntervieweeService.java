package com.example.skaxis.interview.service;

import com.example.skaxis.interview.dto.InterviewScheduleItemDto;
import com.example.skaxis.interview.dto.InterviewScheduleResponseDto;
import com.example.skaxis.interview.dto.SimpleInterviewScheduleResponseDto;
import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interview.model.Interviewee;
import com.example.skaxis.interview.repository.IntervieweeRepository;
import com.example.skaxis.interview.model.InterviewInterviewee;
import com.example.skaxis.interview.repository.InterviewIntervieweeRepository;
import com.example.skaxis.interview.dto.common.PersonDto;
import com.example.skaxis.interview.dto.common.RoomDto;
import com.example.skaxis.interview.dto.common.TimeSlotDto;
// import com.example.skaxis.interview.repository.InterviewRepository; // 이 라인 제거
import com.example.skaxis.user.repository.UserRepository;
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
    private final InterviewService interviewService; // 의존성 주입으로 중복 제거
    private final InterviewIntervieweeRepository interviewIntervieweeRepository;

    // 기본 CRUD 작업 (중복 제거된 버전)
    public List<Interviewee> getAllInterviewees() {
        return intervieweeRepository.findAll();
    }

    public Interviewee findById(Long id) {
        return intervieweeRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Interviewee not found with ID: " + id));
    }

    public Interviewee findByName(String name) {
        return intervieweeRepository.findByName(name)
            .orElseThrow(() -> new RuntimeException("Interviewee not found with name: " + name));
    }

    public Interviewee saveInterviewee(Interviewee interviewee) {
        return intervieweeRepository.save(interviewee);
    }

    public Interviewee createInterviewee(String name, String applicantCode) {
        // applicantCode 필드 추가
        Interviewee interviewee = Interviewee.builder()
                .name(name)
                .applicantCode(applicantCode)
                .createdAt(LocalDateTime.now())
                .build();
        return intervieweeRepository.save(interviewee);
    }

    public void deleteInterviewee(Long id) {
        if (!intervieweeRepository.existsById(id)) {
            throw new RuntimeException("Interviewee not found with ID: " + id);
        }
        intervieweeRepository.deleteById(id);
    }

    // 면접 일정 관련 기능들 (InterviewService와 협력)
    public InterviewScheduleResponseDto getInterviewScheduleByDate(LocalDate date) {
        try {
            // InterviewService를 통해 해당 날짜의 면접 일정 조회
            List<Interview> interviews = interviewService.findInterviewsByDate(date);
            
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
            // InterviewService를 통해 조회
            List<String> roomIds = interviewService.findDistinctRoomIdsByDate(date);
            List<RoomDto> rooms = roomIds.stream()
                .map(roomId -> new RoomDto(roomId, "면접실 " + roomId))
                .collect(Collectors.toList());
            
            // 면접실이 없는 경우 기본 면접실 제공
            if (rooms.isEmpty()) {
                List<String> allRoomIds = interviewService.findDistinctRoomIds();
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
            // InterviewService를 통해 해당 날짜의 면접 일정 조회
            List<Interview> interviews = interviewService.findInterviewsByDate(date);
            
            List<InterviewScheduleItemDto> schedules = new ArrayList<>();
            
            for (Interview interview : interviews) {
                // 면접관 이름들 파싱 (Interview 엔티티의 interviewers 필드에서)
                List<String> interviewerNames = parseInterviewers(interview.getInterviewers());
                
                // 해당 면접의 지원자들 조회
                List<InterviewInterviewee> interviewInterviewees =
                    interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());
                String status = interview.getStatus().getDescription();

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
                        .roomName(interview.getRoomNo())
                        .status(status)
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
                interview.getRoomNo(),
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

    public SimpleInterviewScheduleResponseDto getAllSimpleInterviewSchedules(String status) {
        try {
            // 모든 면접 일정 조회 (상태 필터링 포함)
            List<Interview> interviews;
            if (status != null && !status.trim().isEmpty()) {
                interviews = interviewService.findByStatusOrderByScheduledAt(Interview.InterviewStatus.valueOf(status));
            } else {
                interviews = interviewService.findAllOrderByScheduledAt();
            }
            
            
            List<InterviewScheduleItemDto> schedules = new ArrayList<>();
            
            for (Interview interview : interviews) {
                // 면접관 이름들 파싱
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
                
                // 날짜 추출 (LocalDate)
                LocalDate interviewDate = interview.getScheduledAt().toLocalDate();
                
                InterviewScheduleItemDto scheduleItem = InterviewScheduleItemDto.builder()
                    .interviewDate(interviewDate)
                    .timeRange(timeRange)
                    .roomName(interview.getRoomNo())
                    .interviewers(interviewerNames)
                    .interviewees(interviewees)
                    .status(interview.getStatus().getDescription())
                    .build();
                
                schedules.add(scheduleItem);
            }
            
            return SimpleInterviewScheduleResponseDto.builder()
                .schedules(schedules)
                .message("전체 면접 일정을 성공적으로 조회했습니다.")
                .build();
                
        } catch (Exception e) {
            log.error("전체 면접 일정 조회 중 오류 발생: {}", e.getMessage(), e);
            return SimpleInterviewScheduleResponseDto.builder()
                .schedules(new ArrayList<>())
                .message("면접 일정 조회 중 오류가 발생했습니다: " + e.getMessage())
                .build();
        }
    }

}
