from typing import List, Dict, Set
import sys
from pathlib import Path
from datetime import datetime
from selenium import webdriver
import time

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from crawler.nexon_crawler.config import (
    EVENT_URL, EVENT_CONTENTS_FILE,
    DEBUG_DIR, EVENT_IMAGES_DIR
)
from crawler.nexon_crawler.utils.utils import (
    setup_logging, ensure_directories, setup_session,
    get_page_content,
    load_previous_ids, save_current_items
)
from crawler.nexon_crawler.utils.discord_notifier import DiscordNotifier
from crawler.nexon_crawler.utils.parse_event_date import EventDateParser
from crawler.nexon_crawler.utils.screenshot_utils import setup_webdriver, save_screenshot

logging = setup_logging()

class EventCrawler:
    def __init__(self):
        self.session = setup_session()
        self.events: List[Dict] = []
        self.discord_notifier = DiscordNotifier()
        self.previous_event_ids: Set[str] = load_previous_ids(EVENT_CONTENTS_FILE)
        ensure_directories()
        
        # Selenium 설정
        self.driver = setup_webdriver()
        
    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def _save_current_events(self):
        logging.info(f"현재 이벤트 목록을 저장: {EVENT_CONTENTS_FILE}")
        save_ids = save_current_items(EVENT_CONTENTS_FILE, self.events)
        logging.info(f"이벤트 저장 완료 ids: {save_ids}")

    def crawl(self):
        logging.info(f"{self.__class__.__name__} 크롤링 시작")

        try:
            # 페이지 가져오기
            soup = get_page_content(EVENT_URL, self.session)
            if not soup:
                logging.error("이벤트 페이지를 가져오는데 실패했습니다")
                return

            # 페이지 HTML 저장 (디버깅용)
            with open(DEBUG_DIR / "debug_event_page.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())

            # 이벤트 목록 찾기
            list_area = soup.select_one('.list_area[data-mm-boardlist]')
            if not list_area:
                logging.error("이벤트 목록 영역을 찾을 수 없습니다")
                return

            # 이벤트 목록 추출
            event_list = list_area.select('li.item[data-mm-listitem]')
            if not event_list:
                logging.error("이벤트를 찾을 수 없습니다")
                return

            logging.info(f"총 {len(event_list)}개의 이벤트를 찾았습니다")
            self._process_events(event_list)

        except Exception as e:
            logging.error(f"크롤링 중 오류 발생: {str(e)}")
        
    def _process_events(self, event_list):
        """이벤트 목록을 처리하는 메서드"""
        for event in event_list:
            try:
                # 이벤트 ID 추출
                event_id = event.get('data-threadid')
                if not event_id:
                    continue

                # 제목 추출
                title_elem = event.select_one('.title span')
                if not title_elem:
                    continue
                title = title_elem.text.strip()

                # 이벤트 URL 생성
                event_url = f"{EVENT_URL}/{event_id}"
                logging.info(f"이벤트 URL 생성: {event_url}")

                # 날짜 추출
                date_elem = event.select_one('.date span')
                if not date_elem:
                    continue
                event_date = date_elem.text.strip()

                # 이벤트 타입 추출
                type_elem = event.select_one('.type span')
                event_type = type_elem.text.strip() if type_elem else "일반"

                # 만약 첫 번째 이벤트면
                is_first = event_list.index(event) == 0

                # 이벤트 처리
                self._process_single_event(event_id, title, event_url, event_date, event_type, is_first)

            except Exception as e:
                logging.error(f"이벤트 처리 중 오류 발생: {str(e)}")
                continue
        
        # 이벤트 저장
        self._save_current_events()
        
        # 새로운 이벤트만 디스코드 알림 전송
        new_events = [event for event in self.events if event['id'] not in self.previous_event_ids]
        if new_events:
            logging.info(f"새로운 이벤트 {len(new_events)}개 발견! 디스코드 알림 전송")
            # TODO: 디스코드 알림 전송 기능 추가
            # self.discord_notifier.send_notification(new_events)
        else:
            logging.info("새로운 이벤트가 없습니다.")
                

    def _process_single_event(self, event_id: str, title: str, event_url: str, event_date: str, event_type: str, is_first: bool):
        event_soup = get_page_content(event_url, self.session)
        if not event_soup:
            logging.error(f"이벤트 페이지를 가져오는데 실패했습니다: {event_url}")
            return
        
        if is_first:
            # 페이지 HTML 저장 (디버깅용)
            with open(DEBUG_DIR / "debug_event_first_page.html", "w", encoding="utf-8") as f:
                f.write(event_soup.prettify())
            
        # 이벤트 날짜 파싱
        parser = EventDateParser()
        start_date, end_date = parser.parse_event_date(event_date)
        
        # 종료된 이벤트는 건너뛰기
        if datetime.now() > end_date:
            logging.info(f"종료된 이벤트 건너뛰기: {title} (종료일: {end_date})")
            return
        
        try:            
            # 이벤트 스크린샷 저장
            image_path = EVENT_IMAGES_DIR / f"{event_id}.png"
            image_path = save_screenshot(self.driver, event_url, image_path)
            
        except Exception as e:
            logging.error(f"이벤트 이미지 저장 중 오류 발생: {str(e)}")
            image_path = ""
            
        self.events.append({
            'id': event_id,
            'title': title,
            'image_path': image_path,
            'date': event_date,
            'type': event_type,
            'start_date': start_date.strftime("%Y-%m-%d %H:%M:%S"),
            'end_date': end_date.strftime("%Y-%m-%d %H:%M:%S")
        })

if __name__ == "__main__":
    crawler = EventCrawler()
    crawler.crawl() 