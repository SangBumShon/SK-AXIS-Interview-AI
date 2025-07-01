from fastapi import APIRouter

router = APIRouter()

@router.get("/interviews/simple")
async def get_interviews_simple():
    return {
        "data": [
            {
                "interviewId": 3,
                "intervieweeId": 3,
                "name": "홍길동",
                "scheduledAt": [2025, 6, 30, 9, 0],
                "status": "SCHEDULED",
                "score": None,
                "interviewers": "면접관A,면접관B",
                "roomNo": "회의실A",
                "comment": None,
                "createdAt": [2025, 6, 30, 10, 24, 34]
            }
        ]
    } 