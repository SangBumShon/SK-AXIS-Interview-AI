package com.example.skaxis.user.service;

import com.example.skaxis.user.model.User;
import org.springframework.stereotype.Service;


@Service
public interface UserService {
    User save(User user);
    User findByUserName(String userName);
}
