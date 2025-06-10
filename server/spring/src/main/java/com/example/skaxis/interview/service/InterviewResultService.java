package com.example.skaxis.interview.service;

import com.example.skaxis.interview.dto.result.CommentUpdateRequest;
import com.example.skaxis.interview.model.InterviewResult;
import com.example.skaxis.interview.repository.InterviewResultRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.net.MalformedURLException;
import java.nio.file.Path;
import java.nio.file.Paths;

@Service
@RequiredArgsConstructor
public class InterviewResultService {
    private final InterviewResultRepository interviewResultRepository;
    
    @Value("${file.upload.path:./uploads}")
    private String fileUploadPath;

    public InterviewResult getInterviewResult(Long interviewId, Long intervieweeId) {
        return interviewResultRepository.findByInterviewIdAndIntervieweeId(interviewId, intervieweeId)
                .orElseThrow(() -> new EntityNotFoundException(
                        "면접 결과를 찾을 수 없습니다. 면접 ID: " + interviewId + ", 지원자 ID: " + intervieweeId));
    }

    @Transactional
    public InterviewResult updateComment(Long interviewId, Long intervieweeId, CommentUpdateRequest request) {
        InterviewResult result = getInterviewResult(interviewId, intervieweeId);
        result.setComment(request.getComment());
        return interviewResultRepository.save(result);
    }

    public Resource downloadFile(Long interviewId, Long intervieweeId, String fileType) {
        InterviewResult result = getInterviewResult(interviewId, intervieweeId);
        
        String filePath;
        switch (fileType.toLowerCase()) {
            case "pdf":
                filePath = result.getPdfPath();
                break;
            case "excel":
                filePath = result.getExcelPath();
                break;
            case "txt":
                filePath = result.getSttPath();
                break;
            default:
                throw new IllegalArgumentException("지원하지 않는 파일 형식입니다: " + fileType);
        }
        
        if (filePath == null || filePath.isEmpty()) {
            throw new EntityNotFoundException("요청한 파일이 존재하지 않습니다.");
        }
        
        try {
            Path path = Paths.get(fileUploadPath).resolve(filePath).normalize();
            Resource resource = new UrlResource(path.toUri());
            
            if (resource.exists()) {
                return resource;
            } else {
                throw new EntityNotFoundException("파일을 찾을 수 없습니다: " + filePath);
            }
        } catch (MalformedURLException e) {
            throw new RuntimeException("파일 경로가 잘못되었습니다: " + filePath, e);
        }
    }
}
