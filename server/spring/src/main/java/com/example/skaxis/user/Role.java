package com.example.skaxis.user;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum Role {
    INTERVIEWER("ROLE_INTERVIEWER"),
    ADMIN("ROLE_ADMIN");

    private final String value;
}
