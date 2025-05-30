package com.example.skaxis.auth.filter;

import com.example.skaxis.auth.constants.AuthConstants;
import com.example.skaxis.auth.dto.LoginResponse;
import com.example.skaxis.auth.dto.UserLoginRequest;
import com.example.skaxis.auth.jwt.JWTUtil;
import com.example.skaxis.user.model.CustomUserDetail;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletInputStream;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.util.StreamUtils;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

@Slf4j
public class LoginFilter extends UsernamePasswordAuthenticationFilter {
    private final AuthenticationManager authenticationManager;
    private final JWTUtil jwtUtil;
    private final ObjectMapper objectMapper;

    public LoginFilter(AuthenticationManager authenticationManager, JWTUtil jwtUtil, ObjectMapper objectMapper) {
        this.authenticationManager = authenticationManager;
        this.jwtUtil = jwtUtil;
        this.objectMapper = objectMapper;
        setFilterProcessesUrl("/signin");
    }

    @Override
    public Authentication attemptAuthentication(HttpServletRequest request, HttpServletResponse response)throws AuthenticationException{

        try {
            ServletInputStream inputStream = request.getInputStream();
            String messageBody = StreamUtils.copyToString(inputStream, StandardCharsets.UTF_8);

            UserLoginRequest loginRequest = objectMapper.readValue(messageBody, UserLoginRequest.class);
            //spring security에서 검증하기 위해서는 username, password를   token에 담아야 한다.
            UsernamePasswordAuthenticationToken authRequest = new UsernamePasswordAuthenticationToken(loginRequest.getEmail(), loginRequest.getPassword());
            //token을 authenticationManager로 전달
            return authenticationManager.authenticate(authRequest);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
    @Override
    protected void successfulAuthentication(HttpServletRequest request, HttpServletResponse response,
                                            FilterChain filterChain,Authentication authentication) throws IOException {
        //login 성공시 실행하는 로직
        CustomUserDetail customUserDetail = (CustomUserDetail) authentication.getPrincipal();

        String accessToken = jwtUtil.generateAccessToken(customUserDetail.getUser());
        String refreshToken = jwtUtil.generateRefreshToken(customUserDetail.getUser());
        log.info("refreshToken: {}", refreshToken);
        log.info("accessToken: {}", accessToken);


        jwtUtil.addRefreshToken(refreshToken, customUserDetail.getUser().getEmail());

        response.addHeader(AuthConstants.JWT_ISSUE_HEADER, AuthConstants.ACCESS_PREFIX + accessToken);
        response.addCookie(jwtUtil.createCookie(AuthConstants.REFRESH_PREFIX, refreshToken));
        response.setStatus(HttpServletResponse.SC_OK);

        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        LoginResponse data = new LoginResponse(customUserDetail.getUser());

        //json으로 변환
        String result = objectMapper.writeValueAsString(data);

        response.getWriter().print(result);
    }
    @Override
    protected void unsuccessfulAuthentication(HttpServletRequest request, HttpServletResponse response,
                                            AuthenticationException failed){
        //login 실패시 실행하는 로직
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
    }

}
