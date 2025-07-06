"""
SK AXIS AI 면접 비동기 작업 큐 관리자

이 파일은 면접자별 비동기 작업을 순차적으로 처리하는 큐 시스템입니다.
주요 기능:
- 면접자별 독립적인 작업 큐 관리
- 동시성 제어 및 순차 처리 보장
- 비동기 작업 예외 처리 및 로깅

사용 목적:
- STT, 리라이팅, 평가 작업의 순차 처리
- 여러 면접자의 동시 처리 지원
- 작업 충돌 방지 및 안정성 보장

작업 흐름:
1. enqueue_task()로 작업 등록
2. 큐가 비어있으면 _process_queue() 시작
3. 큐의 모든 작업을 순차적으로 실행
4. 예외 발생 시 로깅 후 다음 작업 계속 진행
"""

from collections import defaultdict, deque
from typing import Callable, Coroutine, Any, Dict
import asyncio

# ──────────────── 📦 전역 저장소 ────────────────
# 인터뷰이별 큐와 실행 상태 저장소
INTERVIEW_TASK_QUEUES: Dict[int, deque] = defaultdict(deque)      # 면접자별 작업 큐
INTERVIEW_QUEUE_RUNNING: Dict[int, bool] = defaultdict(bool)      # 면접자별 큐 실행 상태

async def enqueue_task(interviewee_id: int, coro: Callable[[], Coroutine[Any, Any, None]]):
    """
    면접자별 작업 큐에 비동기 작업을 추가합니다.
    
    Args:
        interviewee_id (int): 면접자 고유 ID
        coro (Callable): 실행할 코루틴 함수
        
    Note:
        - 면접자별 독립적인 큐 관리
        - 큐가 실행 중이 아니면 자동으로 처리 시작
        - 동일 면접자의 작업들은 순차적으로 처리됨
        
    Example:
        await enqueue_task(101, lambda: stt_processing(state))
        await enqueue_task(101, lambda: evaluation_processing(state))
    """
    # 면접자별 큐에 작업 추가
    INTERVIEW_TASK_QUEUES[interviewee_id].append(coro)

    # 해당 면접자의 큐가 실행 중이 아니면 처리 시작
    if not INTERVIEW_QUEUE_RUNNING[interviewee_id]:
        INTERVIEW_QUEUE_RUNNING[interviewee_id] = True
        # 백그라운드에서 큐 처리 시작 (await 하지 않음)
        asyncio.create_task(_process_queue(interviewee_id))

async def _process_queue(interviewee_id: int):
    """
    특정 면접자의 작업 큐를 순차적으로 처리합니다.
    
    Args:
        interviewee_id (int): 처리할 면접자 ID
        
    Note:
        - 큐가 비워질 때까지 모든 작업을 순차 실행
        - 예외 발생 시 해당 작업만 실패하고 다음 작업 계속 진행
        - 모든 작업 완료 후 실행 상태를 False로 변경
        
    처리 과정:
    1. 큐에서 작업 하나씩 꺼내기
    2. 작업 실행 (await)
    3. 예외 발생 시 로깅 후 계속 진행
    4. 큐가 비워지면 실행 상태 해제
    """
    # 큐가 비워질 때까지 반복 처리
    while INTERVIEW_TASK_QUEUES[interviewee_id]:
        # 큐에서 다음 작업 가져오기
        task = INTERVIEW_TASK_QUEUES[interviewee_id].popleft()
        
        try:
            # 비동기 작업 실행
            await task()
        except Exception as e:
            # 예외 발생 시 로깅 후 다음 작업 계속 진행
            print(f"[QueueExecutor] ❌ Error for interviewee {interviewee_id}: {e}")
            # 개별 작업 실패가 전체 큐 처리를 중단시키지 않음
    
    # 모든 작업 완료 후 실행 상태 해제
    INTERVIEW_QUEUE_RUNNING[interviewee_id] = False
