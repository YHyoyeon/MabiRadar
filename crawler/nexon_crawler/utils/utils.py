import logging
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from time import sleep

from config import (
    SLEEP_TIME, MAX_RETRIES, USER_AGENT,
    OUTPUT_DIR, DEBUG_DIR, LOG_FORMAT, LOG_LEVEL
)

def setup_logging() -> logging.Logger:
    """로깅 설정을 초기화하고 로거를 반환합니다."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT
    )
    return logging.getLogger(__name__)

def ensure_directories() -> None:
    """필요한 디렉토리들을 생성합니다."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    DEBUG_DIR.mkdir(exist_ok=True)

def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """JSON 파일을 로드합니다."""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logging.error(f"JSON 파일 로드 중 오류 발생: {str(e)}")
        return []

def save_json_file(file_path: Path, data: List[Dict[str, Any]]) -> None:
    """데이터를 JSON 파일로 저장합니다."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"JSON 파일 저장 중 오류 발생: {str(e)}")

def get_page_content(url: str, session: requests.Session) -> Optional[BeautifulSoup]:
    """웹 페이지를 가져와서 BeautifulSoup 객체로 반환합니다."""
    for i in range(MAX_RETRIES):
        try:
            response = session.get(url)
            response.raise_for_status()
            sleep(SLEEP_TIME)
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            logging.error(f"페이지 로드 실패 (시도 {i+1}/{MAX_RETRIES}): {str(e)}")
            if i == MAX_RETRIES - 1:
                return None
            sleep(SLEEP_TIME * 2)

def setup_session() -> requests.Session:
    """requests 세션을 설정하고 반환합니다."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache'
    })
    return session

def save_current_items(file_url: str, items: List[Dict]) -> None:
    """현재 아이템들을 JSON 파일로 저장합니다."""
    save_json_file(file_url, items)

def load_latest_id(file_path: Path, crawler_type: str) -> Optional[str]:
    """크롤러별 최신 ID를 로드합니다."""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get(crawler_type)
        return None
    except Exception as e:
        logging.error(f"최신 ID 로드 중 오류 발생: {str(e)}")
        return None

def save_latest_id(file_path: Path, crawler_type: str, latest_id: str) -> None:
    """크롤러별 최신 ID를 저장합니다."""
    try:
        data = {crawler_type: latest_id}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"최신 ID 저장 중 오류 발생: {str(e)}") 