package com.example.skaxis.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("SK-AXIS AI 면접 시스템 API")
                        .version("1.0.0")
                        .description("AI 기반 면접 시스템의 REST API 문서입니다.")
                        .contact(new Contact()
                                .name("SK-AXIS Team")
                                .email("support@sk-axis.com")))
                .servers(List.of(
                        new Server().url("http://localhost:8080").description("개발 서버"),
                        new Server().url("https://api.sk-axis.com").description("운영 서버")
                ));
    }
}