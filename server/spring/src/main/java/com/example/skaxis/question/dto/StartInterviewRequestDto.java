package com.example.skaxis.question.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class StartInterviewRequestDto {
    private List<Integer> intervieweeIds;
}