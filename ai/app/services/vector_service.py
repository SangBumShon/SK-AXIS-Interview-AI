# from weaviate import Client
# import os
#
#
# # Weaviate 클라이언트 초기화
# def get_weaviate_client():
#     client = Client("http://localhost:8080")  # 도커 기반 기본 포트
#     return client
#
#
# # 키워드 검색 함수
# def search_related_keywords(query: str, top_k: int = 5):
#     client = get_weaviate_client()
#     result = client.query.get("HRKeyword", ["term", "description"]) \
#         .with_near_text({"concepts": [query]}) \
#         .with_limit(top_k) \
#         .do()
#
#     hits = result['data']['Get']['HRKeyword']
#     return hits