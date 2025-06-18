from typing import List, Dict, Optional, Set
import logging
from pathlib import Path

from config import (
    BASE_URL, NOTICE_URL, CONTENTS_FILE,
    DEBUG_DIR
)
from utils import (
    setup_logging, ensure_directories, setup_session,
    get_page_content, load_json_file, save_json_file
)
from discord_notifier import DiscordNotifier

logger = setup_logging()

class NexonCrawler:
    def __init__(self):
        self.session = setup_session()
        self.posts: List[Dict] = []
        self.discord_notifier = DiscordNotifier()
        self.previous_post_ids: Set[str] = self._load_previous_post_ids()
        ensure_directories()
        
    def _load_previous_post_ids(self) -> Set[str]:
        """이전 게시글 ID 목록을 로드"""
        posts = load_json_file(CONTENTS_FILE)
        return {post['id'] for post in posts}
            
    def _save_current_posts(self):
        """현재 게시글 목록을 저장"""
        save_json_file(CONTENTS_FILE, self.posts)
        self.previous_post_ids = {post['id'] for post in self.posts}

    def crawl(self):
        """크롤링 실행"""
        try:
            # 페이지 가져오기
            soup = get_page_content(NOTICE_URL, self.session)
            if not soup:
                logger.error("페이지를 가져오는데 실패했습니다")
                return

            # 페이지 HTML 저장 (디버깅용)
            with open(DEBUG_DIR / "debug_notice_page.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())

            # 게시글 목록 찾기
            list_area = soup.select_one('.list_area[data-mm-boardlist]')
            if not list_area:
                logger.error("게시글 목록 영역을 찾을 수 없습니다")
                return

            # 게시글 목록 추출
            article_list = list_area.select('li.item[data-mm-listitem]')
            if not article_list:
                logger.error("게시글을 찾을 수 없습니다")
                return

            logger.info(f"총 {len(article_list)}개의 게시글을 찾았습니다")
            self._process_articles(article_list)

        except Exception as e:
            logger.error(f"크롤링 중 오류 발생: {str(e)}")
        
    def _process_articles(self, article_list):
        """게시글 목록을 처리하는 메서드"""
        for article in article_list:
            try:
                # 게시글 ID 추출
                post_id = article.get('data-threadid')
                if not post_id:
                    continue

                # 제목 추출
                title_elem = article.select_one('.title span')
                if not title_elem:
                    continue
                title = title_elem.text.strip()

                # 게시글 URL 생성
                post_url = f"{BASE_URL}/News/Notice/{post_id}"
                logger.info(f"게시글 URL 생성: {post_url}")

                # 날짜 추출
                date_elem = article.select_one('.date span')
                if not date_elem:
                    continue
                post_date = date_elem.text.strip()

                # 게시글 타입 추출
                type_elem = article.select_one('.type span')
                post_type = type_elem.text.strip() if type_elem else "일반"

                # 만약 첫 번째 게시글이면
                is_first = article_list.index(article) == 0

                # 게시글 처리
                self._process_single_article(post_id, title, post_url, post_date, post_type, is_first)

            except Exception as e:
                logger.error(f"게시글 처리 중 오류 발생: {str(e)}")
                continue
        
        # 게시글 저장
        self._save_current_posts()
        
        # 새로운 게시글만 디스코드 알림 전송
        new_posts = [post for post in self.posts if post['id'] not in self.previous_post_ids]
        if new_posts:
            logger.info(f"새로운 게시글 {len(new_posts)}개 발견! 디스코드 알림 전송")
            self.discord_notifier.send_notification(new_posts)
        else:
            logger.info("새로운 게시글이 없습니다.")
                
    def _process_single_article(self, post_id: str, title: str, post_url: str, post_date: str, post_type: str, is_first: bool):
        logger.info(f"단일 게시글 처리 시작: {post_url}")
        
        post_soup = get_page_content(post_url, self.session)
        if not post_soup:
            logger.error(f"게시글 페이지를 가져오는데 실패했습니다: {post_url}")
            return
        
        if is_first:
            # 페이지 HTML 저장 (디버깅용)
            with open(DEBUG_DIR / "debug_notice_first_page.html", "w", encoding="utf-8") as f:
                f.write(post_soup.prettify())
            
        try:            
            # 게시글 내용 추출 시도
            content_area = post_soup.select_one('.view_body_wrap .content_area')
            if not content_area:
                logger.error(f"게시글 내용 영역을 찾을 수 없습니다: {post_url}")
                content = ""
            else:
                # 일반 게시글 내용 추출
                content_div = content_area.select_one('.content[data-blockcontent]')
                if content_div:
                    # 모든 텍스트 내용 추출 및 중복 제거
                    text_elements = []
                    for element in content_div.find_all(['p', 'span']):
                        text = element.text.strip()
                        if text and text not in text_elements:  # 중복 체크
                            text_elements.append(text)
                    
                    # 연속된 중복 문장 제거
                    final_texts = []
                    for i, text in enumerate(text_elements):
                        if i == 0 or text != text_elements[i-1]:  # 이전 문장과 다를 때만 추가
                            final_texts.append(text)
                    
                    content = ' '.join(final_texts)
                else:
                    content = ""
            
        except Exception as e:
            logger.error(f"게시글 내용 추출 중 오류 발생: {str(e)}")
            content = ""
            
        self.posts.append({
            'id': post_id,
            'title': title,
            'content': content,
            'date': post_date,
            'type': post_type
        })

if __name__ == "__main__":
    crawler = NexonCrawler()
    crawler.crawl() 