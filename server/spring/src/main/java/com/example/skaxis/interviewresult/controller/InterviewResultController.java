package com.example.skaxis.interviewresult.controller;

import com.example.skaxis.interviewresult.dto.CommentUpdateRequest;
import com.example.skaxis.interviewresult.model.InterviewResult;
import com.example.skaxis.interviewresult.service.InterviewResultService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/v1")
public class InterviewResultController {

    private final InterviewResultService interviewResultService;

    @Autowired
    public InterviewResultController(InterviewResultService interviewResultService) {
        this.interviewResultService = interviewResultService;
    }

    @GetMapping("/interview/{interview_id}/{interviewee_id}/download")
    public ResponseEntity<Resource> downloadFile(
            @PathVariable("interview_id") Long interviewId,
            @PathVariable("interviewee_id") Long intervieweeId,
            @RequestParam("type") String fileType) {
        
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

    @PutMapping("/interview/{interview_id}/{interviewee_id}/comment")
    public ResponseEntity<Map<String, String>> updateComment(
            @PathVariable("interview_id") Long interviewId,
            @PathVariable("interviewee_id") Long intervieweeId,
            @RequestBody CommentUpdateRequest request) {
        
        InterviewResult result = interviewResultService.updateComment(interviewId, intervieweeId, request);
        
        Map<String, String> response = new HashMap<>();
        response.put("result", "updated");
        
        return ResponseEntity.ok(response);
    }
}
