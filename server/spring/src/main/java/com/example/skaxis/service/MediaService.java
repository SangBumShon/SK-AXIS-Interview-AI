package com.example.skaxis.service;

import com.example.skaxis.dto.FileUploadResponseDto;
import com.example.skaxis.entity.InterviewResult;
import com.example.skaxis.repository.InterviewResultRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Service
@RequiredArgsConstructor
@Slf4j
public class MediaService {
    
    private final InterviewResultRepository interviewResultRepository;
    
    @Value("${app.upload.dir:/uploads}")
    private String uploadDir;
    
    public FileUploadResponseDto uploadMp3File(MultipartFile file, Long interviewResultId) throws IOException {
        return uploadMediaFile(file, interviewResultId, "mp3", "audio/mpeg");
    }
    
    public FileUploadResponseDto uploadMp4File(MultipartFile file, Long interviewResultId) throws IOException {
        return uploadMediaFile(file, interviewResultId, "mp4", "video/mp4");
    }
    
    public FileUploadResponseDto uploadSttFile(MultipartFile file, Long interviewResultId) throws IOException {
        return uploadMediaFile(file, interviewResultId, "stt", "text/plain");
    }
    
    private FileUploadResponseDto uploadMediaFile(MultipartFile file, Long interviewResultId, 
                                                 String fileType, String expectedContentType) throws IOException {
        // 파일 검증
        if (file.isEmpty()) {
            throw new IllegalArgumentException("파일이 비어있습니다.");
        }
        
        // 면접 결과 존재 확인
        InterviewResult interviewResult = interviewResultRepository.findById(interviewResultId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 면접 결과입니다."));
        
        // 업로드 디렉토리 생성
        Path uploadPath = Paths.get(uploadDir, fileType);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }
        
        // 파일명 생성
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String originalFilename = file.getOriginalFilename();
        String fileName = String.format("%s_%d_%s", timestamp, interviewResultId, originalFilename);
        Path filePath = uploadPath.resolve(fileName);
        
        // 파일 저장
        Files.copy(file.getInputStream(), filePath);
        
        // 데이터베이스 업데이트
        String relativePath = filePath.toString();
        switch (fileType) {
            case "mp3":
                interviewResult.setMp3Path(relativePath);
                break;
            case "mp4":
                interviewResult.setMp4Path(relativePath);
                break;
            case "stt":
                interviewResult.setSttPath(relativePath);
                break;
        }
        interviewResultRepository.save(interviewResult);
        
        return new FileUploadResponseDto(
                String.format("%s 파일이 성공적으로 업로드되었습니다.", fileType.toUpperCase()),
                relativePath,
                originalFilename,
                LocalDateTime.now()
        );
    }
}