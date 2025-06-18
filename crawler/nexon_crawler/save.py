import os
import pandas as pd
from typing import List, Tuple
from config import OUTPUT_DIR, CONTENTS_FILE

def ensure_output_dir() -> None:
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def save_data(posts: List[Tuple]) -> None:
    ensure_output_dir()
    
    # 게시글 저장
    df_posts = pd.DataFrame(posts, columns=["id", "title", "content", "date"])
    df_posts.to_json(CONTENTS_FILE, index=False, force_ascii=False)
    
    print(f"✅ 저장 완료\n- 게시글: {len(posts)}개")
