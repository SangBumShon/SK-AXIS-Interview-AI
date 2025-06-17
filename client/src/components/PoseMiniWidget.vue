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
import { ref, onMounted, onBeforeUnmount, defineProps, watch, defineEmits } from 'vue'
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

// 녹음 관련 상태
const mediaRecorder = ref(null)
const audioChunks = ref([])
const MOUTH_CLOSED_THRESHOLD = 3000 // 3초

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
    return {
      name,
      id,
      speaking: false,
      mouthClosedStartTime: null,
      isRecording: false,
      expression: Object.fromEntries(expList.map(e => [e, 0])),
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
  return mouthOpen > 20 && mouthWidth > 25
}

async function startRecording(personIndex) {
  console.log('startRecording 함수 호출됨, personIndex:', personIndex)
  const state = faceStates.value[personIndex]
  console.log('현재 faceState:', state)
  
  if (state.isRecording) {
    console.log(`[녹음 시작 실패] ${state.name}님의 녹음이 이미 진행 중입니다.`)
    return
  }
  
  try {
    console.log(`[녹음 준비] ${state.name}님의 녹음을 시작합니다...`)
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    console.log(`[녹음 준비 완료] ${state.name}님의 오디오 스트림이 준비되었습니다.`)
    
    // WebM 형식으로 녹음 설정
    const mimeType = 'audio/webm'
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      console.error(`[녹음 시작 실패] ${mimeType} 형식이 지원되지 않습니다.`)
      return
    }
    
    mediaRecorder.value = new MediaRecorder(stream, {
      mimeType: mimeType
    })
    audioChunks.value = []
    
    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
      console.log(`[녹음 데이터] ${state.name}님의 녹음 데이터 청크 수신 (${audioChunks.value.length}개)`)
    }
    
    mediaRecorder.value.onstop = async () => {
      console.log(`[녹음 종료] ${state.name}님의 녹음이 종료되었습니다. 파일 변환 중...`)
      const audioBlob = new Blob(audioChunks.value, { type: mimeType })
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const fileName = `${state.id}_${timestamp}.webm`
      
      console.log(`[파일 생성] ${fileName} (${(audioBlob.size / 1024 / 1024).toFixed(2)}MB)`)
      
      const formData = new FormData()
      formData.append('audio', audioBlob, fileName)
      formData.append('interviewee_id', state.id)
      
      try {
        console.log(`[업로드 시작] ${state.name}님의 녹음 파일을 서버로 전송합니다...`)
        const response = await fetch('/api/v1/interview/stt/upload', {
          method: 'POST',
          body: formData
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(`Upload failed: ${response.status} ${errorData.detail || response.statusText}`)
        }
        
        const result = await response.json()
        console.log(`[업로드 성공] ${state.name}님의 녹음 파일이 성공적으로 업로드되었습니다.`, result)
        state.isRecording = false
      } catch (error) {
        console.error(`[업로드 실패] ${state.name}님의 녹음 파일 업로드 중 오류 발생:`, error.message)
        state.isRecording = false
      } finally {
        if (mediaRecorder.value && mediaRecorder.value.stream) {
          mediaRecorder.value.stream.getTracks().forEach(track => {
            track.stop()
            console.log(`[리소스 정리] ${state.name}님의 오디오 스트림 트랙이 정리되었습니다.`)
          })
        }
      }
    }
    
    mediaRecorder.value.start()
    state.isRecording = true
    console.log(`[녹음 시작] ${state.name}님의 녹음이 시작되었습니다.`)
  } catch (error) {
    console.error(`[녹음 시작 실패] ${state.name}님의 녹음 시작 중 오류 발생:`, error.message)
  }
}

function stopRecording(personIndex) {
  console.log('stopRecording 함수 호출됨, personIndex:', personIndex)
  const state = faceStates.value[personIndex]
  console.log('현재 faceState:', state)
  
  if (!state.isRecording) {
    console.log(`[녹음 종료 실패] ${state.name}님의 녹음이 진행 중이 아닙니다.`)
    return
  }
  
  if (!mediaRecorder.value) {
    console.error(`[녹음 종료 실패] ${state.name}님의 MediaRecorder가 초기화되지 않았습니다.`)
    return
  }
  
  try {
    mediaRecorder.value.stop()
    state.isRecording = false
    console.log(`[녹음 종료 요청] ${state.name}님의 녹음 종료가 요청되었습니다.`)
  } catch (error) {
    console.error(`[녹음 종료 실패] ${state.name}님의 녹음 종료 중 오류 발생:`, error.message)
  }
}

onMounted(async () => {
  console.log('=== PoseMiniWidget 컴포넌트 마운트 시작 ===')
  console.log('면접자 목록:', props.intervieweeNames)
  console.log('현재 faceStates:', faceStates.value)

  try {
    console.log('face-api.js 모델 로딩 시작...')
    
    // 모델 로딩 전 상태 확인
    if (!faceapi.nets.tinyFaceDetector.isLoaded) {
      console.log('tinyFaceDetector 모델 로드 시작')
      await faceapi.nets.tinyFaceDetector.loadFromUri('/models/tiny_face_detector')
      console.log('tinyFaceDetector 모델 로드 완료')
    } else {
      console.log('tinyFaceDetector 모델이 이미 로드되어 있음')
    }
    
    if (!faceapi.nets.faceLandmark68Net.isLoaded) {
      console.log('faceLandmark68Net 모델 로드 시작')
      await faceapi.nets.faceLandmark68Net.loadFromUri('/models/face_landmark_68')
      console.log('faceLandmark68Net 모델 로드 완료')
    } else {
      console.log('faceLandmark68Net 모델이 이미 로드되어 있음')
    }
    
    if (!faceapi.nets.faceExpressionNet.isLoaded) {
      console.log('faceExpressionNet 모델 로드 시작')
      await faceapi.nets.faceExpressionNet.loadFromUri('/models/face_expression')
      console.log('faceExpressionNet 모델 로드 완료')
    } else {
      console.log('faceExpressionNet 모델이 이미 로드되어 있음')
    }
    
    console.log('모든 face-api.js 모델 로딩 완료')

    // 비디오 엘리먼트 초기화
    try {
      while (!video.value) {
        console.log('비디오 엘리먼트 대기 중...')
        await new Promise(r => setTimeout(r, 100))  // requestAnimationFrame 대신 setTimeout 사용
      }
      console.log('비디오 엘리먼트 준비 완료')

      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: 1280, 
          height: 720,
          facingMode: 'user'  // 전면 카메라 우선 사용
        } 
      })
      console.log('카메라 스트림 획득 완료')
      
      video.value.srcObject = stream
      await new Promise((resolve, reject) => {
        if (!video.value) {
          reject(new Error('비디오 엘리먼트가 없습니다.'))
          return
        }
        video.value.onloadedmetadata = resolve
        video.value.onerror = reject
      })
      console.log('비디오 메타데이터 로드 완료')

    } catch (error) {
      console.error('비디오 초기화 중 오류:', error)
      throw error  // 상위에서 처리하도록 에러 전파
    }

    const analyze = async () => {
      if (!active) {
        console.log('analyze 함수 비활성화됨')
        return
      }

      try {
        const ctx = canvas.value.getContext('2d')
        ctx.clearRect(0, 0, 1280, 720)
        ctx.drawImage(video.value, 0, 0, 1280, 720)

        let detections = await faceapi.detectAllFaces(video.value, new faceapi.TinyFaceDetectorOptions())
          .withFaceLandmarks()
          .withFaceExpressions()
        
        // 면접자 수에 따라 감지된 얼굴 수 제한
        detections = detections.slice(0, props.intervieweeNames.length)
        detections.sort((a, b) => a.detection.box.x - b.detection.box.x)

        if (detections.length > 0) {
          console.log(`감지된 얼굴 수: ${detections.length}`)
        }

        // 얼굴 랜드마크/박스 시각화 및 상태 업데이트
        for (let k = 0; k < detections.length; k++) {
          const det = detections[k]
          const color = k === 0 ? 'lime' : k === 1 ? 'yellow' : 'aqua'
          
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
          ctx.strokeRect(box.x, box.y, box.width, box.height)
          
          // 면접자 이름 표시
          ctx.font = 'bold 20px sans-serif'
          ctx.fillStyle = color
          ctx.fillText(faceStates.value[k].name, box.x, box.y - 8)

          // 입벌림 감지 및 녹음 처리
          const isSpeaking = detectSpeaking(det.landmarks)
          const faceState = faceStates.value[k]
          
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
              console.log(`[입벌림 종료 감지] ${faceState.name}님이 말하기를 멈췄습니다. 3초 대기 중...`)
            } else if (Date.now() - faceState.mouthClosedStartTime >= MOUTH_CLOSED_THRESHOLD) {
              console.log(`[녹음 종료 조건 충족] ${faceState.name}님이 3초 동안 말하지 않았습니다.`)
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
            faceState.lastExpression = expKor
          }
        }

      } catch (error) {
        console.error('analyze 함수 실행 중 오류:', error)
      }

      requestAnimationFrame(analyze)
    }

    console.log('analyze 함수 시작')
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
      currentData[id] = {
        posture: { upright: 0, leaning: 0, slouching: 0 },  // 자세 데이터는 추후 추가
        facial_expression: {
          smile: state.expression['미소'] || 0,
          neutral: state.expression['무표정'] || 0,
          frown: state.expression['울상'] || 0,
          angry: state.expression['찡그림'] || 0
        },
        gaze: 0,  // 시선 데이터는 추후 추가
        gesture: 0,  // 제스처 데이터는 추후 추가
        timestamp: Date.now()
      }
    })
    nonverbalData.value = currentData
    emit('updateNonverbalData', currentData)
  }, 1000)
})

onBeforeUnmount(() => {
  active = false
  console.log('[컴포넌트 정리] PoseMiniWidget 컴포넌트를 정리합니다...')
  
  // 모든 면접자의 녹음 중지
  faceStates.value.forEach((state, index) => {
    if (state.isRecording) {
      console.log(`[강제 종료] ${state.name}님의 녹음을 강제 종료합니다.`)
      stopRecording(index)
    }
  })
  
  console.log('[컴포넌트 정리 완료] PoseMiniWidget 컴포넌트가 정리되었습니다.')

  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>
