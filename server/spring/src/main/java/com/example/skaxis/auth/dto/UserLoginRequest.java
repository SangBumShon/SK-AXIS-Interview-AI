package com.example.skaxis.auth.dto;

import lombok.Data;

@Data
public class UserLoginRequest {
    private String userName;
    private String password;
}
