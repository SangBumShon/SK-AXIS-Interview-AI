package com.example.skaxis.auth.jwt;

import com.example.skaxis.auth.model.RefreshToken;
import com.example.skaxis.user.model.User;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import jakarta.servlet.http.Cookie;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.PropertySource;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Component
@Slf4j
@PropertySource("classpath:application-jwt.properties")
public class JWTUtil {
    private final RedisTemplate<String, RefreshToken> redisTemplate;

    private final Key ACCESS_SECRET_KEY;
    private final Key REFRESH_SECRET_KEY;
    private final long ACCESS_TOKEN_EXPIRATION_TIME;
    private final long REFRESH_TOKEN_EXPIRATION_TIME;
    public JWTUtil(RedisTemplate<String, RefreshToken> redisTemplate,
                    @Value("${jwt.access-secret}") String accessSecret,
                    @Value("${jwt.refresh-secret}") String refreshSecret,
                    @Value("${jwt.access-expiration}") long accessExpiration,
                    @Value("${jwt.refresh-expiration}") long refreshExpiration) {
        this.redisTemplate = redisTemplate;
        ACCESS_SECRET_KEY = getSigningKey(accessSecret);
        REFRESH_SECRET_KEY = getSigningKey(refreshSecret);
        ACCESS_TOKEN_EXPIRATION_TIME = accessExpiration;
        REFRESH_TOKEN_EXPIRATION_TIME = refreshExpiration;

    }
    private Key getSigningKey(String secretKey) {
        String encodedKey = Base64.getEncoder().encodeToString(secretKey.getBytes());
        return Keys.hmacShaKeyFor(encodedKey.getBytes(StandardCharsets.UTF_8));
    }

    /*
    *  ******************* Token Generator ********************
    * */
    public String generateAccessToken(User user) {

        return Jwts.builder()
                .setHeader(createHeader())
                .setSubject(user.getUserName())
                .setClaims(createClaims(user))
                .setExpiration(new Date(System.currentTimeMillis() + ACCESS_TOKEN_EXPIRATION_TIME))
                .signWith(ACCESS_SECRET_KEY, SignatureAlgorithm.HS256)
                .compact();
    }
    public String generateRefreshToken(User user) {
        return Jwts.builder()
                .setHeader(createHeader())
                .setSubject(user.getUserName())
                .setClaims(createClaims(user))
                .setExpiration(new Date(System.currentTimeMillis() + REFRESH_TOKEN_EXPIRATION_TIME))
                .signWith(REFRESH_SECRET_KEY,SignatureAlgorithm.HS256)
                .compact();
    }

    private Map<String,Object> createClaims(User user) {
        Map<String,Object> claims = new HashMap<>();
        claims.put("user", user.getName());
        claims.put("userName", user.getUserName());
        claims.put("role", user.getUserType());
        return claims;
    }

    private Map<String,Object> createHeader() {
        Map<String,Object> header = new HashMap<>();
        header.put("typ","JWT");
        header.put("alg","HS256");
        return header;
    }

    /*
     *  ******************* Token 유효성검사 ********************
     * */
    public TokenStatus validateAccessToken(String accessToken) {
        return getTokenStatus(accessToken,ACCESS_SECRET_KEY);
    }
    public TokenStatus validateRefreshToken(String refreshToken) {
        return getTokenStatus(refreshToken,REFRESH_SECRET_KEY);
    }

    private TokenStatus getTokenStatus(String token, Key secretKey) {
        try{
            Jwts.parserBuilder()
                    .setSigningKey(secretKey)
                    .build()
                    .parseClaimsJws(token);
            return TokenStatus.AUTHENTICATED;
        } catch (ExpiredJwtException | IllegalArgumentException e) {
            log.error(e.getMessage());
            return TokenStatus.EXPIRED;
        }catch (JwtException e) {
            log.error(e.getMessage());
            throw new JwtException(e.getMessage());
        }
    }

    /*
     *  ******************* Token 분해 ********************
     * */
    public String getUserNameByAccessToken(String token){
        return Jwts.parserBuilder()
                .setSigningKey(ACCESS_SECRET_KEY)
                .build()
                .parseClaimsJws(token)
                .getBody().get("userName", String.class);
    }
    public String getUserNameByRefreshToken(String token){
        return Jwts.parserBuilder()
                .setSigningKey(REFRESH_SECRET_KEY)
                .build()
                .parseClaimsJws(token)
                .getBody().get("userName", String.class);
    }
    public String getUserRoleByAccessToken(String token){
        return Jwts.parserBuilder()
                .setSigningKey(ACCESS_SECRET_KEY)
                .build()
                .parseClaimsJws(token)
                .getBody().get("role", String.class);
    }
    public String getUserRoleByRefreshToken(String token){
        return Jwts.parserBuilder()
                .setSigningKey(REFRESH_SECRET_KEY)
                .build()
                .parseClaimsJws(token)
                .getBody().get("role", String.class);
    }

    /*
     *  ******************* Cookie setting ********************
     * */
    public Cookie createCookie(String key, String value){
        Cookie cookie = new Cookie(key,value);
        cookie.setMaxAge(0);
        cookie.setHttpOnly(true);

        return cookie;
    }

    /*
     *  ******************* refresh repository using redis ********************
     * */
    public void addRefreshToken(String refreshToken,String userName){
        Date date = new Date(System.currentTimeMillis() + REFRESH_TOKEN_EXPIRATION_TIME);

        RefreshToken entity = new RefreshToken();
        entity.setUserName(userName);
        entity.setToken(refreshToken);
        entity.setExpiration(date.toString());

        redisTemplate.opsForValue().set(userName,entity);
        log.info("redis add refresh token {}",getRefreshToken(refreshToken));
    }
    public RefreshToken getRefreshToken(String token){
        String userName = getUserNameByRefreshToken(token);
        return redisTemplate.opsForValue().get(userName);
    }
    public void deleteRefreshToken(String token){
        String userName = getUserNameByRefreshToken(token);
        redisTemplate.delete(userName);
    }

    public boolean isExistRefreshToken(String token) {
        return getRefreshToken(token)!=null;
    }
}
