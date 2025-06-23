package com.example.skaxis.interview.controller;

import com.example.skaxis.interview.dto.*;
import com.example.skaxis.interview.dto.interviewee.IntervieweeListResponseDto;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import com.example.skaxis.interview.service.InterviewService;
import com.example.skaxis.interview.service.IntervieweeService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/interviews")
public class InterviewController {

    // 전체 면접 및 연관 데이터 삭제 (관리자 권한 필요)
    @DeleteMapping("")
    @org.springframework.security.access.prepost.PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> deleteAllInterviews(
        @RequestParam(name = "deleteFiles", defaultValue = "true") boolean deleteFiles) {
        try {
            interviewService.deleteAllInterviews(deleteFiles);
            return ResponseEntity.noContent().build(); // 204 No Content
        } catch (Exception e) {
            log.error("전체 면접 삭제 중 오류: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("message", "면접 전체 삭제 중 서버 오류가 발생했습니다."));
        }
    }

    private final InterviewService interviewService;
    private final IntervieweeService intervieweeService;

    // 기존 면접 관련 메서드들
    @GetMapping("/all")
    public ResponseEntity<?> getAllInterviews() {
        try {
            GetInterviewsResponseDto interviewList = interviewService.getAllInterviews();
            if (interviewList.getInterviewSessions() == null || interviewList.getInterviewSessions().isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("message", "No interviews found"));
            }
            return ResponseEntity.ok(interviewList);
        } catch (Exception e) {
            log.error("Error fetching interviews: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "Internal Server Error"));
        }
    }

    @PostMapping("/")
    public ResponseEntity<?> createInterview(@RequestBody CreateInterviewRequestDto createInterviewRequestDto) {
        try {
            if (createInterviewRequestDto == null || createInterviewRequestDto.getRoomNo() == null ||
                createInterviewRequestDto.getRound() <= 0 || createInterviewRequestDto.getScheduledAt() == null ||
                createInterviewRequestDto.getOrderNo() <= 0) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", "Invalid request data"));
            }
            interviewService.createInterview(createInterviewRequestDto);
            return ResponseEntity.ok().body(Map.of("message", "Interview created successfully"));
        } catch (Exception e) {
            log.error("Error creating interview: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "Internal Server Error"));
        }
    }

    @DeleteMapping("/{interviewId}")
    public ResponseEntity<?> deleteInterview(@PathVariable("interviewId") Long interviewId) {
        try {
            if (interviewId == null || interviewId <= 0) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", "Invalid interview ID"));
            }
            interviewService.deleteInterview(interviewId);
            return ResponseEntity.ok().body(Map.of("message", "Interview deleted successfully")); 
        } catch (Exception e) {
            log.error("Error deleting interview: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "Internal Server Error"));
        }
    }
    
    @PutMapping("/{interviewId}")
    public ResponseEntity<?> updateInterview(@RequestBody UpdateInterviewRequestDto updateInterviewRequestDto, @PathVariable("interviewId") Long interviewId) {
        try {
            if (interviewId == null || interviewId <= 0) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", "Invalid interview ID"));
            }
            if (updateInterviewRequestDto == null) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", "Invalid request data"));
            }
            interviewService.updateInterview(updateInterviewRequestDto, interviewId);
            return ResponseEntity.ok().body(Map.of("message", "Interview updated successfully"));
        } catch (Exception e) {
            log.error("Error updating interview: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "Internal Server Error"));
        }
    }

    @GetMapping("/{interviewId}")
    public ResponseEntity<?> getInterviewById(@PathVariable("interviewId") Long interviewId) {
        try {
            if (interviewId == null || interviewId <= 0) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message","Invalid interview ID"));
            }
            GetInterviewByIdResponseDto interview = interviewService.getInterviewById(interviewId);
            if (interview == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("message", "Interview not found"));
            }
            return ResponseEntity.ok(interview);
        } catch (Exception e) {
            log.error("Error fetching interview by ID: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "Internal Server Error"));
        }
    }
    
    // IntervieweeController에서 통합된 메서드들
    @GetMapping("/simple")
    public ResponseEntity<?> getInterviewees(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String position) {
        try {
            IntervieweeListResponseDto interviewees = intervieweeService.getInterviewees(date, status, position);
            if (interviewees == null || interviewees.getData().isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body("No interviewees found");
            }
            return ResponseEntity.ok(interviewees);
        } catch (Exception e) {
            log.error("Error fetching interviewees: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Internal Server Error");
        }
    }
    
    @GetMapping("/schedule")
    public ResponseEntity<?> getInterviewSchedule(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        try {
            SimpleInterviewScheduleResponseDto schedule = intervieweeService.getInterviewSchedule(date);
            if (schedule == null || schedule.getSchedules().isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body("No schedule found for the given date");
            }
            return ResponseEntity.ok(schedule);
        } catch (Exception e) {
            log.error("Error fetching interview schedule: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Internal Server Error");
        }
    }
    
    @GetMapping("/schedule/all")
    @Transactional(readOnly = true)
    public ResponseEntity<?> getAllInterviewSchedules(
            @RequestParam(required = false) String status) {
        try {
            SimpleInterviewScheduleResponseDto schedules = intervieweeService.getAllInterviewSchedules(status);
            if (schedules == null || schedules.getSchedules().isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body("No schedules found");
            }
            return ResponseEntity.ok(schedules);
        } catch (Exception e) {
            log.error("Error fetching all interview schedules: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Internal Server Error");
        }
    }
    
    @GetMapping("/schedule/detailed")
    public ResponseEntity<?> getDetailedInterviewSchedule(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        try {
            InterviewScheduleResponseDto detailedSchedule = intervieweeService.getDetailedInterviewSchedule(date);
            if (detailedSchedule == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body("No detailed schedule found for the given date");
            }
            return ResponseEntity.ok(detailedSchedule);
        } catch (Exception e) {
            log.error("Error fetching detailed interview schedule: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Internal Server Error");
        }
    }
}
