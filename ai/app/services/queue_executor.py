from collections import defaultdict, deque
from typing import Callable, Coroutine, Any, Dict
import asyncio

# 인터뷰이별 큐와 실행 상태 저장소
INTERVIEW_TASK_QUEUES: Dict[int, deque] = defaultdict(deque)
INTERVIEW_QUEUE_RUNNING: Dict[int, bool] = defaultdict(bool)

async def enqueue_task(interviewee_id: int, coro: Callable[[], Coroutine[Any, Any, None]]):
    INTERVIEW_TASK_QUEUES[interviewee_id].append(coro)

    if not INTERVIEW_QUEUE_RUNNING[interviewee_id]:
        INTERVIEW_QUEUE_RUNNING[interviewee_id] = True
        asyncio.create_task(_process_queue(interviewee_id))

async def _process_queue(interviewee_id: int):
    while INTERVIEW_TASK_QUEUES[interviewee_id]:
        task = INTERVIEW_TASK_QUEUES[interviewee_id].popleft()
        try:
            await task()
        except Exception as e:
            print(f"[QueueExecutor] ❌ Error for {interviewee_id}: {e}")
    INTERVIEW_QUEUE_RUNNING[interviewee_id] = False
