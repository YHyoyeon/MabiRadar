from datetime import datetime
from typing import Final

# 갤러리 설정
GALLERY_TYPE: Final[str] = "mgallery"
TARGET_GALLERY: Final[str] = "mabinogimobile"
BASE_URL: Final[str] = "https://gall.dcinside.com"

# 크롤링 설정
START_DATE: Final[datetime] = datetime.strptime("2025.06.17", "%Y.%m.%d")
END_DATE: Final[datetime] = datetime.strptime("2025.06.17", "%Y.%m.%d")

# 크롤링 옵션
SLEEP_TIME: Final[float] = 1.0
MAX_RETRIES: Final[int] = 3

# 파일 경로
OUTPUT_DIR: Final[str] = "output"
CONTENTS_FILE: Final[str] = f"{OUTPUT_DIR}/contents.csv"
REPLIES_FILE: Final[str] = f"{OUTPUT_DIR}/replies.csv"
