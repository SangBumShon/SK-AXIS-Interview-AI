package com.example.skaxis.interview.exception;

public class InterviewNotFoundException extends RuntimeException {
    public InterviewNotFoundException(String message) {
        super(message);
    }
    
    public InterviewNotFoundException(Long id) {
        super("Interview not found with ID: " + id);
    }
}