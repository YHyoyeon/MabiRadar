import openai
import pandas as pd
import json
import sys
import os

# 비용 문제로 인해 주석처리

# 상위 디렉토리를 파이썬 경로에 추가
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from config import GPT_API_KEY, OUTPUT_DIR, CONTENTS_FILE, REPLIES_FILE

# client = openai.OpenAI(api_key=GPT_API_KEY)

# df = pd.read_csv(CONTENTS_FILE)
# contents = df["content"].tolist()

# prompt = "다음은 커뮤니티 게시글입니다. 각 게시글이 음란하거나 심한 욕설이 포함된 부적절한 내용인지 판단해 주세요.\n"
# prompt += "응답은 JSON 배열이며 true (부적절함) 또는 false (정상)로 구성됩니다. 총 67개입니다.\n\n"

# for i, content in enumerate(contents):
#     prompt += f"{i+1}. {content}\n"

# prompt += "\n결과:"

# response = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": prompt}],
#     temperature=0,
# )

# result_text = response.choices[0].message.content
# filtered_flags = json.loads(result_text)

# df["is_inappropriate"] = filtered_flags
# df_filtered = df[df["is_inappropriate"] == False]  # 정상 게시글만 남김

# df_filtered.to_csv(f"{OUTPUT_DIR}/filtered_contents.csv", index=False)
# print(f"✅ 필터링 완료: {OUTPUT_DIR}/filtered_contents.csv 파일 저장됨")
