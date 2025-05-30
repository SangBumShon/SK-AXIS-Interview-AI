package com.example.skaxis.user.service;

import com.example.skaxis.user.Role;
import com.example.skaxis.user.model.CustomUserDetail;
import com.example.skaxis.user.model.User;
import com.example.skaxis.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class CustomUserDetailService implements UserDetailsService,UserService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        //CustomUserDetails 객체를 생성하여 넘겨줘야한다.
        // User user = findByEmail(email);
        User user = null;

        if (user == null)
            return null;
        return new CustomUserDetail(user);//UserDetail instance 에 넘겨주면 AuthenicationManager가 검증한다.
    }

    //UserService method//
    @Override
    public User save(User user) {
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        // userRepository.save(user);
        return user;
    }

}