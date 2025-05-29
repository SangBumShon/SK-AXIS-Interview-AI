FROM maven:3.8.6-openjdk-17-slim AS build

WORKDIR /app

# 의존성 파일 복사
COPY pom.xml .
# 의존성 다운로드 (캐싱 활용)
RUN mvn dependency:go-offline -B

# 소스 코드 복사 및 빌드
COPY src ./src
RUN mvn package -DskipTests

# 실행 이미지 생성
FROM openjdk:17-slim

WORKDIR /app

# 빌드 단계에서 생성된 JAR 파일 복사
COPY --from=build /app/target/*.jar app.jar

# 환경 변수 설정
ENV SPRING_DATASOURCE_URL="jdbc:mysql://mysql:3306/skaxis?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true"
ENV SPRING_DATASOURCE_USERNAME="skaxis"
ENV SPRING_DATASOURCE_PASSWORD="skaxispassword"
ENV SPRING_JPA_HIBERNATE_DDL_AUTO="update"
ENV FASTAPI_URL="http://fastapi:8000/api/v1"
ENV OUTPUT_DIR="/shared-output"

# 포트 노출
EXPOSE 8080

# 애플리케이션 실행
ENTRYPOINT ["java", "-jar", "app.jar"]
