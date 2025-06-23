package com.example.skaxis.auth.filter;

import com.example.skaxis.auth.constants.AuthConstants;
import com.example.skaxis.auth.jwt.JWTUtil;
import com.example.skaxis.auth.jwt.TokenStatus;
import com.example.skaxis.user.Role;
import com.example.skaxis.user.model.CustomUserDetail;
import com.example.skaxis.user.model.User;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;

@RequiredArgsConstructor
@Slf4j
public class JWTFilter extends OncePerRequestFilter {
    private final JWTUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {
        //permittedURI는 토큰 검사를 진행하지 않는다.
        if(isPermittedURI(request.getRequestURI())){
            log.info("허용된 uri : " + request.getRequestURI());
            filterChain.doFilter(request, response);
            return;
        }

        //request 에서 Authorization 헤더를 찾음.
        String authorizationHeader = request.getHeader(AuthConstants.JWT_ISSUE_HEADER);
        
        // Authorization 헤더가 없거나 Bearer로 시작하지 않으면 인증 없이 통과
        if (authorizationHeader == null || !authorizationHeader.startsWith(AuthConstants.ACCESS_PREFIX)) {
            log.warn("Authorization header is missing or invalid format: {}", authorizationHeader);
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            PrintWriter writer = response.getWriter();
            writer.print("Authorization header is required");
            return;
        }
        
        String token = authorizationHeader.replace(AuthConstants.ACCESS_PREFIX, "");

        if(jwtUtil.validateAccessToken(token)==TokenStatus.INVALID) {
            log.error("Token is invalid");
            //response body
            PrintWriter writer = response.getWriter();
            writer.print("access token invalid");
            //response status
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }
        if(jwtUtil.validateAccessToken(token)==TokenStatus.EXPIRED) {
            log.error("Token is expired");
            //response body
            PrintWriter writer = response.getWriter();
            writer.print("access token expired");
            //response status
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }
        String userName = jwtUtil.getUserNameByAccessToken(token);
        String role = jwtUtil.getUserRoleByAccessToken(token);
        User user = new User();
        user.setUserName(userName);
        user.setPassword("tmp");
        user.setUserType(Role.valueOf(role));

        CustomUserDetail customUserDetail = new CustomUserDetail(user);
        Authentication authentication = new UsernamePasswordAuthenticationToken(customUserDetail, null, customUserDetail.getAuthorities());
        SecurityContextHolder.getContext().setAuthentication(authentication);

        filterChain.doFilter(request, response);
    }
    
    private boolean isPermittedURI(String uri) {
        return Arrays.stream(AuthConstants.PERMITTED_URI)
                .anyMatch(permitted->{
                    String replace = permitted.replace("*","");
                    return uri.contains(replace)||replace.contains(uri);
                });
    }
}
