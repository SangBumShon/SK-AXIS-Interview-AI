import os
import requests
from dotenv import load_dotenv

load_dotenv()  # .env 파일 불러오기

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def text_to_speech(text: str, output_path: str = "output.mp3"):
    url = "https://api.openai.com/v1/audio/speech"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "tts-1",
        "input": text,
        "voice": "nova"
    }

    response = requests.post(url, headers=headers, json=data)
    print(f"TTS 응답 상태 코드: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"TTS 요청 실패: {response.status_code} - {response.text}")

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path

# if __name__ == "__main__":
#     text = "hello."
#     output = text_to_speech(text, "test_output.mp3")
#     print(f"음성 파일 저장 완료: {output}")
