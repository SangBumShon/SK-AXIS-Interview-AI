package com.example.skaxis.interview.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.example.skaxis.interview.model.Interview;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface InterviewRepository extends JpaRepository<Interview, Long> {
    
    @Query("SELECT i FROM Interview i WHERE DATE(i.scheduledAt) = :date ORDER BY i.scheduledAt")
    List<Interview> findByScheduledDate(@Param("date") LocalDate date);
    
    // 고유한 면접실 ID들을 조회하는 메서드 추가
    @Query("SELECT DISTINCT i.roomId FROM Interview i WHERE i.roomId IS NOT NULL ORDER BY i.roomId")
    List<String> findDistinctRoomIds();
    
    // 특정 날짜의 고유한 면접실 ID들을 조회하는 메서드 추가
    @Query("SELECT DISTINCT i.roomId FROM Interview i WHERE DATE(i.scheduledAt) = :date AND i.roomId IS NOT NULL ORDER BY i.roomId")
    List<String> findDistinctRoomIdsByDate(@Param("date") LocalDate date);
}