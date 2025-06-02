package com.example.skaxis.interviewee.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.example.skaxis.interviewee.model.Interviewee;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface IntervieweeRepository extends JpaRepository<Interviewee, Long> {
    @Query("SELECT i FROM Interviewee i WHERE " +
           "(:date IS NULL OR i.interviewDate = :date) AND " +
           "(:status IS NULL OR i.interviewStatus = :status) AND " +
           "(:position IS NULL OR i.position = :position)")
    // 수정된 메서드명
    boolean existsByApplicantId(String applicantId);

    // 새로 추가: 날짜별 면접 대상자 조회
    @Query("SELECT i FROM Interviewee i WHERE i.interviewDate = :date ORDER BY i.interviewDate, i.applicantName")
    List<Interviewee> findByInterviewDateOrderByTime(@Param("date") LocalDate date);

    Optional<Interviewee> findByApplicantId(String applicantId);
}