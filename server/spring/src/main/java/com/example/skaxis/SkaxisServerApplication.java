
package com.example.skaxis;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;

@SpringBootApplication
@EntityScan({"com.example.skaxis.entity", "com.example.skaxis.user.model"})
public class SkaxisServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(SkaxisServerApplication.class, args);
    }
}
