package com.example.skaxis.auth.dto;

import lombok.Data;

@Data
public class ClientSignupRequest {
    private String username;
    private String password;
}
