package com.example.skaxis.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class InterviewScheduleResponseDto {
    private List<RoomDto> rooms;
    private List<TimeSlotDto> timeSlots;
    private List<PersonDto> people;
    private String message;
}