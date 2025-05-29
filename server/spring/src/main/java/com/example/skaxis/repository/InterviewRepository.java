package com.example.skaxis.repository;

import com.example.skaxis.entity.Interview;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface InterviewRepository extends JpaRepository<Interview, Long> {
    
    @Query("SELECT i FROM Interview i WHERE DATE(i.scheduledAt) = :date ORDER BY i.scheduledAt")
    List<Interview> findByScheduledDate(@Param("date") LocalDate date);
    
    @Query("SELECT i FROM Interview i WHERE i.roomId = :roomId AND DATE(i.scheduledAt) = :date ORDER BY i.scheduledAt")
    List<Interview> findByRoomIdAndScheduledDate(@Param("roomId") String roomId, @Param("date") LocalDate date);
    
    List<Interview> findByRoomId(String roomId);
}