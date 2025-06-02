package com.example.skaxis.auth.dto;

import lombok.Data;

@Data
public class UserSignupRequest {
    private String userName;
    private String name;
    private String password;
}
