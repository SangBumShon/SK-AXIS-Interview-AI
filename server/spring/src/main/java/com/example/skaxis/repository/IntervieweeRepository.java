package com.example.skaxis.repository;

import com.example.skaxis.entity.Interviewee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface IntervieweeRepository extends JpaRepository<Interviewee, Long> {
    
    List<Interviewee> findByInterviewDate(LocalDate date);
    
    List<Interviewee> findByInterviewStatus(Interviewee.InterviewStatus status);
    
    List<Interviewee> findByPosition(String position);
    
    @Query("SELECT i FROM Interviewee i WHERE " +
           "(:date IS NULL OR i.interviewDate = :date) AND " +
           "(:status IS NULL OR i.interviewStatus = :status) AND " +
           "(:position IS NULL OR i.position = :position)")
    List<Interviewee> findByFilters(@Param("date") LocalDate date, 
                                   @Param("status") Interviewee.InterviewStatus status, 
                                   @Param("position") String position);
    
    // 수정된 메서드명
    boolean existsByApplicantId(String applicantId);
    
    // 추가 메서드들
    boolean existsByApplicantCode(String applicantCode);
}