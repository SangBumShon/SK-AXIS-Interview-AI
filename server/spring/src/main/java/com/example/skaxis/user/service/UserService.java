package com.example.skaxis.user.service;

import com.example.skaxis.user.model.User;
import org.springframework.stereotype.Service;

import com.example.skaxis.user.Role;
import java.util.List;

@Service
public interface UserService {
    User save(User user);
}
