from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging

def setup_webdriver() -> webdriver.Chrome:
    """웹드라이버 설정을 초기화하고 반환합니다."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def save_screenshot(driver: webdriver.Chrome, url: str, save_path: Path, wait_time: int = 2) -> str:
    """
    웹페이지의 스크린샷을 저장합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        url: 스크린샷을 찍을 웹페이지 URL
        save_path: 스크린샷을 저장할 경로
        wait_time: 페이지 로딩 대기 시간 (초)
    
    Returns:
        str: 저장된 스크린샷의 경로. 실패시 빈 문자열 반환
    """
    try:
        # 저장 디렉토리 생성
        save_path.parent.mkdir(exist_ok=True)
        
        # 페이지 로드
        driver.get(url)
        time.sleep(wait_time)
        
        # 페이지의 전체 높이 계산
        total_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
        
        # 현재 창 크기 가져오기
        window_size = driver.get_window_size()
        
        # 전체 높이의 50%로 창 크기 조정
        capture_height = int(total_height * 0.5)
        driver.set_window_size(window_size['width'], capture_height)
        
        # 스크린샷 저장
        driver.save_screenshot(str(save_path))
        
        # 원래 창 크기로 복원
        driver.set_window_size(window_size['width'], window_size['height'])
        
        return str(save_path)
    except Exception as e:
        logging.error(f"스크린샷 저장 중 오류 발생: {str(e)}")
        return "" 