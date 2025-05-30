package com.example.skaxis.auth.dto;

import com.example.skaxis.user.Role;
import com.example.skaxis.user.model.User;
import lombok.Getter;

@Getter
public class LoginResponse {
    private final String username;
    private final Role userType;

    public LoginResponse(User user) {
        this.username = user.getUserName();
        this.userType = user.getUserType();
    }
}
