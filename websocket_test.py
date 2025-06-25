import asyncio
import websockets
import json

async def handler(websocket, path):
    print("클라이언트 연결됨")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print("수신된 JSON:", data)
                # 응답 필요시:
                # await websocket.send(json.dumps({"result": "ok"}))
            except json.JSONDecodeError:
                print("잘못된 JSON:", message)
    except websockets.ConnectionClosed:
        print("클라이언트 연결 종료")

start_server = websockets.serve(handler, '0.0.0.0', 9000)
print("WebSocket 서버가 9000번 포트에서 대기 중...")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
