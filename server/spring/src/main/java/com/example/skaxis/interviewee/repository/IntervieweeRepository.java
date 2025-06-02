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

    Optional<Interviewee> findByName(String name);

    boolean existsByName(String name);
}