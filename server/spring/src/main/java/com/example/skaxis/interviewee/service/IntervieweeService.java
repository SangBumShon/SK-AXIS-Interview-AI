package com.example.skaxis.interviewee.service;

import com.example.skaxis.interviewee.model.Interviewee;
import com.example.skaxis.interviewee.repository.IntervieweeRepository;
import com.example.skaxis.util.dto.ExcelParseResponseDto;
import com.example.skaxis.util.dto.FileUploadResponseDto;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.ByteArrayOutputStream;
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
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class IntervieweeService {

    private final IntervieweeRepository intervieweeRepository;

    @Value("${app.upload.dir:/uploads/interviewees}")
    private String uploadDir;

    // 선택적 내보내기
    public byte[] exportSelectedInterviewees(List<Long> intervieweeIds, boolean includeResults) {
        List<Interviewee> interviewees = intervieweeRepository.findAllById(intervieweeIds);
        return createExcelFromInterviewees(interviewees, includeResults);
    }

    // 업데이트 모드 파싱
    public FileUploadResponseDto importExcelWithUpdate(MultipartFile file, boolean updateMode) {
        List<IntervieweeDto> parsedData = parseExcelFileToDto(file);

        if (updateMode) {
            return updateExistingInterviewees(parsedData);
        } else {
            return createNewInterviewees(parsedData);
        }
    }

    // 기존 데이터 업데이트
    private FileUploadResponseDto updateExistingInterviewees(List<IntervieweeDto> data) {
        List<String> errors = new ArrayList<>();
        int successCount = 0;

        for (IntervieweeDto dto : data) {
            try {
                // applicantId로 기존 데이터 찾기
                Optional<Interviewee> existing = intervieweeRepository.findByApplicantId(dto.getApplicantId());

                if (existing.isPresent()) {
                    updateIntervieweeData(existing.get(), dto);
                    intervieweeRepository.save(existing.get());
                    successCount++;
                } else {
                    errors.add("지원자 ID " + dto.getApplicantId() + "를 찾을 수 없습니다.");
                }
            } catch (Exception e) {
                errors.add("행 처리 중 오류: " + e.getMessage());
            }
        }

        return FileUploadResponseDto.builder()
                .message("업데이트 완료")
                .filePath("")
                .fileName("")
                .uploadTime(LocalDateTime.now())
                .successCount(successCount)
                .errorCount(errors.size())
                .errors(errors)
                .build();
    }

    // 새로운 면접자 생성
    private FileUploadResponseDto createNewInterviewees(List<IntervieweeDto> data) {
        List<String> errors = new ArrayList<>();
        int successCount = 0;

        for (IntervieweeDto dto : data) {
            try {
                // 중복 체크
                if (intervieweeRepository.existsByApplicantId(dto.getApplicantId())) {
                    errors.add("이미 존재하는 지원자 ID: " + dto.getApplicantId());
                    continue;
                }

                Interviewee interviewee = convertDtoToEntity(dto);
                intervieweeRepository.save(interviewee);
                successCount++;
            } catch (Exception e) {
                errors.add("데이터 생성 중 오류: " + e.getMessage());
            }
        }

        return FileUploadResponseDto.builder()
                .message("새 데이터 생성 완료")
                .filePath("")
                .fileName("")
                .uploadTime(LocalDateTime.now())
                .successCount(successCount)
                .errorCount(errors.size())
                .errors(errors)
                .build();
    }

    // DTO를 Entity로 변환
    private Interviewee convertDtoToEntity(IntervieweeDto dto) {
        return Interviewee.builder()
                .applicantName(dto.getApplicantName())
                .applicantId(dto.getApplicantId())
                .position(dto.getPosition())
                .interviewDate(dto.getInterviewDate())
                .interviewStatus(dto.getInterviewStatus())
                .score(dto.getScore())
                .interviewer(dto.getInterviewer())
                .interviewLocation(dto.getInterviewLocation())
                .build();
    }

    // 기존 데이터 업데이트
    private void updateIntervieweeData(Interviewee existing, IntervieweeDto dto) {
        if (StringUtils.hasText(dto.getApplicantName())) {
            existing.setApplicantName(dto.getApplicantName());
        }
        if (StringUtils.hasText(dto.getPosition())) {
            existing.setPosition(dto.getPosition());
        }
        if (dto.getInterviewDate() != null) {
            existing.setInterviewDate(dto.getInterviewDate());
        }
        if (dto.getInterviewStatus() != null) {
            existing.setInterviewStatus(dto.getInterviewStatus());
        }
        if (dto.getScore() != null) {
            existing.setScore(dto.getScore());
        }
        if (StringUtils.hasText(dto.getInterviewer())) {
            existing.setInterviewer(dto.getInterviewer());
        }
        if (StringUtils.hasText(dto.getInterviewLocation())) {
            existing.setInterviewLocation(dto.getInterviewLocation());
        }
    }

    // Excel에서 DTO 리스트로 파싱
    private List<IntervieweeDto> parseExcelFileToDto(MultipartFile file) {
        List<IntervieweeDto> result = new ArrayList<>();

        try (Workbook workbook = new XSSFWorkbook(file.getInputStream())) {
            Sheet sheet = workbook.getSheetAt(0);

            for (int i = 1; i <= sheet.getLastRowNum(); i++) {
                Row row = sheet.getRow(i);
                if (row == null) continue;

                IntervieweeDto dto = parseRowToDto(row, i + 1);
                if (dto != null) {
                    result.add(dto);
                }
            }
        } catch (IOException e) {
            throw new RuntimeException("Excel 파일 파싱 중 오류: " + e.getMessage());
        }

        return result;
    }

    // Row를 DTO로 변환
    private IntervieweeDto parseRowToDto(Row row, int rowNumber) {
        try {
            return IntervieweeDto.builder()
                    .applicantName(getCellValueAsString(row.getCell(0)))
                    .applicantId(getCellValueAsString(row.getCell(1)))
                    .position(getCellValueAsString(row.getCell(2)))
                    .interviewDate(parseDateCell(row.getCell(3)))
                    .interviewStatus(parseStatusCell(row.getCell(4)))
                    .score(parseScoreCell(row.getCell(5)))
                    .interviewer(getCellValueAsString(row.getCell(6)))
                    .interviewLocation(getCellValueAsString(row.getCell(7)))
                    .build();
        } catch (Exception e) {
            log.error("행 {} 파싱 오류: {}", rowNumber, e.getMessage());
            return null;
        }
    }

    // Excel에서 면접자 리스트 생성
    private byte[] createExcelFromInterviewees(List<Interviewee> interviewees, boolean includeResults) {
        try (Workbook workbook = new XSSFWorkbook();
             ByteArrayOutputStream out = new ByteArrayOutputStream()) {

            Sheet sheet = workbook.createSheet("면접자 목록");

            // 헤더 생성
            Row headerRow = sheet.createRow(0);
            String[] headers = {"지원자명", "지원식별ID", "직무", "면접날짜", "면접상태", "점수", "면접관", "면접장소"};
            for (int i = 0; i < headers.length; i++) {
                headerRow.createCell(i).setCellValue(headers[i]);
            }

            // 데이터 행 생성
            int rowNum = 1;
            for (Interviewee interviewee : interviewees) {
                Row row = sheet.createRow(rowNum++);
                row.createCell(0).setCellValue(interviewee.getApplicantName());
                row.createCell(1).setCellValue(interviewee.getApplicantId());
                row.createCell(2).setCellValue(interviewee.getPosition());
                row.createCell(3).setCellValue(interviewee.getInterviewDate() != null ? interviewee.getInterviewDate().toString() : "");
                row.createCell(4).setCellValue(interviewee.getInterviewStatus() != null ? interviewee.getInterviewStatus().name() : "");
                row.createCell(5).setCellValue(interviewee.getScore() != null ? interviewee.getScore() : 0);
                row.createCell(6).setCellValue(interviewee.getInterviewer() != null ? interviewee.getInterviewer() : "");
                row.createCell(7).setCellValue(interviewee.getInterviewLocation() != null ? interviewee.getInterviewLocation() : "");
            }

            workbook.write(out);
            return out.toByteArray();

        } catch (IOException e) {
            throw new RuntimeException("Excel 파일 생성 중 오류: " + e.getMessage());
        }
    }

    // 날짜 셀 파싱
    private LocalDate parseDateCell(Cell cell) {
        if (cell == null) return null;

        if (cell.getCellType() == CellType.NUMERIC && DateUtil.isCellDateFormatted(cell)) {
            return cell.getLocalDateTimeCellValue().toLocalDate();
        } else {
            String dateStr = getCellValueAsString(cell);
            if (StringUtils.hasText(dateStr)) {
                try {
                    return LocalDate.parse(dateStr);
                } catch (Exception e) {
                    log.warn("날짜 파싱 실패: {}", dateStr);
                }
            }
        }
        return null;
    }

    // 상태 셀 파싱
    private Interviewee.InterviewStatus parseStatusCell(Cell cell) {
        String statusStr = getCellValueAsString(cell);
        if (StringUtils.hasText(statusStr)) {
            try {
                return Interviewee.InterviewStatus.valueOf(statusStr.toUpperCase());
            } catch (IllegalArgumentException e) {
                log.warn("잘못된 면접 상태: {}", statusStr);
            }
        }
        return null;
    }

    // 점수 셀 파싱
    private Integer parseScoreCell(Cell cell) {
        if (cell != null && cell.getCellType() == CellType.NUMERIC) {
            return (int) cell.getNumericCellValue();
        }
        return null;
    }

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

        return FileUploadResponseDto.builder()
                .message("파일이 성공적으로 업로드되었습니다.")
                .filePath(filePath.toString())
                .fileName(originalFilename)
                .uploadTime(LocalDateTime.now())
                .build();
    }

    public ExcelParseResponseDto parseExcelFile(String filePath) {
        List<ExcelParseResponseDto.ParseError> errors = new ArrayList<>();
        List<Interviewee> validInterviewees = new ArrayList<>();
        int processedCount = 0;

        try (FileInputStream fis = new FileInputStream(new File(filePath));
             Workbook workbook = new XSSFWorkbook(fis)) {

            Sheet sheet = workbook.getSheetAt(0);

            // 1단계: 전체 데이터 검증 (저장하지 않음)
            for (int i = 1; i <= sheet.getLastRowNum(); i++) {
                Row row = sheet.getRow(i);
                if (row == null) continue;

                processedCount++;

                try {
                    Interviewee interviewee = parseRowToInterviewee(row, i + 1);

                    // 중복 체크
                    if (intervieweeRepository.existsByApplicantId(interviewee.getApplicantId())) {
                        errors.add(new ExcelParseResponseDto.ParseError(i + 1,
                                "이미 존재하는 지원식별ID입니다: " + interviewee.getApplicantId()));
                        continue;
                    }

                    // 메모리에 임시 저장
                    validInterviewees.add(interviewee);

                } catch (Exception e) {
                    errors.add(new ExcelParseResponseDto.ParseError(i + 1, e.getMessage()));
                }
            }

            // 2단계: 오류가 있으면 전체 중단
            if (!errors.isEmpty()) {
                throw new RuntimeException("Excel 파일에 오류가 있습니다. 모든 오류를 수정한 후 다시 업로드해주세요.");
            }

            // 3단계: 모든 데이터가 유효할 때만 일괄 저장
            intervieweeRepository.saveAll(validInterviewees);

            return new ExcelParseResponseDto(
                    "Excel 파일이 성공적으로 파싱되어 데이터베이스에 저장되었습니다.",
                    processedCount,
                    validInterviewees.size(),
                    0,
                    new ArrayList<>()
            );

        } catch (IOException e) {
            throw new RuntimeException("Excel 파일을 읽는 중 오류가 발생했습니다: " + e.getMessage());
        }
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

    // 내부 DTO 클래스
    @lombok.Data
    @lombok.Builder
    @lombok.NoArgsConstructor
    @lombok.AllArgsConstructor
    public static class IntervieweeDto {
        private String applicantName;
        private String applicantId;
        private String position;
        private LocalDate interviewDate;
        private Interviewee.InterviewStatus interviewStatus;
        private Integer score;
        private String interviewer;
        private String interviewLocation;
    }
}