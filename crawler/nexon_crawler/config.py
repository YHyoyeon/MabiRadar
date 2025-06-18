from datetime import datetime, timedelta
from typing import Final
import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드 (프로젝트 루트 디렉토리 기준)
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')

# 넥슨 마비노기 모바일 공지사항 URL
BASE_URL: Final[str] = "https://mabinogimobile.nexon.com"
NOTICE_LIST_URL: Final[str] = f"{BASE_URL}/News/Notice?headlineId=&directionType=DEFAULT&pageno=1"

# 크롤링 설정
END_DATE: Final[datetime] = datetime.now() - timedelta(days=7)  # 7일 전까지의 게시글 크롤링
SLEEP_TIME: Final[float] = 1.0  # 페이지 요청 간 대기 시간
MAX_RETRIES: Final[int] = 3  # 페이지 로드 실패 시 최대 재시도 횟수

# 파일 경로
OUTPUT_DIR: Final[str] = "nexon_crawler/output"
CONTENTS_FILE: Final[str] = f"{OUTPUT_DIR}/contents.csv"
REPLIES_FILE: Final[str] = f"{OUTPUT_DIR}/replies.csv"

# 디버그 설정
DEBUG_DIR: Final[str] = "nexon_crawler/debug"

# API 설정
GPT_API_KEY: Final[str] = os.getenv("GPT_API_KEY", "")  # GPT API 키 (필요시 사용) 