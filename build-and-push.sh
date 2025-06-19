#!/bin/bash

# 설정
DOCKER_USERNAME="wochae"
APP_NAME="skaxis"
VERSION="latest"

echo "=== SK-AXIS 빌드 및 도커 허브 푸시 시작 ==="

# Docker Hub 로그인 확인
echo "Docker Hub 로그인 상태 확인..."
docker info | grep Username || {
    echo "Docker Hub에 로그인해주세요:"
    docker login
}

# Docker buildx 설정 (멀티 플랫폼 빌드용)
docker buildx rm multiplatform 2>/dev/null || true
docker buildx create --use --name multiplatform


# Spring Boot 이미지 빌드
echo "Spring Boot 이미지 빌드 중..."
docker buildx build --platform linux/amd64,linux/arm64 \
    -t ${DOCKER_USERNAME}/${APP_NAME}-server:${VERSION} \
    --push ./server/spring
if [ $? -ne 0 ]; then
    echo "Spring Boot 빌드 실패!"
    exit 1
fi

# FastAPI 이미지 빌드
# echo "FastAPI 이미지 빌드 중..."
# docker build -t ${DOCKER_USERNAME}/${APP_NAME}-fastapi:${VERSION} ./ai
# if [ $? -ne 0 ]; then
#     echo "FastAPI 빌드 실패!"
#     exit 1
# fi

# 이미지 푸시
echo "이미지를 Docker Hub에 푸시 중..."
docker push ${DOCKER_USERNAME}/${APP_NAME}-server:${VERSION}
# docker push ${DOCKER_USERNAME}/${APP_NAME}-fastapi:${VERSION}

echo "=== 빌드 및 푸시 완료! ==="
echo "Spring Boot: ${DOCKER_USERNAME}/${APP_NAME}-server:${VERSION}"
# echo "FastAPI: ${DOCKER_USERNAME}/${APP_NAME}-fastapi:${VERSION}"