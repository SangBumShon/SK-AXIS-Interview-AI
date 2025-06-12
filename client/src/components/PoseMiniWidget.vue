<template>
  <div style="position:relative; width:100%; height:100%;">
    <video
      ref="video"
      width="1280" height="720"
      autoplay
      muted
      playsinline
      style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:contain; z-index:1; background:#111;"
    ></video>
    <canvas
      ref="canvas"
      width="1280" height="720"
      style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:10; pointer-events:none; background:transparent;"
    ></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as faceapi from 'face-api.js'
import {
  FilesetResolver,
  PoseLandmarker
} from '@mediapipe/tasks-vision'

// 1. WebSocket 연결
const wsUrl = `ws://localhost:8000/api/v1/ws/nonverbal`// 서버 주소에 맞게 수정
let ws = null
function connectWebSocket() {
  ws = new WebSocket(wsUrl)
  ws.onopen = () => console.log('WebSocket 연결됨')
  ws.onerror = err => console.error('WebSocket 에러:', err)
  ws.onclose = () => console.log('WebSocket 연결 종료')
}
connectWebSocket()

const video = ref(null)
const canvas = ref(null)
let poseLandmarker
let active = true

const LEFT_KNEE = 25, RIGHT_KNEE = 26
const NOSE = 0, LEFT_SHOULDER = 11, RIGHT_SHOULDER = 12
const POSE_FACE_LANDMARKS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
let spreadCount = [0, 0]
let shakeCount = [0, 0]
let headDownCount = [0, 0]
let prevKneeY = [
  { left: null, right: null, max: null, min: null },
  { left: null, right: null, max: null, min: null }
]
let lastCountedTime = 0

const expList = ['미소', '무표정', '당황', '울상', '찡그림']
const expKorean = {
  happy: '미소', sad: '울상', angry: '찡그림', surprised: '당황',
  neutral: '무표정', fearful: '불안', disgusted: '불쾌'
}
let faceExpCount = [
  Object.fromEntries(expList.map(e => [e, 0])),
  Object.fromEntries(expList.map(e => [e, 0]))
]

function detectSpeaking(landmarks) {
  if (!landmarks || !landmarks.positions) return false
  const topLip = landmarks.positions[62]
  const bottomLip = landmarks.positions[66]
  const leftMouth = landmarks.positions[60]
  const rightMouth = landmarks.positions[64]
  if (!topLip || !bottomLip || !leftMouth || !rightMouth) return false
  const mouthOpen = Math.abs(topLip.y - bottomLip.y)
  const mouthWidth = Math.abs(leftMouth.x - rightMouth.x)
  return mouthOpen > 20 && mouthWidth > 25
}

function isValidKeypoint(lm) {
  return (
    lm &&
    ((typeof lm.visibility === "number" && lm.visibility > 0.5) ||
      (typeof lm.presence === "number" && lm.presence > 0.5) ||
      (lm.visibility === undefined && lm.presence === undefined)) &&
    lm.x >= 0.0 && lm.x <= 1.0 &&
    lm.y >= 0.0 && lm.y <= 1.0
  )
}

function analyzeLegByKnee(poseLandmarks, k) {
  if (!isValidKeypoint(poseLandmarks[LEFT_KNEE]) || !isValidKeypoint(poseLandmarks[RIGHT_KNEE]))
    return { kneeSpread: 0, kneeShakeAmp: 0, valid: false }

  const kneeSpread = Math.abs(poseLandmarks[LEFT_KNEE].x - poseLandmarks[RIGHT_KNEE].x)
  const avgKneeY = (poseLandmarks[LEFT_KNEE].y + poseLandmarks[RIGHT_KNEE].y) / 2

  if (prevKneeY[k].min === null || prevKneeY[k].max === null) {
    prevKneeY[k].min = avgKneeY
    prevKneeY[k].max = avgKneeY
  } else {
    prevKneeY[k].min = Math.min(prevKneeY[k].min, avgKneeY)
    prevKneeY[k].max = Math.max(prevKneeY[k].max, avgKneeY)
  }

  const kneeShakeAmp = prevKneeY[k].max - prevKneeY[k].min
  return { kneeSpread, kneeShakeAmp, valid: true }
}

function getSortedPersonIndexes(landmarksArr) {
  if (!landmarksArr || landmarksArr.length === 0) return []
  if (landmarksArr.length === 1) return [0]
  let centers = []
  for (let i = 0; i < landmarksArr.length; i++) {
    const lmArr = landmarksArr[i]
    if (!lmArr || lmArr.length === 0) continue
    const avgX = lmArr.reduce((acc, l) => acc + l.x, 0) / lmArr.length
    centers.push({ i, avgX })
  }
  centers.sort((a, b) => a.avgX - b.avgX)
  return centers.map(c => c.i)
}

onMounted(async () => {
  await faceapi.nets.tinyFaceDetector.loadFromUri('/models/tiny_face_detector')
  await faceapi.nets.faceLandmark68Net.loadFromUri('/models/face_landmark_68')
  await faceapi.nets.faceExpressionNet.loadFromUri('/models/face_expression')

  while (!video.value) await new Promise(r => requestAnimationFrame(r))
  const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } })
  video.value.srcObject = stream
  await new Promise(resolve => { video.value.onloadedmetadata = resolve })

  const vision = await FilesetResolver.forVisionTasks('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm')
  poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task'
    },
    runningMode: 'VIDEO',
    numPoses: 2,
    outputSegmentationMasks: false
  })

  const analyze = async () => {
    if (!active) return
    const ctx = canvas.value.getContext('2d')
    ctx.clearRect(0, 0, 1280, 720)
    ctx.drawImage(video.value, 0, 0, 1280, 720)

    const poses = poseLandmarker.detectForVideo(video.value, performance.now())
    let poseIndexes = getSortedPersonIndexes(poses.landmarks)
    if (poseIndexes.length > 2) poseIndexes = poseIndexes.slice(0, 2)

    let detections = await faceapi.detectAllFaces(video.value, new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks()
      .withFaceExpressions()
    detections.sort((a, b) => a.detection.box.x - b.detection.box.x)
    if (detections.length > 2) detections = detections.slice(0, 2)

    const numPersons = Math.max(poseIndexes.length, detections.length)
    if (numPersons === 0) {
      requestAnimationFrame(analyze)
      return
    }

    // 얼굴 랜드마크/박스 시각화
    if (detections.length === 1) {
      const color = 'lime'
      const det = detections[0]
      for (const pt of det.landmarks.positions) {
        ctx.beginPath()
        ctx.arc(pt.x, pt.y, 2.2, 0, 2 * Math.PI)
        ctx.fillStyle = color
        ctx.fill()
      }
      const box = det.detection.box
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.strokeRect(box.x, box.y, box.width, box.height)
      ctx.font = 'bold 20px sans-serif'
      ctx.fillStyle = color
      ctx.fillText(`person1`, box.x, box.y - 8)
    } else if (detections.length === 2) {
      for (let k = 0; k < 2; k++) {
        const color = k === 0 ? 'lime' : 'yellow'
        const det = detections[k]
        for (const pt of det.landmarks.positions) {
          ctx.beginPath()
          ctx.arc(pt.x, pt.y, 2.2, 0, 2 * Math.PI)
          ctx.fillStyle = color
          ctx.fill()
        }
        const box = det.detection.box
        ctx.strokeStyle = color
        ctx.lineWidth = 2
        ctx.strokeRect(box.x, box.y, box.width, box.height)
        ctx.font = 'bold 20px sans-serif'
        ctx.fillStyle = color
        ctx.fillText(`person${k + 1}`, box.x, box.y - 8)
      }
    }

    // 포즈 랜드마크 시각화
    for (let k = 0; k < poseIndexes.length; k++) {
      const i = poseIndexes[k]
      const landmarks = poses.landmarks[i]
      if (!landmarks || landmarks.length < 20) continue
      const color = k === 0 ? 'aqua' : 'orange'
      for (let j = 0; j < landmarks.length; j++) {
        ctx.beginPath()
        ctx.arc(landmarks[j].x * 1280, landmarks[j].y * 720, 3, 0, 2 * Math.PI)
        ctx.fillStyle = color
        ctx.fill()
      }
    }

    // 1초마다 JSON 송신
    if (Date.now() - lastCountedTime > 1000) {
      for (let k = 0; k < numPersons; k++) {
        let isSpeaking = false
        if (detections[k]) {
          isSpeaking = detectSpeaking(detections[k].landmarks)
        }

        let poseObj = { leg_spread: 0, leg_shake: 0, head_down: 0 }
        if (poseIndexes[k] !== undefined) {
          const i = poseIndexes[k]
          const landmarks = poses.landmarks[i]
          if (landmarks && landmarks.length >= 20) {
            const { kneeSpread, kneeShakeAmp, valid } = analyzeLegByKnee(landmarks, k)
            if (valid && (kneeSpread > 0.21)) spreadCount[k] += 1
            if (valid && (kneeShakeAmp > 0.04)) shakeCount[k] += 1
            const nose = landmarks[NOSE]
            const avgShoulderY = (landmarks[LEFT_SHOULDER].y + landmarks[RIGHT_SHOULDER].y) / 2
            if (nose && nose.y > avgShoulderY + 0.04) headDownCount[k] += 1
            poseObj = {
              leg_spread: spreadCount[k],
              leg_shake: shakeCount[k],
              head_down: headDownCount[k]
            }
            prevKneeY[k].min = prevKneeY[k].max = (landmarks[LEFT_KNEE].y + landmarks[RIGHT_KNEE].y) / 2
          }
        }
        if (!faceExpCount[k]) faceExpCount[k] = Object.fromEntries(expList.map(e => [e, 0]))
        let faceExpTmp = Object.fromEntries(expList.map(e => [e, 0]))
        if (detections[k]) {
          const det = detections[k]
          const expLabel = Object.entries(det.expressions)
            .reduce((max, cur) => cur[1] > max[1] ? cur : max)[0]
          const expKor = expKorean[expLabel] || expLabel
          if (faceExpTmp[expKor] !== undefined) faceExpTmp[expKor] += 1
          for (let key of expList) {
            faceExpCount[k][key] += faceExpTmp[key]
          }
        }

        // ----- JSON 송신 -----
        const payload = {
          person: k + 1,
          speaking: isSpeaking,
          pose: poseObj,
          expression: Object.fromEntries(expList.map(e => [e, faceExpCount[k][e] || 0])),
          timestamp: new Date().toISOString()
        }
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(payload))
        }
        // 개발/테스트용 로그 출력
        console.log(payload)
      }
      lastCountedTime = Date.now()
    }

    requestAnimationFrame(analyze)
  }
  analyze()
})

onBeforeUnmount(() => {
  active = false
  if (ws) ws.close()
})
</script>
