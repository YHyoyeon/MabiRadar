from datetime import datetime, timedelta
from typing import Final
import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드 (프로젝트 루트 디렉토리 기준)
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')

# 기본 설정
BASE_DIR: Final[Path] = Path(__file__).parent
DEBUG: Final[bool] = os.getenv("DEBUG", "False").lower() == "true"

# 넥슨 마비노기 모바일 공지사항 URL
BASE_URL: Final[str] = "https://mabinogimobile.nexon.com"
NOTICE_URL: Final[str] = f"{BASE_URL}/News/Notice"
EVENT_URL: Final[str] = f"{BASE_URL}/News/Events"

# 크롤링 설정
SLEEP_TIME: Final[float] = 1.0
MAX_RETRIES: Final[int] = 2
USER_AGENT: Final[str] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'

# 파일 경로
OUTPUT_DIR: Final[Path] = BASE_DIR / "output"
CONTENTS_FILE: Final[Path] = OUTPUT_DIR / "notice_contents.json"
LAST_NOTIFIED_FILE: Final[Path] = OUTPUT_DIR / "last_notified.json"
EVENT_CONTENTS_FILE: Final[Path] = OUTPUT_DIR / "event_contents.json"
EVENT_IMAGES_DIR: Final[Path] = OUTPUT_DIR / "event_images"

# 디버그 설정
DEBUG_DIR: Final[Path] = BASE_DIR / "debug"

# API 설정
GPT_API_KEY: Final[str] = os.getenv("GPT_API_KEY", "")

# 디스코드 웹훅 URL 설정
DISCORD_WEBHOOK_URL: Final[str] = os.getenv("DISCORD_WEBHOOK_URL", "")

# 로깅 설정
LOG_FORMAT: Final[str] = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL: Final[str] = "DEBUG" if DEBUG else "INFO" 