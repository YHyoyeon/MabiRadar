import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import sys
import os
from datetime import datetime
from time import sleep
from pathlib import Path

# 상위 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    END_DATE, SLEEP_TIME, MAX_RETRIES,
    OUTPUT_DIR, CONTENTS_FILE, REPLIES_FILE,
    BASE_URL, NOTICE_LIST_URL, DEBUG_DIR
)
from save import save_data

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NexonCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.posts: List[Dict] = []
        self.comments: List[Dict] = []
        self._setup_session()
        self.debug_dir = Path(DEBUG_DIR)
        self.debug_dir.mkdir(exist_ok=True)
        
    def _setup_session(self):
        """세션 설정"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def _get_page_with_retry(self, url: str, retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
        """페이지 요청 및 파싱 (재시도 로직 포함)"""
        logger.info(f"페이지 로드 시도: {url}")
        for i in range(retries):
            try:
                response = self.session.get(url)
                response.raise_for_status()
                sleep(SLEEP_TIME)
                
                return BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                logger.error(f"페이지 로드 실패 (시도 {i+1}/{retries}): {str(e)}")
                if i == retries - 1:
                    return None
                sleep(SLEEP_TIME * 2)
    
    def crawl(self):
        """크롤링 메인 함수"""
        logger.info("크롤링 시작")
        logger.info(f"종료시간 : {END_DATE}")
        
        while True:
            url = f"{NOTICE_LIST_URL}"
            soup = self._get_page_with_retry(url)
            if not soup:
                logger.error("페이지 로드 실패 - soup이 없습니다")
                break
                
            # 페이지 HTML 저장 (디버깅용)
            with open(f"{DEBUG_DIR}/debug_first_page.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())
                
            # 게시글 목록 찾기
            article_list = soup.select("div.news_list > ul > li")
            if not article_list:
                logger.error("게시글을 찾을 수 없습니다")
                break

            logger.info(f"url: {url}")
            logger.info(f"게시글 수: {len(article_list)}개")
                
            # 현재 페이지의 게시글 처리
            self._process_articles(article_list)
                
        save_data(self.posts, self.comments)
        
    def _process_articles(self, article_list):
        """게시글 목록 처리"""
        logger.info(f"게시글 목록 처리 시작: {len(article_list)}개")
        for article in article_list:
            try:
                # 게시글 제목과 링크 찾기
                title_link = article.select_one("a")
                if not title_link:
                    logger.error("제목 링크를 찾을 수 없습니다")
                    continue
                
                title = title_link.text.strip()
                post_url = BASE_URL + title_link['href']
                
                # 게시글 번호 찾기 (URL에서 추출)
                post_id = post_url.split('/')[-1]
                
                # 날짜 찾기
                date_span = article.select_one("span.date")
                if not date_span:
                    logger.error("날짜를 찾을 수 없습니다")
                    continue
                    
                post_date = date_span.text.strip()
                post_time = datetime.strptime(post_date, "%Y-%m-%d")
                
                # 종료 시간 체크
                if post_time < END_DATE:
                    logger.info(f"END_DATE({END_DATE})보다 이전 게시글 발견, 크롤링 종료")
                    return
                
                logger.info(f"게시글 발견: {title} (ID: {post_id})")
                self._process_single_article(post_id, title, post_url, post_date)
                
            except Exception as e:
                logger.error(f"게시글 처리 실패: {str(e)}")
                
    def _process_single_article(self, post_id: str, title: str, post_url: str, post_date: str):
        """단일 게시글 처리"""
        logger.info(f"단일 게시글 처리 시작")
        
        post_soup = self._get_page_with_retry(post_url)
        if not post_soup:
            return
            
        try:            
            content = post_soup.select_one("div.news_view > div.content").text.strip()
        except:
            content = ""
            
        self.posts.append({
            'id': post_id,
            'title': title,
            'content': content,
            'date': post_date
        })
        
        # TODO: 댓글 처리 추가
        # self._process_comments(post_soup, post_id)

if __name__ == "__main__":
    crawler = NexonCrawler()
    crawler.crawl() 