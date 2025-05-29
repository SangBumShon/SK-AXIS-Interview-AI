package com.example.skaxis.service;

import com.example.skaxis.dto.ExcelParseResponseDto;
import com.example.skaxis.dto.FileUploadResponseDto;
import com.example.skaxis.entity.Interviewee;
import com.example.skaxis.repository.IntervieweeRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class IntervieweeService {
    
    private final IntervieweeRepository intervieweeRepository;
    
    @Value("${app.upload.dir:/uploads/interviewees}")
    private String uploadDir;
    
//    public IntervieweeListResponseDto getInterviewees(LocalDate date, String status, String position) {
//        Interviewee.InterviewStatus interviewStatus = null;
//        if (status != null) {
//            try {
//                interviewStatus = Interviewee.InterviewStatus.valueOf(status);
//            } catch (IllegalArgumentException e) {
//                log.warn("Invalid status: {}", status);
//            }
//        }
//
//        List<Interviewee> interviewees = intervieweeRepository.findByFilters(date, interviewStatus, position);
//        List<IntervieweeResponseDto> responseList = IntervieweeResponseDto.fromList(interviewees);
//
//        return new IntervieweeListResponseDto(responseList, responseList.size());
//    }
    
    public FileUploadResponseDto uploadExcelFile(MultipartFile file) throws IOException {
        // 파일 검증
        if (file.isEmpty()) {
            throw new IllegalArgumentException("파일이 비어있습니다.");
        }
        
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || (!originalFilename.endsWith(".xlsx") && !originalFilename.endsWith(".xls"))) {
            throw new IllegalArgumentException("지원되지 않는 파일 형식입니다. Excel 파일(.xlsx, .xls)만 업로드 가능합니다.");
        }
        
        // 업로드 디렉토리 생성
        Path uploadPath = Paths.get(uploadDir);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }
        
        // 파일명 생성 (중복 방지를 위해 타임스탬프 추가)
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String fileName = timestamp + "_" + originalFilename;
        Path filePath = uploadPath.resolve(fileName);
        
        // 파일 저장
        Files.copy(file.getInputStream(), filePath);
        
        return new FileUploadResponseDto(
            "파일이 성공적으로 업로드되었습니다.",
            filePath.toString(),
            originalFilename,
            LocalDateTime.now()
        );
    }
    
    public ExcelParseResponseDto parseExcelFile(String filePath) {
        List<ExcelParseResponseDto.ParseError> errors = new ArrayList<>();
        int processedCount = 0;
        int successCount = 0;
        
        try (FileInputStream fis = new FileInputStream(new File(filePath));
             Workbook workbook = new XSSFWorkbook(fis)) {
            
            Sheet sheet = workbook.getSheetAt(0);
            
            // 헤더 행 건너뛰기 (첫 번째 행은 헤더로 가정)
            for (int i = 1; i <= sheet.getLastRowNum(); i++) {
                Row row = sheet.getRow(i);
                if (row == null) continue;
                
                processedCount++;
                
                try {
                    Interviewee interviewee = parseRowToInterviewee(row, i + 1);
                    
                    // 중복 체크
                    if (intervieweeRepository.existsByApplicantId(interviewee.getApplicantId())) {
                        errors.add(new ExcelParseResponseDto.ParseError(i + 1, "이미 존재하는 지원식별ID입니다: " + interviewee.getApplicantId()));
                        continue;
                    }
                    
                    intervieweeRepository.save(interviewee);
                    successCount++;
                    
                } catch (Exception e) {
                    errors.add(new ExcelParseResponseDto.ParseError(i + 1, e.getMessage()));
                }
            }
            
        } catch (IOException e) {
            throw new RuntimeException("Excel 파일을 읽는 중 오류가 발생했습니다: " + e.getMessage());
        }
        
        return new ExcelParseResponseDto(
            "Excel 파일이 성공적으로 파싱되어 데이터베이스에 저장되었습니다.",
            processedCount,
            successCount,
            errors.size(),
            errors
        );
    }
    
    private Interviewee parseRowToInterviewee(Row row, int rowNumber) {
        try {
            Interviewee interviewee = new Interviewee();
            
            // 컬럼 순서: 지원자명, 지원식별ID, 직무, 면접날짜, 면접상태, 점수, 면접관, 면접장소
            interviewee.setApplicantName(getCellValueAsString(row.getCell(0)));
            interviewee.setApplicantId(getCellValueAsString(row.getCell(1)));
            interviewee.setPosition(getCellValueAsString(row.getCell(2)));
            
            // 면접 날짜 파싱
            Cell dateCell = row.getCell(3);
            if (dateCell != null) {
                if (dateCell.getCellType() == CellType.NUMERIC && DateUtil.isCellDateFormatted(dateCell)) {
                    interviewee.setInterviewDate(dateCell.getLocalDateTimeCellValue().toLocalDate());
                } else {
                    String dateStr = getCellValueAsString(dateCell);
                    if (!dateStr.isEmpty()) {
                        interviewee.setInterviewDate(LocalDate.parse(dateStr));
                    }
                }
            }
            
            // 면접 상태
            String statusStr = getCellValueAsString(row.getCell(4));
            if (!statusStr.isEmpty()) {
                try {
                    interviewee.setInterviewStatus(Interviewee.InterviewStatus.valueOf(statusStr));
                } catch (IllegalArgumentException e) {
                    throw new IllegalArgumentException("잘못된 면접 상태: " + statusStr);
                }
            }
            
            // 점수
            Cell scoreCell = row.getCell(5);
            if (scoreCell != null && scoreCell.getCellType() == CellType.NUMERIC) {
                interviewee.setScore((int) scoreCell.getNumericCellValue());
            }
            
            interviewee.setInterviewer(getCellValueAsString(row.getCell(6)));
            interviewee.setInterviewLocation(getCellValueAsString(row.getCell(7)));
            
            // 필수 필드 검증
            if (interviewee.getApplicantName() == null || interviewee.getApplicantName().trim().isEmpty()) {
                throw new IllegalArgumentException("지원자명은 필수입니다.");
            }
            if (interviewee.getApplicantId() == null || interviewee.getApplicantId().trim().isEmpty()) {
                throw new IllegalArgumentException("지원식별ID는 필수입니다.");
            }
            if (interviewee.getPosition() == null || interviewee.getPosition().trim().isEmpty()) {
                throw new IllegalArgumentException("직무는 필수입니다.");
            }
            
            return interviewee;
            
        } catch (Exception e) {
            throw new RuntimeException("행 " + rowNumber + " 파싱 오류: " + e.getMessage());
        }
    }
    
    private String getCellValueAsString(Cell cell) {
        if (cell == null) return "";
        
        switch (cell.getCellType()) {
            case STRING:
                return cell.getStringCellValue().trim();
            case NUMERIC:
                if (DateUtil.isCellDateFormatted(cell)) {
                    return cell.getLocalDateTimeCellValue().toLocalDate().toString();
                } else {
                    return String.valueOf((long) cell.getNumericCellValue());
                }
            case BOOLEAN:
                return String.valueOf(cell.getBooleanCellValue());
            case FORMULA:
                return cell.getCellFormula();
            default:
                return "";
        }
    }
}