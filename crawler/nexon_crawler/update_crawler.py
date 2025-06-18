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
    UPDATE_URL, UPDATE_CONTENTS_FILE,
    DEBUG_DIR, UPDATE_IMAGES_DIR,
    UPDATE_LAST_ID_FILE
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

class UpdateCrawler:
    def __init__(self):
        self.session = setup_session()
        self.updates: List[Dict] = []
        self.discord_notifier = DiscordNotifier()
        ensure_directories()
        
        # Selenium 설정
        self.driver = setup_webdriver()
        
        # 최신 ID 파일 경로 설정
        self.latest_id_file = Path(UPDATE_LAST_ID_FILE).parent / "update_latest_id.json"
        
    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def _save_current_updates(self):
        logging.info(f"현재 업데이트 목록을 저장: {UPDATE_CONTENTS_FILE}")
        save_current_items(UPDATE_CONTENTS_FILE, self.updates)
        logging.info(f"업데이트 저장 완료")

    def crawl(self):
        logging.info(f"{self.__class__.__name__} 크롤링 시작")

        try:
            # 페이지 가져오기
            soup = get_page_content(UPDATE_URL, self.session)
            if not soup:
                logging.error("업데이트 페이지를 가져오는데 실패했습니다")
                return

            # 페이지 HTML 저장 (디버깅용)
            with open(DEBUG_DIR / "debug_update_page.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())

            # 업데이트 목록 찾기
            list_area = soup.select_one('.list_area[data-mm-boardlist]')
            if not list_area:
                logging.error("업데이트 목록 영역을 찾을 수 없습니다")
                return

            # 업데이트 목록 추출
            update_list = list_area.select('li.item[data-mm-listitem]')
            if not update_list:
                logging.error("업데이트를 찾을 수 없습니다")
                return

            # 첫 번째 업데이트 ID 확인
            first_update_id = max(int(update.get('data-threadid')) for update in update_list)
            if not first_update_id:
                logging.error("첫 번째 업데이트 ID를 찾을 수 없습니다")
                return

            # 저장된 최신 ID 로드
            saved_latest_id = load_latest_id(self.latest_id_file, "update")
            
            # 첫 번째 업데이트가 저장된 최신 ID와 같으면 크롤링 중단
            if saved_latest_id and first_update_id == saved_latest_id:
                logging.info("새로운 업데이트가 없습니다.")
                return

            logging.info(f"총 {len(update_list)}개의 업데이트를 찾았습니다")
            self._process_updates(update_list)

        except Exception as e:
            logging.error(f"크롤링 중 오류 발생: {str(e)}")
        
    def _process_updates(self, update_list):
        """업데이트 목록을 처리하는 메서드"""
        saved_latest_id = load_latest_id(self.latest_id_file, "update")
        
        for update in update_list:
            try:
                # 업데이트 ID 추출
                update_id = update.get('data-threadid')
                if not update_id:
                    continue

                # 저장된 최신 ID와 일치하면 업데이트 후 크롤링 중단
                if saved_latest_id and int(update_id) <= int(saved_latest_id):
                    break

                # 제목 추출
                title_elem = update.select_one('.title span')
                if not title_elem:
                    continue
                title = title_elem.text.strip()

                # 업데이트 URL 생성
                update_url = f"{UPDATE_URL}/{update_id}"
                logging.info(f"업데이트 URL 생성: {update_url}")

                # 날짜 추출
                date_elem = update.select_one('.date span')
                if not date_elem:
                    continue
                update_date = date_elem.text.strip()

                # 업데이트 타입 추출
                type_elem = update.select_one('.type span')
                update_type = type_elem.text.strip() if type_elem else "일반"

                # 만약 첫 번째 업데이트면
                is_first = update_list.index(update) == 0

                # 업데이트 처리
                self._process_single_update(update_id, title, update_url, update_date, update_type, is_first)

            except Exception as e:
                logging.error(f"업데이트 처리 중 오류 발생: {str(e)}")
                continue
        
        # 업데이트 저장
        self._save_current_updates()
        
        # 새로운 업데이트만 디스코드 알림 전송
        new_updates = [update for update in self.updates]
        if new_updates:
            logging.info(f"새로운 업데이트 {len(new_updates)}개 발견! 디스코드 알림 전송")
            for update in new_updates:
                update_url = f"{UPDATE_URL}/{update['id']}"
                image_path = UPDATE_IMAGES_DIR / f"{update['id']}.png"
                self.discord_notifier.send_notification(update, update_url, "업데이트", image_path)
            
            # 최신 ID 저장
            if new_updates:
                latest_id = max(int(update['id']) for update in new_updates)
                save_latest_id(self.latest_id_file, "update", latest_id)
                logging.info(f"최신 ID 저장 완료: {latest_id}")
        else:
            logging.info("새로운 업데이트가 없습니다.")
                
    def _process_single_update(self, update_id: str, title: str, update_url: str, update_date: str, update_type: str, is_first: bool):
        update_soup = get_page_content(update_url, self.session)
        if not update_soup:
            logging.error(f"업데이트 페이지를 가져오는데 실패했습니다: {update_url}")
            return
        
        if is_first:
            # 페이지 HTML 저장 (디버깅용)
            with open(DEBUG_DIR / "debug_update_first_page.html", "w", encoding="utf-8") as f:
                f.write(update_soup.prettify())
        
        try:            
            # 업데이트 스크린샷 저장
            image_path = UPDATE_IMAGES_DIR / f"{update_id}.png"
            image_path = save_screenshot(self.driver, update_url, image_path)
            
        except Exception as e:
            logging.error(f"업데이트 이미지 저장 중 오류 발생: {str(e)}")
            image_path = ""
            
        self.updates.append({
            'id': update_id,
            'title': title,
            'image_path': image_path,
            'date': update_date,
            'type': update_type
        })

if __name__ == "__main__":
    crawler = UpdateCrawler()
    crawler.crawl() 