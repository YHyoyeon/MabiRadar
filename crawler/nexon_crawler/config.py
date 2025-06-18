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

# 크롤링 설정
SLEEP_TIME: Final[float] = 1.0
MAX_RETRIES: Final[int] = 2

# 파일 경로
OUTPUT_DIR: Final[str] = "nexon_crawler/output"
CONTENTS_FILE: Final[str] = f"{OUTPUT_DIR}/contents.json"

# 디버그 설정
DEBUG_DIR: Final[str] = "nexon_crawler/debug"

# API 설정
GPT_API_KEY: Final[str] = os.getenv("GPT_API_KEY", "")  # GPT API 키 (필요시 사용)

# 디스코드 웹훅 URL 설정
DISCORD_WEBHOOK_URL = "여기에_디스코드_웹훅_URL을_입력하세요"  # 실제 웹훅 URL로 교체 필요 