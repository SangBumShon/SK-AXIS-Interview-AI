# app/services/interview/question_matcher.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# (면접 시작 시, Spring Boot에서 내려받은 “5개 대표 질문”을 이 리스트에 넣어 주세요.)
REP_QUESTIONS = [
    "자신의 장점을 말씀해 주세요.",
    "팀으로 일할 때 중요하게 생각하는 점은?",
    "본인의 단점은 무엇인가요?",
    "지원 동기가 궁금합니다.",
    "자기소개서에서 언급한 경험을 더 자세히 설명해 주세요."
]

# TF-IDF 벡터라이저 초기화(앱 시작 시 한 번만 실행)
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words=None,       # ⬅️ "korean" 대신 None으로 설정
    ngram_range=(1, 2)
)
rep_tfidf = vectorizer.fit_transform(REP_QUESTIONS)  # shape = (5, vocab_size)

def match_representative_question(stt_text: str, threshold: float = 0.8) -> int | None:
    """
    TF-IDF 기반 대표질문 매칭
    - stt_text를 벡터라이저에 넣어 TF-IDF 벡터화
    - 코사인 유사도 계산 후, 최대 유사도가 threshold 이상이면 그 인덱스 반환
    - 아니면 None 반환(=꼬리질문)
    """
    query_vec = vectorizer.transform([stt_text])  # shape = (1, vocab_size)
    sims = cosine_similarity(query_vec, rep_tfidf).flatten()  # shape = (5,)
    best_idx = int(sims.argmax())
    best_score = float(sims[best_idx])

    if best_score >= threshold:
        return best_idx  # 0~4 사이의 인덱스
    return None
