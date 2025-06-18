import pandas as pd
import json
import sys
import os
import re
from typing import List, Set
import requests
import io

# 상위 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GPT_API_KEY, OUTPUT_DIR, CONTENTS_FILE, REPLIES_FILE

class BadWordFilter:
    def __init__(self):
        # 악성댓글 데이터셋 로드
        self.malicious_dataset = self._load_malicious_dataset()
    
    def _load_malicious_dataset(self) -> pd.DataFrame:
        """악성댓글 데이터셋 로드"""
        try:
            # GitHub raw URL에서 데이터셋 다운로드
            url = "https://raw.githubusercontent.com/ZIZUN/korean-malicious-comments-dataset/master/Dataset.csv"
            response = requests.get(url)
            df = pd.read_csv(io.StringIO(response.text))
            return df
        except Exception as e:
            print(f"악성댓글 데이터셋 로드 실패: {str(e)}")
            return pd.DataFrame()
    
    def contains_bad_word(self, text: str) -> bool:
        """악성댓글 포함 여부 확인"""
        if self.malicious_dataset.empty:
            return False
            
        # 악성댓글 데이터셋과 유사도 체크
        for _, row in self.malicious_dataset.iterrows():
            if row['label'] == 0:  # 악성댓글인 경우
                if text in row['text'] or row['text'] in text:
                    return True
        return False
    
    def filter_contents(self, csv_path: str, output_path: str = None) -> pd.DataFrame:
        """CSV 파일에서 악성댓글이 포함된 게시물 필터링"""
        try:
            df = pd.read_csv(csv_path)
            
            # 악성댓글 필터링
            df['contains_bad_word'] = df['content'].apply(self.contains_bad_word)
            filtered_df = df[~df['contains_bad_word']]
            
            # 결과 저장
            if output_path:
                filtered_df.to_csv(output_path, index=False)
            
            return filtered_df
            
        except Exception as e:
            print(f"Error processing CSV file: {str(e)}")
            return pd.DataFrame()

if __name__ == "__main__":
    # 필터 인스턴스 생성
    filter = BadWordFilter()
    
    # CSV 파일 필터링
    filtered_df = filter.filter_contents(
        CONTENTS_FILE,
        f"{OUTPUT_DIR}/filtered_contents.csv"
    )
    print(f"✅ 필터링 완료: {OUTPUT_DIR}/filtered_contents.csv 파일 저장됨")
