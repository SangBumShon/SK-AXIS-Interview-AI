package com.example.skaxis.service;

import com.example.skaxis.dto.ExcelParseResponseDto;
import com.example.skaxis.dto.FileUploadResponseDto;
import com.example.skaxis.dto.IntervieweeDto;
import com.example.skaxis.entity.InterviewStatus;
import com.example.skaxis.entity.Interviewee;
import com.example.skaxis.repository.IntervieweeRepository;
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

    // 기본 CRUD 작업만 유지
    public List<Interviewee> getAllInterviewees() {
        return intervieweeRepository.findAll();
    }

    public Optional<Interviewee> getIntervieweeById(Long id) {
        return intervieweeRepository.findById(id);
    }

    public Optional<Interviewee> getIntervieweeByName(String name) {
        return intervieweeRepository.findByName(name);
    }

    public Interviewee createInterviewee(String name) {
        Interviewee interviewee = Interviewee.builder()
                .name(name)
                .createdAt(LocalDateTime.now())
                .build();
        return intervieweeRepository.save(interviewee);
    }

    public boolean existsByName(String name) {
        return intervieweeRepository.existsByName(name);
    }
    
    public void deleteInterviewee(Long id) {
        intervieweeRepository.deleteById(id);
    }
}