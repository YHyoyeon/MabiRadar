import openai
import pandas as pd
import json
import sys
import os
from typing import List
import time
from datetime import datetime

# 상위 디렉토리를 파이썬 경로에 추가
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from config import GPT_API_KEY

# openai.api_key = GPT_API_KEY

# def process_batch(contents: List[str], batch_size: int = 20) -> List[bool]:
#     """게시글을 배치 단위로 처리하는 함수"""
#     results = []
    
#     for i in range(0, len(contents), batch_size):
#         batch = contents[i:i + batch_size]
#         prompt = "다음은 커뮤니티 게시글입니다. 각 게시글이 음란하거나 심한 욕설이 포함된 부적절한 내용인지 판단해 주세요.\n"
#         prompt += f"응답은 JSON 배열이며 true (부적절함) 또는 false (정상)로 구성됩니다. 총 {len(batch)}개입니다.\n\n"
        
#         for j, content in enumerate(batch):
#             prompt += f"{j+1}. {content}\n"
        
#         prompt += "\n결과:"
        
#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-4",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0,
#             )
            
#             result_text = response["choices"][0]["message"]["content"]
#             batch_results = json.loads(result_text)
#             results.extend(batch_results)
            
#             # API 호출 제한을 위한 대기
#             time.sleep(1)
            
#         except Exception as e:
#             print(f"배치 처리 중 오류 발생: {str(e)}")
#             # 오류 발생 시 해당 배치의 모든 게시글을 정상으로 처리
#             results.extend([False] * len(batch))
    
#     return results

# def main():
#     try:
#         # CSV 파일 읽기
#         df = pd.read_csv("contents.csv")
#         contents = df["content"].tolist()
        
#         # 배치 처리로 필터링
#         filtered_flags = process_batch(contents)
        
#         # 결과 저장
#         df["is_inappropriate"] = filtered_flags
#         df_filtered = df[df["is_inappropriate"] == False]  # 정상 게시글만 남김
        
#         # 파일명에 타임스탬프 추가
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         output_filename = f"filtered_contents_{timestamp}.csv"
        
#         df_filtered.to_csv(output_filename, index=False)
#         print(f"✅ 필터링 완료: {output_filename} 파일 저장됨")
        
#     except FileNotFoundError:
#         print("❌ contents.csv 파일을 찾을 수 없습니다.")
#     except Exception as e:
#         print(f"❌ 처리 중 오류 발생: {str(e)}")

# if __name__ == "__main__":
#     main() 