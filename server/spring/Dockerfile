# 빌드 스테이지
FROM --platform=linux/amd64 gradle:8.7-jdk17 AS build
WORKDIR /app

# Gradle Wrapper 및 프로젝트 파일 복사
COPY . .

# Gradle 빌드 (테스트 생략)
RUN ./gradlew build -x test

# 실행 이미지 생성
FROM --platform=linux/amd64 openjdk:17-slim
WORKDIR /app

# 빌드 결과 JAR 복사
COPY --from=build /app/build/libs/*.jar app.jar

# 출력 디렉토리 생성
RUN mkdir -p /shared-output

# 환경 변수 설정
ENV SPRING_DATASOURCE_URL="jdbc:mysql://mysql:3306/skaxis?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true"
ENV SPRING_DATASOURCE_USERNAME="skaxis"
ENV SPRING_DATASOURCE_PASSWORD="skaxispassword"
ENV SPRING_JPA_HIBERNATE_DDL_AUTO="update"
ENV FASTAPI_URL="http://fastapi:8000/api/v1"
ENV OUTPUT_DIR="/shared-output"

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
