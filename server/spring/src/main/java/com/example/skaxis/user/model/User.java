package com.example.skaxis.user.model;

import com.example.skaxis.user.Role;
import lombok.Data;
import org.springframework.data.annotation.Id;

@Data
public class User {
    @Id
    private String userName;
    private String password;
    private String name;
    private Role userType;
}