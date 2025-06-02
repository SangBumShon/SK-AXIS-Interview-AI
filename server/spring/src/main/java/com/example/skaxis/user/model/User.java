package com.example.skaxis.user.model;

import java.time.LocalDateTime;

import com.example.skaxis.user.Role;
import lombok.Data;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import jakarta.persistence.Column;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.EnumType;

@Data
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Long userId;

    @Column(name = "username", length = 50, nullable = false, unique = true)
    private String userName;
    
    @Column(name = "password_hash", length = 255, nullable = false)
    private String password;
    
    @Column(name = "name", length = 50, nullable = false)
    private String name;
    
    @Enumerated(EnumType.STRING)    
    @Column(name = "user_type")
    private Role userType;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
