from datetime import datetime, timedelta
from typing import Final
import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드 (프로젝트 루트 디렉토리 기준)
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')

# 갤러리 설정
GALLERY_TYPE: Final[str] = "mgallery"
TARGET_GALLERY: Final[str] = "mabinogimobile"
BASE_URL: Final[str] = "https://gall.dcinside.com"

# 크롤링 설정
END_DATE: Final[datetime] = datetime.now() - timedelta(minutes=3)

# 크롤링 옵션
SLEEP_TIME: Final[float] = 1.0
MAX_RETRIES: Final[int] = 3

# 파일 경로
OUTPUT_DIR: Final[str] = "dc_crawler/output"
CONTENTS_FILE: Final[str] = f"{OUTPUT_DIR}/contents.csv"
REPLIES_FILE: Final[str] = f"{OUTPUT_DIR}/replies.csv"

# 필터링 설정
GPT_API_KEY: Final[str] = os.getenv("GPT_API_KEY", "")