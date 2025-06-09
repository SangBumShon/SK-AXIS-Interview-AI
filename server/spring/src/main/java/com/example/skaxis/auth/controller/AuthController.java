package com.example.skaxis.auth.controller;

import com.example.skaxis.user.Role;
import com.example.skaxis.auth.constants.AuthConstants;
import com.example.skaxis.auth.dto.UserSignupRequest;
import com.example.skaxis.auth.jwt.JWTUtil;
import com.example.skaxis.auth.jwt.TokenStatus;
import com.example.skaxis.user.model.User;
import com.example.skaxis.user.service.UserService;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RequiredArgsConstructor
@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {
    private final UserService userService;
    private final JWTUtil jwtUtil;

    @PostMapping("/signup/admin")
    public ResponseEntity<?> signupAdmin(@RequestBody UserSignupRequest adminSignupRequest) {
        return signup(adminSignupRequest.getUserName(), adminSignupRequest.getPassword(), 
                adminSignupRequest.getName(), Role.ADMIN);
    }
    @PostMapping("/signup/interviewer")
    public ResponseEntity<?> signupInterviewer(@RequestBody UserSignupRequest interviewerSignupRequest) {
        return signup(interviewerSignupRequest.getUserName(), interviewerSignupRequest.getPassword(),
                interviewerSignupRequest.getName(), Role.INTERVIEWER);
    }

    private ResponseEntity<?> signup(String userName,String password,String name,Role userType) {
        try{
            //사용자 중복 확인
            if(userService.findByUserName(userName) != null) {
                return ResponseEntity.status(HttpStatus.CONFLICT).body("Username already exists");
            }

            User user = new User();
            user.setUserName(userName);
            user.setPassword(password);
            user.setName(name);
            user.setUserType(userType);

            userService.save(user);
            return ResponseEntity.status(HttpStatus.CREATED).body("Signup successful");
        } catch (Exception e) {
            log.error("Sign up error: {}",e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Internal Server Error");
        }
    }

    @PostMapping("/reissue")
    public ResponseEntity<?> reissue(HttpServletRequest request,HttpServletResponse response) {
        String reissueToken = null;
        Cookie[] cookies = request.getCookies();
        for(Cookie cookie : cookies) {
            if(cookie.getName().equals(AuthConstants.REFRESH_PREFIX))
                reissueToken = cookie.getValue();
        }
        if(jwtUtil.validateRefreshToken(reissueToken)== TokenStatus.INVALID
                ||!jwtUtil.isExistRefreshToken(reissueToken))
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Invalid refresh token");

        if(jwtUtil.validateRefreshToken(reissueToken)==TokenStatus.EXPIRED) {
            jwtUtil.deleteRefreshToken(reissueToken);
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Expired refresh token");
        }
        String username = jwtUtil.getUserNameByRefreshToken(reissueToken);
        String role = jwtUtil.getUserRoleByRefreshToken(reissueToken);

        User user = new User();
        user.setUserName(username);
        user.setUserType(Role.valueOf(role));

        String accessToken = jwtUtil.generateAccessToken(user);
        String refreshToken = jwtUtil.generateRefreshToken(user);

        //기존의 refresh token 삭제,새로 저장
        jwtUtil.deleteRefreshToken(reissueToken);
        jwtUtil.addRefreshToken(refreshToken,user.getUserName());

        //재발급시 refreshToken도 재발급 => Refresh Rotate 방식
        response.addHeader(AuthConstants.JWT_ISSUE_HEADER, AuthConstants.ACCESS_PREFIX + accessToken);
        response.addCookie(jwtUtil.createCookie(AuthConstants.REFRESH_PREFIX, refreshToken));

        return ResponseEntity.status(HttpStatus.CREATED).body("Reissue successful");
    }
}