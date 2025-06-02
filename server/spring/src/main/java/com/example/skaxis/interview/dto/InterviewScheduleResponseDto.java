package com.example.skaxis.interview.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

import com.example.skaxis.util.dto.PersonDto;
import com.example.skaxis.util.dto.RoomDto;
import com.example.skaxis.util.dto.TimeSlotDto;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class InterviewScheduleResponseDto {
    private List<RoomDto> rooms;
    private List<TimeSlotDto> timeSlots;
    private List<PersonDto> people;
    private String message;
}