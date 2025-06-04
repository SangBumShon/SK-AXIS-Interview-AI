package com.example.skaxis.config;

import com.example.skaxis.auth.constants.AuthConstants;
import com.example.skaxis.auth.filter.CustomLogoutFilter;
import com.example.skaxis.auth.filter.JWTFilter;
import com.example.skaxis.auth.filter.LoginFilter;
import com.example.skaxis.auth.jwt.JWTUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.authentication.logout.LogoutFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.CorsUtils;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

import static org.springframework.security.config.Customizer.withDefaults;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    //authenticationManager가 인자로 받을 AuthenticationConfiguration객체
    private final AuthenticationConfiguration authenticationConfiguration;
    private final JWTUtil jwtUtil;

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authenticationConfiguration)throws Exception {
        return authenticationConfiguration.getAuthenticationManager();

    }
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .cors(withDefaults())
                .csrf(AbstractHttpConfigurer::disable) //disable crsf
                .formLogin(AbstractHttpConfigurer::disable)// disable formLogin
                .httpBasic(AbstractHttpConfigurer::disable)//disable http basic
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth->auth
                        .requestMatchers(CorsUtils::isPreFlightRequest).permitAll()
                        .requestMatchers(AuthConstants.ADMIN_URI).hasRole("ADMIN")
                        .requestMatchers(AuthConstants.PERMITTED_URI).permitAll()// Swagger UI 관련 경로 허용
                        .requestMatchers("/swagger-ui/**", "/v3/api-docs/**", "/swagger-ui.html").permitAll()
                        // API 경로들 허용 (필요에 따라 수정)
                        .requestMatchers("/api/**", "/interviewees/**", "/upload/**", "/parse/**").permitAll()
                        // 새로 추가된 면접 일정 API 허용
                        .requestMatchers("/api/interview-schedule/**").permitAll()
                        .requestMatchers("/api/media/**").permitAll()
                        .anyRequest().authenticated())
                .addFilterBefore(new CustomLogoutFilter(jwtUtil), LogoutFilter.class)
                .addFilterBefore(new JWTFilter(jwtUtil),LoginFilter.class)
                .addFilterAt(new LoginFilter(authenticationManager(authenticationConfiguration),jwtUtil,objectMapper()), UsernamePasswordAuthenticationFilter.class);


        return http.build();
    }
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(); // 비밀번호 암호화를 위해 BCrypt 사용
    }
    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());
        return objectMapper;
    }
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(List.of(
            "http://localhost:*",
            "http://127.0.0.1:*",
            "http://192.168.*.*:*"  // 로컬 네트워크 허용
        ));
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);
    
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}