<template>
  <div style="position:relative; width:100%; height:100%;">
    <video
      ref="video"
      width="1280" height="720"
      autoplay
      muted
      playsinline
      style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; z-index:1; background:#111;"
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
import {
  FilesetResolver,
  PoseLandmarker,
  FaceLandmarker,
} from '@mediapipe/tasks-vision'

const video = ref(null)
const canvas = ref(null)
let poseLandmarker, faceLandmarker
let active = true

const LEFT_ANKLE = 27, RIGHT_ANKLE = 28
const LEFT_KNEE = 25, RIGHT_KNEE = 26
const NOSE = 0, LEFT_SHOULDER = 11, RIGHT_SHOULDER = 12
const POSE_FACE_LANDMARKS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

// ★ 최종 표정 평가 항목(5종)
const FINAL_EXP_TYPES = [
  '무표정', '미소', '울상', '당황', '찡그림'
]

// 원래의 분류 (추론용)
const EXP_TYPES = [
  '입벌림', '무표정', '미소',
  '울상', '당황', '찡그림', '놀람', '찡그림+입', '눈웃음'
]

// 평가 항목별 카운트
let spreadCount = [0, 0]
let shakeCount = [0, 0]
let headDownCount = [0, 0]
let faceExpCount = [
  Object.fromEntries(FINAL_EXP_TYPES.map(e => [e, 0])),
  Object.fromEntries(FINAL_EXP_TYPES.map(e => [e, 0])),
]
let prevAnkleY = [null, null]
let lastCountedTime = 0

// 표정 mapping 함수
function mapExpression(exp) {
  if (exp === '눈웃음' || exp === '미소') return '미소'
  if (exp === '찡그림+입' || exp === '찡그림') return '찡그림'
  if (exp === '놀람' || exp === '당황') return '당황'
  if (exp === '울상') return '울상'
  // 입벌림은 무표정으로 처리
  return '무표정'
}

// --- 표정 분석 정규화 버전 ---
function analyzeFaceExpression(faceLandmarks) {
  const LEFT_MOUTH = 61, RIGHT_MOUTH = 291, TOP_LIP = 13, BOTTOM_LIP = 14
  const LEFT_CORNER = 78, RIGHT_CORNER = 308
  const LEFT_EYE_TOP = 159, RIGHT_EYE_TOP = 386, LEFT_EYE_BOTTOM = 145, RIGHT_EYE_BOTTOM = 374
  const LEFT_BROW = 70, RIGHT_BROW = 300
  const NOSE_TIP = 1
  const CHIN = 152
  const FOREHEAD = 10

  const leftMouth = faceLandmarks[LEFT_MOUTH]
  const rightMouth = faceLandmarks[RIGHT_MOUTH]
  const topLip = faceLandmarks[TOP_LIP]
  const bottomLip = faceLandmarks[BOTTOM_LIP]
  const leftCorner = faceLandmarks[LEFT_CORNER]
  const rightCorner = faceLandmarks[RIGHT_CORNER]
  const leftEyeTop = faceLandmarks[LEFT_EYE_TOP]
  const leftEyeBottom = faceLandmarks[LEFT_EYE_BOTTOM]
  const rightEyeTop = faceLandmarks[RIGHT_EYE_TOP]
  const rightEyeBottom = faceLandmarks[RIGHT_EYE_BOTTOM]
  const leftBrow = faceLandmarks[LEFT_BROW]
  const rightBrow = faceLandmarks[RIGHT_BROW]
  const noseTip = faceLandmarks[NOSE_TIP]
  const chin = faceLandmarks[CHIN]
  const forehead = faceLandmarks[FOREHEAD]

  const faceHeight = Math.max(0.001, Math.abs(chin.y - forehead.y))
  const mouthOpen = Math.abs(topLip.y - bottomLip.y) / faceHeight
  const mouthWidth = Math.abs(leftMouth.x - rightMouth.x) / faceHeight
  const mouthCornerSlope = (leftCorner.y - rightCorner.y) / ((leftCorner.x - rightCorner.x) + 1e-6)
  const isSadMouth = mouthCornerSlope > 0.05
  const isSmile = mouthCornerSlope < -0.07
  const leftEyeHeight = Math.abs(leftEyeTop.y - leftEyeBottom.y) / faceHeight
  const rightEyeHeight = Math.abs(rightEyeTop.y - rightEyeBottom.y) / faceHeight
  const leftBrowDist = Math.abs(leftEyeTop.y - leftBrow.y) / faceHeight
  const rightBrowDist = Math.abs(rightEyeTop.y - rightBrow.y) / faceHeight
  const avgBrowDist = (leftBrowDist + rightBrowDist) / 2
  const chinLipDist = Math.abs(chin.y - bottomLip.y) / faceHeight

  if (mouthOpen > 0.25 && leftEyeHeight > 0.11 && rightEyeHeight > 0.11 && avgBrowDist > 0.035) {
    return '당황'
  }
  if (isSadMouth && avgBrowDist < 0.018 && mouthWidth < 0.18) {
    return '울상'
  }
  if (avgBrowDist < 0.012 && isSadMouth) {
    return '찡그림'
  }
  if (mouthOpen > 0.34 && chinLipDist > 0.31 && avgBrowDist > 0.034) {
    return '놀람'
  }
  if (isSmile && mouthWidth > 0.22) {
    if (leftEyeHeight < 0.053 && rightEyeHeight < 0.053) {
      return '눈웃음'
    }
    return '미소'
  }
  if (mouthOpen > 0.15 && mouthWidth > 0.15) {
    return '입벌림'
  }
  if (
    mouthOpen < 0.07 &&
    Math.abs(mouthCornerSlope) < 0.035 &&
    leftEyeHeight > 0.038 &&
    rightEyeHeight > 0.038
  ) {
    return '무표정'
  }
  if (avgBrowDist < 0.013 && mouthOpen > 0.13) {
    return '찡그림+입'
  }
  return '무표정'
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
function analyzeLegSpread(poseLandmarks) {
  if (
    !isValidKeypoint(poseLandmarks[LEFT_ANKLE]) ||
    !isValidKeypoint(poseLandmarks[RIGHT_ANKLE]) ||
    !isValidKeypoint(poseLandmarks[LEFT_KNEE]) ||
    !isValidKeypoint(poseLandmarks[RIGHT_KNEE])
  ) return { ankleSpread: 0, kneeSpread: 0, valid: false }
  const ankleSpread = Math.abs(poseLandmarks[LEFT_ANKLE].x - poseLandmarks[RIGHT_ANKLE].x)
  const kneeSpread = Math.abs(poseLandmarks[LEFT_KNEE].x - poseLandmarks[RIGHT_KNEE].x)
  return { ankleSpread, kneeSpread, valid: true }
}

const SIMPLE_POSE_CONNECTIONS = [
  [11, 13], [13, 15], [12, 14], [14, 16],
  [11, 12], [23, 24],
  [23, 25], [25, 27], [24, 26], [26, 28],
  [27, 31], [28, 32]
]
const poseColors = ['red', 'blue']
const faceColors = ['lime', 'yellow']

function getPersonIndexes(landmarksArr) {
  if (!landmarksArr || landmarksArr.length === 0) return []
  if (landmarksArr.length === 1) return [0]
  let centers = []
  for (let i = 0; i < landmarksArr.length; i++) {
    const lmArr = landmarksArr[i]
    if (!lmArr || lmArr.length === 0) continue
    const avgX = lmArr.reduce((acc, l) => acc + l.x, 0) / lmArr.length
    const avgY = lmArr.reduce((acc, l) => acc + l.y, 0) / lmArr.length
    centers.push({ i, dist: Math.hypot(avgX - 0.5, avgY - 0.5) })
  }
  centers.sort((a, b) => a.dist - b.dist)
  if (centers.length >= 2) {
    const first = centers[0]
    const second = centers[1]
    const dist = Math.abs(first.dist - second.dist)
    if (dist < 0.08) return [first.i]
    return [first.i, second.i]
  }
  return [centers[0].i]
}

onMounted(async () => {
  while (!video.value) {
    await new Promise(r => requestAnimationFrame(r))
  }

  const stream = await navigator.mediaDevices.getUserMedia({
    video: { width: 1280, height: 720 }
  })
  video.value.srcObject = stream
  await new Promise(resolve => {
    video.value.onloadedmetadata = resolve
  })

  const vision = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm'
  )

  poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task'
    },
    runningMode: 'VIDEO',
    numPoses: 2,
    outputSegmentationMasks: false
  })

  faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'
    },
    runningMode: 'VIDEO',
    numFaces: 2,
    minDetectionConfidence: 0.8,
    minTrackingConfidence: 0.8,
    outputFaceBlendshapes: false,
    outputFacialTransformationMatrixes: false
  })

  const analyze = () => {
    if (!active) return
    const ctx = canvas.value.getContext('2d')
    ctx.clearRect(0, 0, 1280, 720)
    ctx.drawImage(video.value, 0, 0, 1280, 720)

    const poses = poseLandmarker.detectForVideo(
      video.value,
      performance.now()
    )
    const faces = faceLandmarker.detectForVideo(
      video.value,
      performance.now()
    )

    const poseIndexes = getPersonIndexes(poses.landmarks)
    const faceIndexes = getPersonIndexes(faces.faceLandmarks)
    const validCount = Math.max(poseIndexes.length, faceIndexes.length)
    const now = Date.now()
    const shouldCount = (now - lastCountedTime > 1000)
    if (shouldCount) lastCountedTime = now

    let isSpreadArr = []
    let isShakeArr = []
    let isHeadDownArr = []
    let expArr = []

    // ----- POSE -----
    for (let k = 0; k < poseIndexes.length; k++) {
      const i = poseIndexes[k]
      const landmarks = poses.landmarks[i]
      if (!landmarks || landmarks.length < 20) continue
      const color = poseColors[k % 2]

      for (let j = 0; j < landmarks.length; j++) {
        if (POSE_FACE_LANDMARKS.includes(j)) continue
        const pt = landmarks[j]
        ctx.beginPath()
        ctx.arc(pt.x * 1280, pt.y * 720, 4, 0, 2 * Math.PI)
        ctx.fillStyle = color
        ctx.fill()
      }
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      for (const [start, end] of SIMPLE_POSE_CONNECTIONS) {
        if (POSE_FACE_LANDMARKS.includes(start) || POSE_FACE_LANDMARKS.includes(end)) continue
        const s = landmarks[start], e = landmarks[end]
        if (s && e) {
          ctx.beginPath()
          ctx.moveTo(s.x * 1280, s.y * 720)
          ctx.lineTo(e.x * 1280, e.y * 720)
          ctx.stroke()
        }
      }
      const { ankleSpread, kneeSpread, valid } = analyzeLegSpread(landmarks)
      isSpreadArr[k] = valid && (ankleSpread > 0.3 || kneeSpread > 0.3)
      if (valid && prevAnkleY[k] !== null) {
        const dy = Math.abs(landmarks[RIGHT_ANKLE].y - prevAnkleY[k])
        isShakeArr[k] = (dy > 0.012)
      } else {
        isShakeArr[k] = false
      }
      prevAnkleY[k] = valid ? landmarks[RIGHT_ANKLE].y : null
      const nose = landmarks[NOSE]
      const avgShoulderY = (landmarks[LEFT_SHOULDER].y + landmarks[RIGHT_SHOULDER].y) / 2
      isHeadDownArr[k] = (nose && nose.y > avgShoulderY + 0.04)
      const lmk = landmarks[LEFT_SHOULDER]
      if (lmk) {
        ctx.font = 'bold 13px sans-serif'
        ctx.fillStyle = color
        ctx.fillText(`Person${k+1}: 다리벌림${isSpreadArr[k] ? '▲' : ''}`, lmk.x * 1280, lmk.y * 720 - 10)
      }
    }

    // ----- FACE -----
    for (let k = 0; k < faceIndexes.length; k++) {
      const i = faceIndexes[k]
      const color = faceColors[k % 2]
      const faceLandmarks = faces.faceLandmarks[i]
      for (let j = 0; j < faceLandmarks.length; j++) {
        const pt = faceLandmarks[j]
        ctx.beginPath()
        ctx.arc(pt.x * 1280, pt.y * 720, 1.8, 0, 2 * Math.PI)
        ctx.fillStyle = color
        ctx.fill()
      }
      // ★ 표정은 mapExpression()으로 매핑하여 최종 평가 항목에 귀속
      const rawExp = analyzeFaceExpression(faceLandmarks)
      const finalExp = mapExpression(rawExp)
      expArr[k] = finalExp
      const nose = faceLandmarks[1]
      if (nose) {
        ctx.font = 'bold 13px sans-serif'
        ctx.fillStyle = color
        ctx.fillText(`표정: ${finalExp}`, nose.x * 1280, nose.y * 720 - 10)
      }
    }

    if (shouldCount) {
      for (let k = 0; k < validCount; k++) {
        if (isSpreadArr[k]) spreadCount[k] += 1
        if (isShakeArr[k]) shakeCount[k] += 1
        if (isHeadDownArr[k]) headDownCount[k] += 1
        if (expArr[k] && faceExpCount[k][expArr[k]] !== undefined) faceExpCount[k][expArr[k]] += 1
        let expStr = FINAL_EXP_TYPES.map(e => `${e}:${faceExpCount[k][e]}`).join(', ')
        console.log(
          `[Person${k+1}] 다리벌림:${spreadCount[k]}, 다리떨기:${shakeCount[k]}, 고개숙임:${headDownCount[k]}, [표정] ${expStr}`
        )
      }
    }

    requestAnimationFrame(analyze)
  }
  analyze()
})

onBeforeUnmount(() => {
  active = false
})
</script>