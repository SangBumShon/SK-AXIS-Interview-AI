<template>
  <div style="position:relative; width:100%; height:100%;">
    <video
      ref="video"
      autoplay
      muted
      playsinline
      style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:contain; z-index:1; background:#111;"
    ></video>
    <canvas
      ref="canvas"
      style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:100; pointer-events:none; background:transparent; border: 2px solid red;"
    ></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, defineProps, watch, defineEmits, defineExpose } from 'vue'
import * as faceapi from 'face-api.js'

const props = defineProps({
  intervieweeNames: {
    type: Array,
    required: true,
    default: () => []
  },
  intervieweeIds: {
    type: Array,
    required: true,
    default: () => []
  }
})

const emit = defineEmits(['updateNonverbalData'])

// rafId로 analyze 중복 호출 방지
let rafId = null
let active = false

// 부모 컴포넌트에서 접근 가능하도록 누적 데이터 노출
defineExpose({
  getAccumulatedNonverbalData: () => accumulatedNonverbalData.value,
  getCurrentNonverbalData: () => nonverbalData.value,
  stopDetection: () => {
    active = false
    if (rafId) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
    console.log('[감지 중단] PoseMiniWidget 감지가 중단되었습니다.')
  },
  startDetection: () => {
    console.log('[감지 시작 시도] startDetection 호출됨')
    if (!active) {
      active = true
      if (!rafId) {
        rafId = requestAnimationFrame(analyze)
      }
      console.log('[감지 시작] PoseMiniWidget 감지가 시작되었습니다.')
    } else {
      console.log('[감지 시작] 이미 감지가 활성화되어 있습니다.')
    }
  }
})

const recorderMap = ref({})
const MOUTH_CLOSED_THRESHOLD = 3000
const video = ref(null)
const canvas = ref(null)

const expList = ['미소', '무표정', '울상', '찡그림']
const expKorean = {
  happy: '미소', sad: '울상', angry: '찡그림',
  neutral: '무표정', disgusted: '불쾌'
}
const toInternalLabel = {
  '미소': 'smile', '무표정': 'neutral', '울상': 'frown', '찡그림': 'angry'
}

const faceStates = ref([])
const nonverbalData = ref({})
const accumulatedNonverbalData = ref({})
let updateInterval = null
let analyze = null

watch(() => props.intervieweeNames, (newNames) => {
  faceStates.value = newNames.map((name, index) => {
    const id = props.intervieweeIds[index]
    nonverbalData.value[id] = {
      posture: { upright: 0, leaning: 0, slouching: 0 },
      facial_expression: { smile: 0, neutral: 0, frown: 0, angry: 0 },
      gaze: 0, // placeholder
      gesture: 0, // placeholder
      timestamp: Date.now()
    }
    accumulatedNonverbalData.value[id] = {
      facial_expression_history: [],
      posture_history: [],
      gaze_history: [],
      gesture_history: [],
      start_time: Date.now()
    }
    return {
      name,
      id,
      speaking: false,
      mouthClosedStartTime: null,
      isRecording: false,
      expression: Object.fromEntries(expList.map(e => [e, 0])),
      expressionTotal: 0,
      lastExpression: null
    }
  })
}, { immediate: true })

function detectSpeaking(landmarks) {
  if (!landmarks || !landmarks.positions) return false
  const topLip = landmarks.positions[62]
  const bottomLip = landmarks.positions[66]
  const leftMouth = landmarks.positions[60]
  const rightMouth = landmarks.positions[64]
  if (!topLip || !bottomLip || !leftMouth || !rightMouth) return false
  const mouthOpen = Math.abs(topLip.y - bottomLip.y)
  const mouthWidth = Math.abs(leftMouth.x - rightMouth.x)
  return mouthOpen > 10 && mouthWidth > 20
}

async function startRecording(personIndex) {
  const state = faceStates.value[personIndex]
  if (state.isRecording) {
    console.log(`[녹음 시작 실패] ${state.name}님의 녹음이 이미 진행 중입니다.`)
    return
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mimeType = 'audio/webm'
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      console.error(`[녹음 시작 실패] ${mimeType} 형식이 지원되지 않습니다.`)
      return
    }
    const recorder = new MediaRecorder(stream, { mimeType })
    const audioChunks = []
    recorder.ondataavailable = (event) => { audioChunks.push(event.data) }
    recorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: mimeType })
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const fileName = `${state.id}_${timestamp}.webm`
      const formData = new FormData()
      formData.append('audio', audioBlob, fileName)
      formData.append('interviewee_id', state.id.toString())
      try {
        const response = await fetch('http://localhost:8000/api/v1/stt/upload', {
          method: 'POST', body: formData
        })
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(`Upload failed: ${response.status} ${errorData.detail || response.statusText}`)
        }
        await response.json()
        console.log(`[업로드 성공] ${state.name}님의 녹음 파일이 성공적으로 업로드되었습니다.`)
        state.isRecording = false
      } catch (error) {
        console.error(`[업로드 실패] ${state.name}님의 녹음 파일 업로드 중 오류 발생:`, error.message)
        state.isRecording = false
      } finally {
        if (recorder && recorder.stream) {
          recorder.stream.getTracks().forEach(track => { track.stop() })
        }
      }
    }
    recorder.start()
    state.isRecording = true
    console.log(`[녹음 시작] ${state.name}님의 녹음이 시작되었습니다.`)
    recorderMap.value[state.id] = { mediaRecorder: recorder, audioChunks, stream }
  } catch (error) {
    console.error(`[녹음 시작 실패] ${state.name}님의 녹음 시작 중 오류 발생:`, error.message)
  }
}

function stopRecording(personIndex) {
  const state = faceStates.value[personIndex]
  if (!state.isRecording) {
    console.log(`[녹음 종료 실패] ${state.name}님의 녹음이 진행 중이 아닙니다.`)
    return
  }
  if (!recorderMap.value[state.id]) {
    console.error(`[녹음 종료 실패] ${state.name}님의 MediaRecorder가 초기화되지 않았습니다.`)
    return
  }
  try {
    const recorder = recorderMap.value[state.id].mediaRecorder
    recorder.stop()
    state.isRecording = false
    console.log(`[녹음 종료] ${state.name}님의 녹음이 종료되었습니다.`)
  } catch (error) {
    console.error(`[녹음 종료 실패] ${state.name}님의 녹음 종료 중 오류 발생:`, error.message)
  }
}

// analyze 함수 정의를 변수로 할당
analyze = async function analyze() {
  if (!active) {
    rafId = null
    return
  }
  // 비디오/캔버스/스트림 체크
  if (!video.value || !canvas.value || !video.value.srcObject) {
    rafId = requestAnimationFrame(analyze)
    return
  }
  try {
    const ctx = canvas.value.getContext('2d')
    const width = canvas.value.width
    const height = canvas.value.height
    ctx.clearRect(0, 0, width, height)
    ctx.drawImage(video.value, 0, 0, width, height)
    let detections = await faceapi.detectAllFaces(video.value, new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks()
      .withFaceExpressions()
    detections = detections.slice(0, props.intervieweeNames.length)
    detections.sort((a, b) => a.detection.box.x - b.detection.box.x)
    for (let k = 0; k < detections.length; k++) {
      const det = detections[k]
      const color = k === 0 ? 'lime' : k === 1 ? 'yellow' : 'aqua'
      if (!faceStates.value[k]) continue
      const faceState = faceStates.value[k]
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
      ctx.fillText(faceState.name, box.x, box.y - 8)
      const isSpeaking = detectSpeaking(det.landmarks)
      if (isSpeaking) {
        if (!faceState.speaking) {
          console.log(`[입벌림 감지] ${faceState.name}님이 말하기 시작했습니다.`)
        }
        faceState.speaking = true
        faceState.mouthClosedStartTime = null
        if (!faceState.isRecording) {
          startRecording(k)
        }
      } else if (faceState.speaking) {
        if (!faceState.mouthClosedStartTime) {
          faceState.mouthClosedStartTime = Date.now()
        } else if (Date.now() - faceState.mouthClosedStartTime >= MOUTH_CLOSED_THRESHOLD) {
          console.log(`[녹음 종료] ${faceState.name}님이 3초 동안 말하지 않았습니다.`)
          faceState.speaking = false
          faceState.mouthClosedStartTime = null
          stopRecording(k)
        }
      }
      const expLabel = Object.entries(det.expressions)
        .reduce((max, cur) => cur[1] > max[1] ? cur : max)[0]
      const expKor = expKorean[expLabel]
      if (expKor && expList.includes(expKor)) {
        faceState.expression[expKor]++
        faceState.expressionTotal++
        faceState.lastExpression = expKor
      }
    }
  } catch (error) {
    console.error('analyze 함수 실행 중 오류:', error)
  }
  rafId = requestAnimationFrame(analyze)
}

onMounted(async () => {
  console.log('=== PoseMiniWidget 컴포넌트 마운트 시작 ===')
  try {
    console.log('face-api.js 모델 로딩 시작...')
    if (!faceapi.nets.tinyFaceDetector.isLoaded) {
      await faceapi.nets.tinyFaceDetector.loadFromUri('/models/tiny_face_detector')
    }
    if (!faceapi.nets.faceLandmark68Net.isLoaded) {
      await faceapi.nets.faceLandmark68Net.loadFromUri('/models/face_landmark_68')
    }
    if (!faceapi.nets.faceExpressionNet.isLoaded) {
      await faceapi.nets.faceExpressionNet.loadFromUri('/models/face_expression')
    }
    console.log('모든 face-api.js 모델 로딩 완료')
    try {
      while (!video.value) {
        await new Promise(r => setTimeout(r, 100))
      }
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: 1280, 
          height: 720,
          facingMode: 'user'
        } 
      })
      video.value.srcObject = stream
      await new Promise((resolve, reject) => {
        if (!video.value) {
          reject(new Error('비디오 엘리먼트가 없습니다.'))
          return
        }
        video.value.onloadedmetadata = () => {
          console.log('비디오 실제 해상도:', video.value.videoWidth, video.value.videoHeight)
          const width = video.value.videoWidth
          const height = video.value.videoHeight
          canvas.value.width = width
          canvas.value.height = height
          canvas.value.style.zIndex = '100'
          canvas.value.style.position = 'absolute'
          canvas.value.style.top = '0'
          canvas.value.style.left = '0'
          canvas.value.style.width = '100%'
          canvas.value.style.height = '100%'
          canvas.value.style.pointerEvents = 'none'
          canvas.value.style.background = 'transparent'
          console.log(`Canvas 해상도 동기화 완료: ${width}x${height}`)
          resolve()
        }
        video.value.onerror = reject
      })
    } catch (error) {
      console.error('비디오 초기화 중 오류:', error)
      throw error
    }
    console.log('=== PoseMiniWidget 컴포넌트 마운트 완료 ===')
  } catch (error) {
    console.error('PoseMiniWidget 초기화 중 오류 발생:', error)
    alert('카메라 초기화 중 오류가 발생했습니다. 페이지를 새로고침하거나 카메라 권한을 확인해주세요.')
  }
  updateInterval = setInterval(() => {
    const currentData = {}
    faceStates.value.forEach((state, index) => {
      const id = props.intervieweeIds[index]
      // === 표정 카운트 누적 (내부 키로 변환) ===
      const converted = {}
      Object.entries(state.expression).forEach(([k, v]) => {
        if (toInternalLabel[k]) converted[toInternalLabel[k]] = v
      })
      converted.timestamp = Date.now()
      accumulatedNonverbalData.value[id].facial_expression_history.push(converted)
      Object.keys(state.expression).forEach(key => { state.expression[key] = 0 })
      state.expressionTotal = 0
      const acc = accumulatedNonverbalData.value[id]
      const expHistory = acc?.facial_expression_history || []
      const sumExp = expHistory.reduce((acc, cur) => {
        acc.smile += cur.smile || 0
        acc.neutral += cur.neutral || 0
        acc.frown += cur.frown || 0
        acc.angry += cur.angry || 0
        return acc
      }, { smile: 0, neutral: 0, frown: 0, angry: 0 })
      const postureHistory = acc?.posture_history || []
      const sumPosture = postureHistory.reduce((acc, cur) => {
        acc.upright += cur.upright || 0
        acc.leaning += cur.leaning || 0
        acc.slouching += cur.slouching || 0
        return acc
      }, { upright: 0, leaning: 0, slouching: 0 })
      const lastTimestamp = expHistory.length > 0 ? expHistory[expHistory.length-1].timestamp : Date.now()
      currentData[id] = {
        posture: sumPosture,
        facial_expression: sumExp,
        gaze: 0, // placeholder
        gesture: 0, // placeholder
        timestamp: lastTimestamp
      }
    })
    nonverbalData.value = currentData
    emit('updateNonverbalData', currentData)
  }, 1000)
})

onBeforeUnmount(() => {
  active = false
  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = null
  }
  if (video.value?.srcObject) {
    video.value.srcObject.getTracks().forEach(track => track.stop())
  }
  Object.entries(recorderMap.value).forEach(([id, recorderData]) => {
    if (recorderData.mediaRecorder && recorderData.mediaRecorder.state !== 'inactive') {
      console.log(`[강제 종료] 면접자 ID ${id}의 녹음을 강제 종료합니다.`)
      try {
        recorderData.mediaRecorder.stop()
      } catch (error) {
        console.warn(`[리소스 정리] 면접자 ID ${id}의 녹음 종료 중 오류:`, error.message)
      }
    }
    if (recorderData.stream) {
      recorderData.stream.getTracks().forEach(track => { track.stop() })
    }
  })
  recorderMap.value = {}
  console.log('[컴포넌트 정리 완료] PoseMiniWidget 컴포넌트가 정리되었습니다.')
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>
