from datetime import datetime, timedelta
from typing import Final
import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드 (프로젝트 루트 디렉토리 기준)
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')

# 넥슨 마비노기 모바일 공지사항 URL
BASE_URL: Final[str] = "https://mabinogimobile.nexon.com"
NOTICE_URL: Final[str] = f"{BASE_URL}/News/Notice"
NOTICE_LIST_URL: Final[str] = f"{NOTICE_URL}?headlineId=&directionType=DEFAULT&pageno=1"

# 크롤링 설정
END_DATE: Final[datetime] = datetime.now() - timedelta(days=1)
SLEEP_TIME: Final[float] = 1.0
MAX_RETRIES: Final[int] = 2

# 파일 경로
OUTPUT_DIR: Final[str] = "nexon_crawler/output"
CONTENTS_FILE: Final[str] = f"{OUTPUT_DIR}/contents.csv"
REPLIES_FILE: Final[str] = f"{OUTPUT_DIR}/replies.csv"

# 디버그 설정
DEBUG_DIR: Final[str] = "nexon_crawler/debug"

# API 설정
GPT_API_KEY: Final[str] = os.getenv("GPT_API_KEY", "")  # GPT API 키 (필요시 사용) 