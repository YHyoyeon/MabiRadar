import os
import pandas as pd
from typing import List, Tuple
from config import OUTPUT_DIR, CONTENTS_FILE, REPLIES_FILE

def ensure_output_dir() -> None:
    # 출력 디렉토리가 없으면 생성합니다.
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

# 게시글과 댓글 데이터를 CSV 파일로 저장합니다.
#    Args:
#         posts: 게시글 데이터 리스트 (id, title, content, date)
#         comments: 댓글 데이터 리스트 (id, reply_id, reply_content, reply_date)
def save_data(posts: List[Tuple], comments: List[Tuple] = []) -> None:
    ensure_output_dir()
    
    # 게시글 저장
    df_posts = pd.DataFrame(posts, columns=["id", "title", "content", "date"])
    df_posts.to_csv(CONTENTS_FILE, index=False, encoding="utf-8")
    
    # 댓글 저장
    df_comments = pd.DataFrame(comments, columns=["id", "reply_id", "reply_content", "reply_date"])
    df_comments.to_csv(REPLIES_FILE, index=False, encoding="utf-8")
    
    print(f"✅ 저장 완료\n- 게시글: {len(posts)}개\n- 댓글: {len(comments)}개")
