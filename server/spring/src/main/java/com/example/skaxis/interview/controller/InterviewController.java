package com.example.skaxis.interview.controller;

import org.springframework.web.bind.annotation.RestController;

import com.example.skaxis.interview.dto.GetInterviewsResponseDto;
import com.example.skaxis.interview.dto.UpdateInterviewRequestDto;
import com.example.skaxis.interview.service.InterviewService;
import com.example.skaxis.interview.dto.CreateInterviewRequestDto;
import com.example.skaxis.interview.dto.GetInterviewByIdResponseDto;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.PathVariable;



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

    @GetMapping("/")
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
    public ResponseEntity<?> deleteInterview(@PathVariable("interview_id") Long interviewId) {
        try {
            if (interviewId == null || interviewId <= 0) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", "Invalid interview ID"));
            }
            interviewService.deleteInterview(interviewId);
            return ResponseEntity.ok().body(Map.of("messgae", "Interview deleted successfully")); 
        } catch (Exception e) {
            log.error("Error deleting interview: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "Internal Server Error"));
        }
    }
    
    @PutMapping("/{interviewId}")
    public ResponseEntity<?> updateInterview(@RequestBody UpdateInterviewRequestDto updateInterviewRequestDto, @PathVariable("interview_id") Long interviewId) {
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
    public ResponseEntity<?> getInterviewById(@PathVariable("interview_id") Long interviewId) {
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
}
