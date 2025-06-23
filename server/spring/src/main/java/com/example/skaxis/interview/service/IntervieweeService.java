package com.example.skaxis.interview.service;

import com.example.skaxis.interview.dto.InterviewScheduleItemDto;
import com.example.skaxis.interview.dto.InterviewScheduleResponseDto;
import com.example.skaxis.interview.dto.SimpleInterviewScheduleResponseDto;
import com.example.skaxis.interview.dto.interviewee.IntervieweeListResponseDto;
import com.example.skaxis.interview.dto.interviewee.IntervieweeResponseDto;
import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interview.model.Interviewee;
import com.example.skaxis.interview.repository.IntervieweeRepository;
import com.example.skaxis.interview.model.InterviewInterviewee;
import com.example.skaxis.interview.repository.InterviewIntervieweeRepository;
import com.example.skaxis.interview.dto.common.PersonDto;
import com.example.skaxis.interview.dto.common.RoomDto;
import com.example.skaxis.interview.dto.common.TimeSlotDto;
import com.example.skaxis.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

<<<<<<< HEAD
import static com.example.skaxis.interview.model.Interview.InterviewStatus.UNDECIDED;

=======
>>>>>>> origin/front-ai-face
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
<<<<<<< HEAD
                .orElseThrow(() -> new RuntimeException("Interviewee not found with ID: " + id));
=======
            .orElseThrow(() -> new RuntimeException("Interviewee not found with ID: " + id));
>>>>>>> origin/front-ai-face
    }

    public Interviewee findByName(String name) {
        return intervieweeRepository.findByName(name)
<<<<<<< HEAD
                .orElseThrow(() -> new RuntimeException("Interviewee not found with name: " + name));
=======
            .orElseThrow(() -> new RuntimeException("Interviewee not found with name: " + name));
>>>>>>> origin/front-ai-face
    }

    public Interviewee saveInterviewee(Interviewee interviewee) {
        return intervieweeRepository.save(interviewee);
    }

    public Interviewee createInterviewee(String name, String applicantCode) {
        // applicantCode 필드 추가
        Interviewee interviewee = Interviewee.builder()
                .name(name)
<<<<<<< HEAD
//                .applicantCode(applicantCode)
=======
                .applicantCode(applicantCode)
>>>>>>> origin/front-ai-face
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
<<<<<<< HEAD

=======
            
>>>>>>> origin/front-ai-face
            // 해당 날짜의 면접에 참여하는 면접 대상자들을 Interview를 통해 조회
            List<Interviewee> interviewees = new ArrayList<>();
            for (Interview interview : interviews) {
                List<InterviewInterviewee> interviewInterviewees =
<<<<<<< HEAD
                        interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());

                for (InterviewInterviewee ii : interviewInterviewees) {
                    Interviewee interviewee = intervieweeRepository.findById(ii.getIntervieweeId())
                            .orElse(null);
=======
                    interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());

                for (InterviewInterviewee ii : interviewInterviewees) {
                    Interviewee interviewee = intervieweeRepository.findById(ii.getIntervieweeId())
                        .orElse(null);
>>>>>>> origin/front-ai-face
                    if (interviewee != null && !interviewees.contains(interviewee)) {
                        interviewees.add(interviewee);
                    }
                }
            }
<<<<<<< HEAD

=======
            
>>>>>>> origin/front-ai-face
            // 데이터베이스에서 해당 날짜의 면접실 정보 동적 생성
            // InterviewService를 통해 조회
            List<String> roomIds = interviewService.findDistinctRoomIdsByDate(date);
            List<RoomDto> rooms = roomIds.stream()
<<<<<<< HEAD
                    .map(roomId -> new RoomDto(roomId, "면접실 " + roomId))
                    .collect(Collectors.toList());

=======
                .map(roomId -> new RoomDto(roomId, "면접실 " + roomId))
                .collect(Collectors.toList());
            
>>>>>>> origin/front-ai-face
            // 면접실이 없는 경우 기본 면접실 제공
            if (rooms.isEmpty()) {
                List<String> allRoomIds = interviewService.findDistinctRoomIds();
                rooms = allRoomIds.stream()
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/front-ai-face
        }
    }

    public SimpleInterviewScheduleResponseDto getSimpleInterviewScheduleByDate(LocalDate date) {
        try {
            // InterviewService를 통해 해당 날짜의 면접 일정 조회
            List<Interview> interviews = interviewService.findInterviewsByDate(date);
<<<<<<< HEAD

            List<InterviewScheduleItemDto> schedules = new ArrayList<>();

            for (Interview interview : interviews) {
                // 면접관 이름들 파싱 (Interview 엔티티의 interviewers 필드에서)
                List<String> interviewerNames = parseInterviewers(interview.getInterviewers());

                // 해당 면접의 지원자들 조회
                List<InterviewInterviewee> interviewInterviewees =
                        interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());
=======
            
            List<InterviewScheduleItemDto> schedules = new ArrayList<>();
            
            for (Interview interview : interviews) {
                // 면접관 이름들 파싱 (Interview 엔티티의 interviewers 필드에서)
                List<String> interviewerNames = parseInterviewers(interview.getInterviewers());
                
                // 해당 면접의 지원자들 조회
                List<InterviewInterviewee> interviewInterviewees =
                    interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());
>>>>>>> origin/front-ai-face
                String status = interview.getStatus().getDescription();

                List<String> interviewees = new ArrayList<>();
                for (InterviewInterviewee ii : interviewInterviewees) {
                    Interviewee interviewee = intervieweeRepository.findById(ii.getIntervieweeId())
<<<<<<< HEAD
                            .orElse(null);
=======
                        .orElse(null);
>>>>>>> origin/front-ai-face
                    if (interviewee != null && interviewee.getName() != null) {
                        interviewees.add(interviewee.getName());
                    }
                }
<<<<<<< HEAD

                // 시간 범위 포맷팅
                String timeRange = formatSimpleTimeRange(interview.getScheduledAt(), interview.getScheduledEndAt());

=======
                
                // 시간 범위 포맷팅
                String timeRange = formatSimpleTimeRange(interview.getScheduledAt(), interview.getScheduledEndAt());
                
>>>>>>> origin/front-ai-face
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
<<<<<<< HEAD

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
=======
            
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
>>>>>>> origin/front-ai-face
        }
    }

    private List<TimeSlotDto> createTimeSlots(List<Interview> interviews, List<Interviewee> interviewees) {
        Map<String, TimeSlotDto> timeSlotMap = new HashMap<>();
<<<<<<< HEAD

=======
        
>>>>>>> origin/front-ai-face
        // 면접별로 시간대 생성
        for (Interview interview : interviews) {
            String timeRange = formatTimeRange(interview.getScheduledAt());
            String timeSlotId = "ts_" + interview.getInterviewId();
<<<<<<< HEAD

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

=======
            
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
        
>>>>>>> origin/front-ai-face
        return new ArrayList<>(timeSlotMap.values());
    }

    private List<PersonDto> createPeople(List<Interview> interviews, List<Interviewee> interviewees) {
        List<PersonDto> people = new ArrayList<>();
<<<<<<< HEAD

        // 지원자 정보 추가
        for (Interviewee interviewee : interviewees) {
            people.add(new PersonDto(
                    "c" + interviewee.getIntervieweeId(),
                    interviewee.getName() != null ? interviewee.getName() : "이름 없음",
                    "candidate"
            ));
        }

=======
        
        // 지원자 정보 추가
        for (Interviewee interviewee : interviewees) {
            people.add(new PersonDto(
                "c" + interviewee.getIntervieweeId(),
                interviewee.getName() != null ? interviewee.getName() : "이름 없음",
                "candidate"
            ));
        }
        
>>>>>>> origin/front-ai-face
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
<<<<<<< HEAD

=======
        
>>>>>>> origin/front-ai-face
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
<<<<<<< HEAD

=======
        
>>>>>>> origin/front-ai-face
        DateTimeFormatter timeFormatter = DateTimeFormatter.ofPattern("HH:mm");
        String startTime = scheduledAt.format(timeFormatter);
        String endTime = scheduledAt.plusHours(1).format(timeFormatter); // 1시간 후를 종료 시간으로 가정
        return startTime + " - " + endTime;
    }

    private String formatSimpleTimeRange(LocalDateTime start, LocalDateTime end) {
        if (start == null) return "시간 미정";
<<<<<<< HEAD

        DateTimeFormatter timeFormatter = DateTimeFormatter.ofPattern("HH:mm");
        String startTime = start.format(timeFormatter);

=======
        
        DateTimeFormatter timeFormatter = DateTimeFormatter.ofPattern("HH:mm");
        String startTime = start.format(timeFormatter);
        
>>>>>>> origin/front-ai-face
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
<<<<<<< HEAD


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
=======
            
            
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
>>>>>>> origin/front-ai-face
                    if (interviewee != null && interviewee.getName() != null) {
                        interviewees.add(interviewee.getName());
                    }
                }
<<<<<<< HEAD

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
=======
                
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
>>>>>>> origin/front-ai-face
        }
    }

    public IntervieweeListResponseDto getInterviewees(LocalDate date, String status, String position) {
        try {
<<<<<<< HEAD
            List<InterviewInterviewee> interviewInterviewees;

            if (date == null) {
                // 날짜가 지정되지 않은 경우, 모든 면접-면접자 정보를 가져옵니다.
                // LazyInitializationException을 해결하기 위해 JOIN FETCH를 사용합니다.
                interviewInterviewees = interviewIntervieweeRepository.findAllWithInterviewAndInterviewee();
            } else {
                // 날짜가 지정된 경우, 해당 날짜의 면접 정보를 기반으로 필터링합니다.
                LocalDateTime startOfDay = date.atStartOfDay();
                List<Interview> interviews = interviewService.findInterviewsByDate(date);
                List<Long> interviewIds = interviews.stream()
                        .filter(interview -> status == null || status.isEmpty() || interview.getStatus().name().equalsIgnoreCase(status))
                        .map(Interview::getInterviewId)
                        .collect(Collectors.toList());
                // TODO: N+1 문제가 발생할 수 있으므로 fetch join을 사용하는 것이 좋습니다.
                interviewInterviewees = interviewIntervieweeRepository.findByInterviewIdIn(interviewIds);
            }

            // 필터링된 InterviewInterviewee 목록을 DTO로 변환
            List<IntervieweeResponseDto> dtos = IntervieweeResponseDto.fromList(interviewInterviewees);
        
            return new IntervieweeListResponseDto(dtos, dtos.size());
        } catch (Exception e) {
            log.error("Error fetching interviewees: {}", e.getMessage());
            // 예외 상황에 맞는 적절한 응답을 반환하거나, 더 구체적인 예외 처리를 수행할 수 있습니다.
            return new IntervieweeListResponseDto(Collections.emptyList(), 0); // 또는 예외를 던짐
=======
            List<Interviewee> interviewees;

            if (date != null) {
                // 특정 날짜의 면접에 참여하는 면접자들 조회
                List<Interview> interviews = interviewService.findInterviewsByDate(date);
                Set<Long> intervieweeIds = new HashSet<>();

                for (Interview interview : interviews) {
                    // 상태 필터링
                    if (status != null && !status.isEmpty() &&
                        !interview.getStatus().getDescription().equalsIgnoreCase(status)) {
                        continue;
                    }

                    List<InterviewInterviewee> interviewInterviewees =
                        interviewIntervieweeRepository.findByInterviewId(interview.getInterviewId());

                    for (InterviewInterviewee ii : interviewInterviewees) {
                        intervieweeIds.add(ii.getIntervieweeId());
                    }
                }

                interviewees = intervieweeIds.stream()
                    .map(id -> intervieweeRepository.findById(id).orElse(null))
                    .filter(Objects::nonNull)
                    .collect(Collectors.toList());
            } else {
                // 전체 면접자 조회
                interviewees = intervieweeRepository.findAll();
            }

            List<IntervieweeResponseDto> responseList = interviewees.stream()
                .map(this::convertToResponseDto)
                .collect(Collectors.toList());

            return new IntervieweeListResponseDto(responseList, responseList.size());

        } catch (Exception e) {
            log.error("면접자 목록 조회 중 오류 발생: {}", e.getMessage(), e);
            return new IntervieweeListResponseDto(new ArrayList<>(), 0);
>>>>>>> origin/front-ai-face
        }
    }

    public SimpleInterviewScheduleResponseDto getInterviewSchedule(LocalDate date) {
        return getSimpleInterviewScheduleByDate(date);
    }

    public SimpleInterviewScheduleResponseDto getAllInterviewSchedules(String status) {
        return getAllSimpleInterviewSchedules(status);
    }

    public InterviewScheduleResponseDto getDetailedInterviewSchedule(LocalDate date) {
        return getInterviewScheduleByDate(date);
    }

<<<<<<< HEAD
    // 이 메서드는 더 이상 사용되지 않으므로 삭제하거나 주석 처리할 수 있습니다.
    /*
    private IntervieweeResponseDto convertToResponseDto(Interviewee interviewee) {
        // 해당 면접자의 최근 면접 정보 조회
        List<InterviewInterviewee> interviewInterviewees =
                interviewIntervieweeRepository.findByIntervieweeId(interviewee.getIntervieweeId());
=======
    private IntervieweeResponseDto convertToResponseDto(Interviewee interviewee) {
        // 해당 면접자의 최근 면접 정보 조회
        List<InterviewInterviewee> interviewInterviewees =
            interviewIntervieweeRepository.findByIntervieweeId(interviewee.getIntervieweeId());
>>>>>>> origin/front-ai-face

        Interview recentInterview = null;
        if (!interviewInterviewees.isEmpty()) {
            Long recentInterviewId = interviewInterviewees.get(0).getInterviewId();
            recentInterview = interviewService.findById(recentInterviewId);
        }

        return IntervieweeResponseDto.builder()
<<<<<<< HEAD
                .intervieweeId(interviewee.getIntervieweeId())
                .name(interviewee.getName())
                .scheduledAt(recentInterview != null ? recentInterview.getScheduledAt() : null)
                .status(recentInterview != null ? recentInterview.getStatus() : UNDECIDED)
                .score(interviewee.getScore())
                .interviewers(recentInterview != null ? recentInterview.getInterviewers() : "미정")
                .roomNo(recentInterview != null ? recentInterview.getRoomNo() : "미정")
                .createdAt(interviewee.getCreatedAt())
                .build();
    }
    */
=======
            .intervieweeId(interviewee.getIntervieweeId())
            .applicantName(interviewee.getName())
            .applicantId(interviewee.getApplicantCode())
//            .position("개발자") // 기본값, 추후 엔티티에 필드 추가 필요
            .interviewDate(recentInterview != null ? recentInterview.getScheduledAt().toLocalDate() : null)
            .interviewStatus(recentInterview != null ? recentInterview.getStatus().getDescription() : "미정")
            .score(interviewee.getScore())
            .interviewer(recentInterview != null ? recentInterview.getInterviewers() : "미정")
            .interviewLocation(recentInterview != null ? recentInterview.getRoomNo() : "미정")
            .createdAt(interviewee.getCreatedAt())
            .build();
    }
>>>>>>> origin/front-ai-face

}
