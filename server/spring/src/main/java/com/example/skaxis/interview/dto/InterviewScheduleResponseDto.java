package com.example.skaxis.interview.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

import com.example.skaxis.interview.dto.common.PersonDto;
import com.example.skaxis.interview.dto.common.RoomDto;
import com.example.skaxis.interview.dto.common.TimeSlotDto;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InterviewScheduleResponseDto {
    private List<RoomDto> rooms;
    private List<TimeSlotDto> timeSlots;
    private List<PersonDto> people;
    private String message;
}