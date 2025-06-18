package com.example.skaxis.interview.service;

import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interview.repository.InterviewRepository;
import com.example.skaxis.interview.model.Interviewee;
import com.example.skaxis.interview.repository.IntervieweeRepository;
import com.example.skaxis.interview.model.InterviewInterviewee;
import com.example.skaxis.interview.repository.InterviewIntervieweeRepository;
import com.example.skaxis.interview.dto.common.FileUploadResponseDto;
import com.example.skaxis.interview.dto.common.ExcelParseResponseDto;
import com.example.skaxis.interview.dto.common.InterviewScheduleExcelDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class MediaService {

    private final InterviewIntervieweeRepository interviewIntervieweeRepository;
    private final InterviewRepository interviewRepository;
    private final IntervieweeRepository intervieweeRepository;

    @Value("${app.upload.dir:/uploads}")
    private String uploadDir;

    public FileUploadResponseDto uploadSttFile(MultipartFile file, Long interviewResultId) throws IOException {
        return uploadMediaFile(file, interviewResultId, "stt", "text/plain");
    }

    private FileUploadResponseDto uploadMediaFile(MultipartFile file, Long interviewResultId,
                                                  String fileType, String expectedContentType) throws IOException {
        // 파일 검증
        if (file.isEmpty()) {
            throw new IllegalArgumentException("파일이 비어있습니다.");
        }

        InterviewInterviewee interviewInterviewee = interviewIntervieweeRepository.findById(interviewResultId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 면접 결과입니다."));

        Path uploadPath = Paths.get(uploadDir, fileType);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String originalFilename = file.getOriginalFilename();
        String fileName = String.format("%s_%d_%s", timestamp, interviewResultId, originalFilename);
        Path filePath = uploadPath.resolve(fileName);

        Files.copy(file.getInputStream(), filePath);

        String relativePath = filePath.toString();
        interviewInterviewee.setSttPath(relativePath);
        interviewIntervieweeRepository.save(interviewInterviewee);

        return FileUploadResponseDto.builder()
                .message(String.format("%s 파일이 성공적으로 업로드되었습니다.", fileType.toUpperCase()))
                .filePath(relativePath)
                .fileName(originalFilename)
                .uploadTime(LocalDateTime.now())
                .build();
    }

    // 통합된 면접 일정 엑셀 업로드 및 처리
    public FileUploadResponseDto uploadAndProcessInterviewScheduleExcel(MultipartFile file) throws IOException {
        // 1. 파일 업로드
        FileUploadResponseDto uploadResult = uploadInterviewScheduleExcel(file);
    
        // 2. 파일 파싱 및 데이터 저장
        ExcelParseResponseDto parseResult = parseAndSaveInterviewSchedule(uploadResult.getFilePath());
    
        // 3. 결과 통합
        return FileUploadResponseDto.builder()
                .message(String.format("엑셀 업로드 및 처리 완료: %s", parseResult.getMessage()))
                .filePath(uploadResult.getFilePath())
                .fileName(uploadResult.getFileName())
                .uploadTime(uploadResult.getUploadTime())
                .successCount(parseResult.getSuccessCount())
                .errorCount(parseResult.getErrorCount())
                .errors(parseResult.getErrors().stream()
                        .map(error -> String.format("행 %d: %s", error.getRow(), error.getErrorMessage()))
                        .collect(Collectors.toList()))
                .build();
    }

    private FileUploadResponseDto uploadInterviewScheduleExcel(MultipartFile file) throws IOException {
        // 파일 검증
        if (file.isEmpty()) {
            throw new IllegalArgumentException("파일이 비어있습니다.");
        }

        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null ||
            (!originalFilename.toLowerCase().endsWith(".xlsx") &&
             !originalFilename.toLowerCase().endsWith(".xls"))) {
            throw new IllegalArgumentException("Excel 파일만 업로드 가능합니다.");
        }

        // 업로드 디렉토리 생성
        Path uploadPath = Paths.get(uploadDir, "interview-schedule");
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        // 파일명 생성 (타임스탬프 포함)
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
        String savedFilename = "interview_schedule_" + timestamp + fileExtension;

        // 파일 저장
        Path filePath = uploadPath.resolve(savedFilename);
        Files.copy(file.getInputStream(), filePath);

        log.info("면접 일정 엑셀 파일 업로드 완료: {}", filePath.toString());

        return FileUploadResponseDto.builder()
                .message("면접 일정 엑셀 파일 업로드가 완료되었습니다.")
                .filePath(filePath.toString())
                .fileName(savedFilename)
                .uploadTime(LocalDateTime.now())
                .build();
    }

    // 통합된 파싱 및 저장 메서드
    private ExcelParseResponseDto parseAndSaveInterviewSchedule(String filePath) {
        List<ExcelParseResponseDto.ParseError> errors = new ArrayList<>();
        int successCount = 0;
        int errorCount = 0;
    
        try {
            Workbook workbook = createWorkbook(filePath);
            Sheet sheet = workbook.getSheetAt(0);
    
            int startRow = 1; // 헤더 행 건너뛰기
            int processedCount = 0;
    
            for (int i = startRow; i <= sheet.getLastRowNum(); i++) {
                Row row = sheet.getRow(i);
    
                if (row == null || isEmptyRow(row)) {
                    continue;
                }
    
                processedCount++;
                try {
                    InterviewScheduleExcelDto schedule = parseScheduleRow(row, i + 1);
                    saveInterviewAndInterviewees(schedule);
                    successCount++;
                } catch (Exception e) {
                    errorCount++;
                    errors.add(new ExcelParseResponseDto.ParseError(i + 1, e.getMessage()));
                    log.error("Excel 행 파싱 실패 - 행 {}: {}", i + 1, e.getMessage());
                }
            }
    
            workbook.close();
    
        } catch (Exception e) {
            errorCount++;
            errors.add(new ExcelParseResponseDto.ParseError(0, "파일 읽기 실패: " + e.getMessage()));
            log.error("Excel 파일 파싱 실패: {}", e.getMessage());
        }
    
        String message = String.format("총 %d개 일정 중 %d개 성공, %d개 실패",
                                     successCount + errorCount, successCount, errorCount);
    
        return new ExcelParseResponseDto(
                message,
                successCount + errorCount, // processedCount
                successCount,
                errorCount,
                errors
        );
    }

    // 통합된 Interview와 Interviewee 저장 로직
    @Transactional
    public void saveInterviewAndInterviewees(InterviewScheduleExcelDto scheduleDto) {
        // 1. Interview 생성 및 저장
        Interview interview = Interview.builder()
                .roomNo(scheduleDto.getRoomName())
                .round(1)
                .scheduledAt(LocalDateTime.of(scheduleDto.getInterviewDate(), scheduleDto.getStartTime()))
                .scheduledEndAt(LocalDateTime.of(scheduleDto.getInterviewDate(), scheduleDto.getEndTime()))
                .orderNo(1)
                .status(Interview.InterviewStatus.SCHEDULED)
                .interviewers(String.join(", ", scheduleDto.getInterviewerNames())) // 면접관을 문자열로 저장
                .createdAt(LocalDateTime.now())
                .build();

        interview = interviewRepository.save(interview);
        log.info("면접 저장 완료: interviewId={}", interview.getInterviewId());
        // 2. Interviewee 생성/조회 및 InterviewInterviewee 관계 생성
        for (String intervieweeName : scheduleDto.getIntervieweeNames()) {
            Interviewee interviewee = getOrCreateInterviewee(intervieweeName);

            InterviewInterviewee interviewInterviewee = InterviewInterviewee.builder()
                    .interviewId(interview.getInterviewId())
                    .intervieweeId(interviewee.getIntervieweeId())
                    .createdAt(LocalDateTime.now())
                    .build();

            interviewIntervieweeRepository.save(interviewInterviewee);
            log.info("관계 저장 완료: interviewId={}, intervieweeId={}", interview.getInterviewId(), interviewee.getIntervieweeId());
        }
    }


    private Workbook createWorkbook(String filePath) throws IOException {
        // 절대 경로로 변환
        Path fullPath;
        if (Paths.get(filePath).isAbsolute()) {
            fullPath = Paths.get(filePath);
        } else {
            // 상대 경로인 경우 업로드 디렉토리와 결합
            fullPath = Paths.get(uploadDir, "interview-schedule", filePath);
        }

        if (filePath.toLowerCase().endsWith(".xlsx")) {
            return new XSSFWorkbook(Files.newInputStream(fullPath));
        } else if (filePath.toLowerCase().endsWith(".xls")) {
            return new HSSFWorkbook(Files.newInputStream(fullPath));
        } else {
            throw new IllegalArgumentException("지원하지 않는 파일 형식입니다.");
        }
    }

    private InterviewScheduleExcelDto parseScheduleRow(Row row, int rowNumber) {
        try {
            // 면접날짜 (A열)
            Cell dateCell = row.getCell(0);
            LocalDate interviewDate = parseDateCell(dateCell);

            // 면접시간 (B열) - "09:00~09:30" 형식
            Cell timeCell = row.getCell(1);
            String timeRange = getCellValueAsString(timeCell);
            String[] times = timeRange.split("~");
            if (times.length != 2) {
                throw new IllegalArgumentException("시간 형식이 올바르지 않습니다: " + timeRange);
            }
            LocalTime startTime = LocalTime.parse(times[0].trim());
            LocalTime endTime = LocalTime.parse(times[1].trim());

            // 면접 호실 (C열)
            Cell roomCell = row.getCell(2);
            String roomName = getCellValueAsString(roomCell);

            // 면접관 이름 (D열) - "홍길동, 강감찬, 이순신" 형식
            Cell interviewerCell = row.getCell(3);
            String interviewerStr = getCellValueAsString(interviewerCell);
            List<String> interviewerNames = Arrays.stream(interviewerStr.split(","))
                    .map(String::trim)
                    .filter(name -> !name.isEmpty())
                    .collect(Collectors.toList());

            // 지원자 (E열) - "지원자1, 지원자2" 형식 또는 "1~2명" 형식
            Cell intervieweeCell = row.getCell(4);
            String intervieweeStr = getCellValueAsString(intervieweeCell);
            List<String> intervieweeNames = new ArrayList<>();

            if (intervieweeStr.contains("~") && intervieweeStr.contains("명")) {
                // "1~2명" 형식인 경우 빈 리스트로 처리 (실제 지원자명이 없음)
                intervieweeNames = new ArrayList<>();
            } else {
                // 실제 지원자명이 있는 경우
                intervieweeNames = Arrays.stream(intervieweeStr.split(","))
                        .map(String::trim)
                        .filter(name -> !name.isEmpty())
                        .collect(Collectors.toList());
            }

            return InterviewScheduleExcelDto.builder()
                    .interviewDate(interviewDate)
                    .startTime(startTime)
                    .endTime(endTime)
                    .roomName(roomName)
                    .interviewerNames(interviewerNames)
                    .intervieweeNames(intervieweeNames)
                    .build();

        } catch (Exception e) {
            throw new RuntimeException("행 파싱 실패: " + e.getMessage(), e);
        }
    }


    private LocalDate parseDateCell(Cell cell) {
        if (cell == null) {
            throw new IllegalArgumentException("면접날짜가 비어있습니다.");
        }

        if (cell.getCellType() == CellType.NUMERIC && DateUtil.isCellDateFormatted(cell)) {
            return cell.getLocalDateTimeCellValue().toLocalDate();
        } else if (cell.getCellType() == CellType.STRING) {
            String dateStr = cell.getStringCellValue().trim();
            try {
                return LocalDate.parse(dateStr, DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            } catch (Exception e) {
                try {
                    return LocalDate.parse(dateStr, DateTimeFormatter.ofPattern("yyyy/MM/dd"));
                } catch (Exception e2) {
                    throw new IllegalArgumentException("날짜 형식이 올바르지 않습니다: " + dateStr);
                }
            }
        }

        throw new IllegalArgumentException("날짜 셀 형식을 인식할 수 없습니다.");
    }

    private String getCellValueAsString(Cell cell) {
        if (cell == null) {
            return "";
        }

        switch (cell.getCellType()) {
            case STRING:
                return cell.getStringCellValue().trim();
            case NUMERIC:
                if (DateUtil.isCellDateFormatted(cell)) {
                    return cell.getLocalDateTimeCellValue().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
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

    private Interviewee getOrCreateInterviewee(String intervieweeName) {
        return intervieweeRepository.findByName(intervieweeName)
                .orElseGet(() -> {
                    // 새 지원자 생성
                    Interviewee newInterviewee = Interviewee.builder()
                            .name(intervieweeName)
                            .score(0)  // 추가
                            .build();
                    return intervieweeRepository.save(newInterviewee);
                });
    }
    private String generateApplicantCode(String name) {
        return "APP_" + name.hashCode() + "_" + System.currentTimeMillis();
    }

    // 빈 행 체크 메서드 추가
    private boolean isEmptyRow(Row row) {
        for (int i = 0; i < 5; i++) { // A~E열 체크
            Cell cell = row.getCell(i);
            if (cell != null && !getCellValueAsString(cell).trim().isEmpty()) {
                return false;
            }
        }
        return true;
    }
}