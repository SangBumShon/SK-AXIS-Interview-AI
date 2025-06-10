package com.example.skaxis.question;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum Type {
    COMMON("공통질문"),
    INDIVIDUAL("개별질문");

    private final String value;
}
