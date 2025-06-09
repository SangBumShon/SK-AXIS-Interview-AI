package com.example.skaxis.interview.exception;

public class IntervieweeNotFoundException extends RuntimeException {
    public IntervieweeNotFoundException(String message) {
        super(message);
    }
    
    public IntervieweeNotFoundException(Long id) {
        super("Interviewee not found with ID: " + id);
    }
}