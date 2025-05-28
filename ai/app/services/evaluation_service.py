from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from dotenv import load_dotenv
import os

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

chat_model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.0,
    openai_api_key=openai_key
)

def evaluate_answer(answer: str) -> str:
    """
    면접 답변을 평가하는 함수
    :param answer: 면접 답변 텍스트
    :return: 평가 결과 텍스트
    """
    prompt = ChatPromptTemplate.from_template(
        "다음 면접 답변을 평가해 주세요:\n\n{answer}\n\n"
        "평가 기준:\n"
        "- 답변의 명확성, 일관성, 관련성\n"
        "- 어휘 사용과 문법적 정확성\n"
        "- 전체적인 표현력과 설득력\n"
        "평가 기준을 0점에서 5점 사이로 점수화하고, 각 기준에 대한 설명을 포함해 주세요.\n"
        "평가 결과를 간결하게 요약해 주세요."
    )

    chain = LLMChain(llm=chat_model, prompt=prompt)
    response = chain.run(answer=answer)

    return response.strip()