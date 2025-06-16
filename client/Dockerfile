FROM node:16-alpine as build

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY package*.json ./
RUN npm install

# Tailwind CSS 및 추가 패키지 설치
RUN npm install -D tailwindcss@latest postcss@latest autoprefixer@latest @tailwindcss/postcss
RUN npm install @mediapipe/pose @mediapipe/camera_utils @mediapipe/drawing_utils @mediapipe/tasks-vision
RUN npm install axios vue-router@4 pinia@latest chart.js vue-chartjs

# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build

# 실행 이미지 생성
FROM nginx:stable-alpine

# Nginx 설정 복사
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 추가 파일 디렉토리 생성
RUN mkdir -p /usr/share/nginx/html/assets
RUN mkdir -p /usr/share/nginx/html/downloads

# 환경 변수 설정
ENV API_URL="/api"
ENV WS_URL="/ws"

# 포트 노출
EXPOSE 80

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]