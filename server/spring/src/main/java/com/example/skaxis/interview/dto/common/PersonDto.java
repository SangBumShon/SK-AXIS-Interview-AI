package com.example.skaxis.interview.dto.common;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PersonDto {
    private String id;
    private String name;
    private String role; // "interviewer" or "candidate"
}