package com.example.skaxis.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(authz -> authz
                // Swagger UI 관련 경로 허용
                .requestMatchers("/swagger-ui/**", "/v3/api-docs/**", "/swagger-ui.html").permitAll()
                // API 경로들 허용 (필요에 따라 수정)
                .requestMatchers("/api/**", "/interviewees/**", "/upload/**", "/parse/**").permitAll()
                // 새로 추가된 면접 일정 API 허용
                .requestMatchers("/api/interview-schedule/**").permitAll()
                .requestMatchers("/api/media/**").permitAll()
                .anyRequest().authenticated()
            );
        
        return http.build();
    }
}