import openai
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 불러오기
openai.api_key = os.getenv("OPENAI_API_KEY")

#텍스트 입력 → GPT 응답 받기
def get_gpt_response(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4",  #3.5터보로 바꿔서 사용해도 OK
        messages=[
            {"role": "system",
             "content": "당신은 친절하고 공손한 음성 비서입니다. 모르는 질문이나 이상한 말에는 '죄송해요, 이해하지 못했어요. 다시 한번 더 말씀해주시겠어요?'라고 대답하세요."},
            {"role": "user", "content": user_input}

        ],
        temperature=0.8  #자연스러움 조절=>0부터 1까지 조절할 수 있음
    )

    reply = response.choices[0].message['content']
    return reply

print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")

# #기본 테스트
# if __name__ == "__main__":
#     stt_output = "졸업할 수 있겠지?"
#     answer = get_gpt_response(stt_output)
#     print("🙋 나:" , stt_output)
#     print("🤖 GPT 응답:", answer)
#     print("-" * 40)

# #여러 문장을 한꺼번에 테스트
# questions = [
#     "안녕, 반가워.",
#     "오늘 할 일 추천해줘!",
#     "오늘 서울에서 벚꽃 보러갈 만한 곳이 어디 있을까?",
#     "서울에서 10000원으로 장보고 싶은데 어떤 걸 구매할까?",
# ]

# for q in questions:
#     print(f"🙋 사용자: {q}")
#     print(f"🤖 나만의 음성 비서: {get_gpt_response(q)}")
#     print("-" * 40)