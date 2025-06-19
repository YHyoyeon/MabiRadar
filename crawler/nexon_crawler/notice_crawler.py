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
    NOTICE_URL, NOTICE_CONTENTS_FILE, DEBUG_DIR, NOTICE_IMAGES_DIR,
    NOTICE_LAST_ID_FILE
)
from crawler.nexon_crawler.utils.utils import (
    setup_logging, ensure_directories, setup_session,
    get_page_content,
    save_current_items,
    load_latest_id, save_latest_id
)
from crawler.nexon_crawler.utils.discord_notifier import DiscordNotifier
from crawler.nexon_crawler.utils.screenshot_utils import setup_webdriver, save_screenshot

logging = setup_logging()

class NoticeCrawler:
    def __init__(self):
        self.session = setup_session()
        self.notices: List[Dict] = []
        self.discord_notifier = DiscordNotifier()
        ensure_directories()
        
        # Selenium 설정
        self.driver = setup_webdriver()
        
        # 최신 ID 파일 경로 설정
        self.latest_id_file = Path(NOTICE_LAST_ID_FILE).parent / "notice_latest_id.json"
        
    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def _save_current_notices(self):
        logging.info(f"현재 공지사항 목록을 저장: {NOTICE_CONTENTS_FILE}")
        save_current_items(NOTICE_CONTENTS_FILE, self.notices)
        logging.info(f"공지사항 저장 완료")

    def crawl(self):
        logging.info(f"{self.__class__.__name__} 크롤링 시작")

        try:
            # 페이지 가져오기
            soup = get_page_content(NOTICE_URL, self.session)
            if not soup:
                logging.error("공지사항 페이지를 가져오는데 실패했습니다")
                return

            # 페이지 HTML 저장 (디버깅용)
            with open(DEBUG_DIR / "debug_notice_page.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())

            # 공지사항 목록 찾기
            list_area = soup.select_one('.list_area[data-mm-boardlist]')
            if not list_area:
                logging.error("공지사항 목록 영역을 찾을 수 없습니다")
                return

            # 공지사항 목록이 비어있는지 확인
            list_empty = list_area.select_one('.list_empty')
            if list_empty:
                logging.info("현재 공지사항 목록이 비어있습니다. 게시글이 없습니다.")
                return

            # 공지사항 목록 추출
            notice_list = list_area.select('li.item[data-mm-listitem]')
            if not notice_list:
                logging.error("공지사항을 찾을 수 없습니다")
                return

            # 첫 번째 공지사항 ID 확인
            first_notice_id = max(int(notice.get('data-threadid')) for notice in notice_list)
            if not first_notice_id:
                logging.error("첫 번째 공지사항 ID를 찾을 수 없습니다")
                return

            # 저장된 최신 ID 로드
            saved_latest_id = load_latest_id(self.latest_id_file, "notice")
            
            # 첫 번째 공지사항이 저장된 최신 ID와 같으면 크롤링 중단
            if saved_latest_id and first_notice_id == saved_latest_id:
                logging.info("새로운 공지사항이 없습니다.")
                return

            logging.info(f"총 {len(notice_list)}개의 공지사항을 찾았습니다")
            self._process_notices(notice_list)

        except Exception as e:
            logging.error(f"크롤링 중 오류 발생: {str(e)}")
        
    def _process_notices(self, notice_list):
        """공지사항 목록을 처리하는 메서드"""
        saved_latest_id = load_latest_id(self.latest_id_file, "notice")
        
        for notice in notice_list:
            try:
                # 공지사항 ID 추출
                notice_id = notice.get('data-threadid')
                if not notice_id:
                    continue

                # 저장된 최신 ID와 일치하면 공지사항 후 크롤링 중단
                if saved_latest_id and int(notice_id) <= int(saved_latest_id):
                    break

                # 제목 추출
                title_elem = notice.select_one('.title span')
                if not title_elem:
                    continue
                title = title_elem.text.strip()

                # 공지사항 URL 생성
                notice_url = f"{NOTICE_URL}/{notice_id}"
                logging.info(f"공지사항 URL 생성: {notice_url}")

                # 날짜 추출
                date_elem = notice.select_one('.date span')
                if not date_elem:
                    continue
                notice_date = date_elem.text.strip()

                # 공지사항 타입 추출
                type_elem = notice.select_one('.type span')
                notice_type = type_elem.text.strip() if type_elem else "일반"

                # 만약 첫 번째 공지사항이면
                is_first = notice_list.index(notice) == 0

                # 공지사항 처리
                self._process_single_notice(notice_id, title, notice_url, notice_date, notice_type, is_first)

            except Exception as e:
                logging.error(f"공지사항 처리 중 오류 발생: {str(e)}")
                continue
        
        # 공지사항 저장
        self._save_current_notices()
        
        # 새로운 공지사항만 디스코드 알림 전송
        new_notices = [notice for notice in self.notices]
        if new_notices:
            logging.info(f"새로운 공지사항 {len(new_notices)}개 발견! 디스코드 알림 전송")
            for notice in new_notices:
                notice_url = f"{NOTICE_URL}/{notice['id']}"
                image_path = NOTICE_IMAGES_DIR / f"{notice['id']}.png"
                self.discord_notifier.send_notification(notice, notice_url, "공지사항", image_path, notice_date)
            
            # 최신 ID 저장
            if new_notices:
                latest_id = max(int(notice['id']) for notice in new_notices)
                save_latest_id(self.latest_id_file, "notice", latest_id)
                logging.info(f"최신 ID 저장 완료: {latest_id}")
        else:
            logging.info("새로운 공지사항이 없습니다.")
                
    def _process_single_notice(self, notice_id: str, title: str, notice_url: str, notice_date: str, notice_type: str, is_first: bool):
        notice_soup = get_page_content(notice_url, self.session)
        if not notice_soup:
            logging.error(f"공지사항 페이지를 가져오는데 실패했습니다: {notice_url}")
            return
        
        if is_first:
            # 페이지 HTML 저장 (디버깅용)
            with open(DEBUG_DIR / "debug_notice_first_page.html", "w", encoding="utf-8") as f:
                f.write(notice_soup.prettify())
        
        try:            
            # 공지사항 스크린샷 저장
            image_path = NOTICE_IMAGES_DIR / f"{notice_id}.png"
            image_path = save_screenshot(self.driver, notice_url, image_path)
            
        except Exception as e:
            logging.error(f"공지사항 이미지 저장 중 오류 발생: {str(e)}")
            image_path = ""
            
        self.notices.append({
            'id': notice_id,
            'title': title,
            'image_path': image_path,
            'date': notice_date,
            'type': notice_type
        })

if __name__ == "__main__":
    crawler = NoticeCrawler()
    crawler.crawl() 