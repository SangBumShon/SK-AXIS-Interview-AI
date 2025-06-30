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

// 부모 컴포넌트에서 접근 가능하도록 누적 데이터 노출
defineExpose({
  getAccumulatedNonverbalData: () => accumulatedNonverbalData.value,
  getCurrentNonverbalData: () => nonverbalData.value,
  stopDetection: () => {
    active = false
    console.log('[감지 중단] PoseMiniWidget 감지가 중단되었습니다.')
  }
})

// 녹음 관련 상태 - 면접자별 개별 관리
const recorderMap = ref({})  // { [id]: { mediaRecorder, audioChunks, stream } }
const MOUTH_CLOSED_THRESHOLD = 5000 // 5초

const video = ref(null)
const canvas = ref(null)
let active = true

// 얼굴표정 관련 상수
const expList = ['미소', '무표정', '울상', '찡그림']
const expKorean = {
  happy: '미소', sad: '울상', angry: '찡그림',
  neutral: '무표정', disgusted: '불쾌'
}

// 각 면접자별 상태 관리
const faceStates = ref([])

// 비언어적 데이터 저장소
const nonverbalData = ref({})

// 면접 종료 시 누적 데이터 저장소
const accumulatedNonverbalData = ref({})  // { [id]: { facial_expression_history: [], posture_history: [], ... } }

// 1초마다 데이터 업데이트 및 전송
let updateInterval = null

// 면접자 이름이 변경될 때마다 상태 초기화
watch(() => props.intervieweeNames, (newNames) => {
  faceStates.value = newNames.map((name, index) => {
    const id = props.intervieweeIds[index]
    nonverbalData.value[id] = {
      posture: { upright: 0, leaning: 0, slouching: 0 },
      facial_expression: { smile: 0, neutral: 0, frown: 0, angry: 0 },
      gaze: 0,
      gesture: 0,
      timestamp: Date.now()
    }
    
    // 누적 데이터 초기화
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
      expressionTotal: 0, // 총 프레임 수
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
    
    // WebM 형식으로 녹음 설정
    const mimeType = 'audio/webm'
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      console.error(`[녹음 시작 실패] ${mimeType} 형식이 지원되지 않습니다.`)
      return
    }
    
    const recorder = new MediaRecorder(stream, {
      mimeType: mimeType
    })
    const audioChunks = []
    
    recorder.ondataavailable = (event) => {
      audioChunks.push(event.data)
    }
    
    recorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: mimeType })
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const fileName = `${state.id}_${timestamp}.webm`
      
      const formData = new FormData()
      formData.append('audio', audioBlob, fileName)
      formData.append('interviewee_id', state.id.toString())
      
      try {
        const response = await fetch('http//:localhost:8000/api/v1/stt/upload', {
          method: 'POST',
          body: formData
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(`Upload failed: ${response.status} ${errorData.detail || response.statusText}`)
        }
        
        const result = await response.json()
        console.log(`[업로드 성공] ${state.name}님의 녹음 파일이 성공적으로 업로드되었습니다.`)
        state.isRecording = false
      } catch (error) {
        console.error(`[업로드 실패] ${state.name}님의 녹음 파일 업로드 중 오류 발생:`, error.message)
        state.isRecording = false
      } finally {
        if (recorder && recorder.stream) {
          recorder.stream.getTracks().forEach(track => {
            track.stop()
          })
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

onMounted(async () => {
  console.log('=== PoseMiniWidget 컴포넌트 마운트 시작 ===')

  try {
    console.log('face-api.js 모델 로딩 시작...')
    
    // 모델 로딩 전 상태 확인
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

    // 비디오 엘리먼트 초기화
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
      
      // 비디오 메타데이터 로드 완료 후 캔버스 크기 동기화
      await new Promise((resolve, reject) => {
        if (!video.value) {
          reject(new Error('비디오 엘리먼트가 없습니다.'))
          return
        }
        video.value.onloadedmetadata = () => {
          console.log('비디오 실제 해상도:', video.value.videoWidth, video.value.videoHeight)
          // 💡 실제 비디오 해상도를 기반으로 canvas 해상도 설정 (스케일링 문제 해결)
          const width = video.value.videoWidth
          const height = video.value.videoHeight
          canvas.value.width = width
          canvas.value.height = height
          
          // Canvas 스타일 동적 설정
          canvas.value.style.zIndex = '100'
          canvas.value.style.position = 'absolute'
          canvas.value.style.top = '0'
          canvas.value.style.left = '0'
          canvas.value.style.width = '100%'
          canvas.value.style.height = '100%'
          canvas.value.style.pointerEvents = 'none'
          canvas.value.style.background = 'transparent'
          
          console.log(`Canvas 해상도 동기화 완료: ${width}x${height}`)
          
          // 테스트용 빨간 사각형 그리기
          const ctx = canvas.value.getContext('2d')
          ctx.fillStyle = 'red'
          ctx.fillRect(20, 20, 50, 50)
          
          resolve()
        }
        video.value.onerror = reject
      })

    } catch (error) {
      console.error('비디오 초기화 중 오류:', error)
      throw error
    }

    const analyze = async () => {
      if (!active) {
        return
      }

      try {
        const ctx = canvas.value.getContext('2d')
        const width = canvas.value.width
        const height = canvas.value.height
        
        ctx.clearRect(0, 0, width, height)
        ctx.drawImage(video.value, 0, 0, width, height)

        // 테스트용 점 찍기 (계속 그리기)
        ctx.fillStyle = 'red'
        ctx.fillRect(10, 10, 10, 10)
        ctx.fillRect(width - 20, height - 20, 10, 10) // 우하단에도 점 찍기

        let detections = await faceapi.detectAllFaces(video.value, new faceapi.TinyFaceDetectorOptions())
          .withFaceLandmarks()
          .withFaceExpressions()
        
        // 면접자 수에 따라 감지된 얼굴 수 제한
        detections = detections.slice(0, props.intervieweeNames.length)
        detections.sort((a, b) => a.detection.box.x - b.detection.box.x)

        // 얼굴 랜드마크/박스 시각화 및 상태 업데이트
        for (let k = 0; k < detections.length; k++) {
          const det = detections[k]
          const color = k === 0 ? 'lime' : k === 1 ? 'yellow' : 'aqua'
          
          // faceStates 안전성 체크
          if (!faceStates.value[k]) {
            continue
          }
          const faceState = faceStates.value[k]
          
          // 얼굴 랜드마크 시각화
          for (const pt of det.landmarks.positions) {
            ctx.beginPath()
            ctx.arc(pt.x, pt.y, 2.2, 0, 2 * Math.PI)
            ctx.fillStyle = color
            ctx.fill()
          }
          
          // 얼굴 박스 시각화
          const box = det.detection.box
          ctx.strokeStyle = color
          ctx.lineWidth = 2
          ctx.strokeRect(
            box.x,
            box.y,
            box.width,
            box.height
          )
          
          // 면접자 이름 표시
          ctx.font = 'bold 20px sans-serif'
          ctx.fillStyle = color
          ctx.fillText(
            faceState.name,
            box.x,
            box.y - 8
          )

          // 입벌림 감지 및 녹음 처리
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

          // 표정 감지 및 카운트
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

      requestAnimationFrame(analyze)
    }

    analyze()
    console.log('=== PoseMiniWidget 컴포넌트 마운트 완료 ===')

  } catch (error) {
    console.error('PoseMiniWidget 초기화 중 오류 발생:', error)
    // 사용자에게 오류 알림
    alert('카메라 초기화 중 오류가 발생했습니다. 페이지를 새로고침하거나 카메라 권한을 확인해주세요.')
  }

  // 1초마다 데이터 업데이트 및 전송
  updateInterval = setInterval(() => {
    const currentData = {}
    faceStates.value.forEach((state, index) => {
      const id = props.intervieweeIds[index]
      // 누적값 합산
      const acc = accumulatedNonverbalData.value[id]
      // 표정 누적 합산
      const expHistory = acc?.facial_expression_history || []
      const sumExp = expHistory.reduce((acc, cur) => {
        acc.smile += cur.smile || 0
        acc.neutral += cur.neutral || 0
        acc.frown += cur.frown || 0
        acc.angry += cur.angry || 0
        return acc
      }, { smile: 0, neutral: 0, frown: 0, angry: 0 })
      // 자세 누적 합산
      const postureHistory = acc?.posture_history || []
      const sumPosture = postureHistory.reduce((acc, cur) => {
        acc.upright += cur.upright || 0
        acc.leaning += cur.leaning || 0
        acc.slouching += cur.slouching || 0
        return acc
      }, { upright: 0, leaning: 0, slouching: 0 })
      // 마지막 timestamp
      const lastTimestamp = expHistory.length > 0 ? expHistory[expHistory.length-1].timestamp : Date.now()
      currentData[id] = {
        posture: sumPosture,
        facial_expression: sumExp,
        gaze: 0, // 누적 시선/제스처 필요시 추가
        gesture: 0,
        timestamp: lastTimestamp
      }
    })
    nonverbalData.value = currentData
    emit('updateNonverbalData', currentData)
  }, 1000)
})

onBeforeUnmount(() => {
  active = false
  console.log('[컴포넌트 정리] PoseMiniWidget 컴포넌트를 정리합니다...')
  
  // 모든 면접자의 녹음 중지 및 리소스 정리
  Object.entries(recorderMap.value).forEach(([id, recorderData]) => {
    if (recorderData.mediaRecorder && recorderData.mediaRecorder.state !== 'inactive') {
      console.log(`[강제 종료] 면접자 ID ${id}의 녹음을 강제 종료합니다.`)
      try {
        recorderData.mediaRecorder.stop()
      } catch (error) {
        console.warn(`[리소스 정리] 면접자 ID ${id}의 녹음 종료 중 오류:`, error.message)
      }
    }
    
    // 스트림 리소스 정리
    if (recorderData.stream) {
      recorderData.stream.getTracks().forEach(track => {
        track.stop()
      })
    }
  })
  
  // recorderMap 초기화
  recorderMap.value = {}
  
  console.log('[컴포넌트 정리 완료] PoseMiniWidget 컴포넌트가 정리되었습니다.')

  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>
