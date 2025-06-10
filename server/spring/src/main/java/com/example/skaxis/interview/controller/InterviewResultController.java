package com.example.skaxis.interview.controller;

import com.example.skaxis.interview.dto.result.CommentUpdateRequest;
import com.example.skaxis.interview.service.InterviewResultService;

import lombok.RequiredArgsConstructor;

import java.util.Map;

import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/results")
@RequiredArgsConstructor
public class InterviewResultController {
    private final InterviewResultService interviewResultService;

    @GetMapping("/{interview_id}/{interviewee_id}/download")
    public ResponseEntity<?> downloadFile(
            @PathVariable("interview_id") Long interviewId,
            @PathVariable("interviewee_id") Long intervieweeId,
            @RequestParam("type") String fileType) {
        
        if (interviewId == null || interviewId <= 0 ||
            intervieweeId == null || intervieweeId <= 0 || 
            fileType == null || fileType.isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", "Invalid request data"));
        }
        
        Resource file = interviewResultService.downloadFile(interviewId, intervieweeId, fileType);
        
        String contentType;
        String filename;
        
        switch (fileType.toLowerCase()) {
            case "pdf":
                contentType = MediaType.APPLICATION_PDF_VALUE;
                filename = "interview_" + interviewId + "_" + intervieweeId + ".pdf";
                break;
            case "excel":
                contentType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
                filename = "interview_" + interviewId + "_" + intervieweeId + ".xlsx";
                break;
            case "txt":
                contentType = MediaType.TEXT_PLAIN_VALUE;
                filename = "interview_" + interviewId + "_" + intervieweeId + ".txt";
                break;
            default:
                contentType = MediaType.APPLICATION_OCTET_STREAM_VALUE;
                filename = "interview_" + interviewId + "_" + intervieweeId;
        }
        
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .body(file);
    }

    @PutMapping("/{interview_id}/{interviewee_id}/comment")
    public ResponseEntity<?> updateComment(
            @PathVariable("interview_id") Long interviewId,
            @PathVariable("interviewee_id") Long intervieweeId,
            @RequestBody CommentUpdateRequest request) {

        if (interviewId == null || interviewId <= 0 ||
            intervieweeId == null || intervieweeId <= 0 ||
            request == null || request.getComment() == null || request.getComment().isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", "Invalid request data"));
        }
        
        interviewResultService.updateComment(interviewId, intervieweeId, request);
  
        return ResponseEntity.ok().body(Map.of("message", "Comment updated successfully"));
    }
}
