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
}