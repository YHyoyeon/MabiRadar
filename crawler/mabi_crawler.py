from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
from typing import List, Tuple, Optional
import logging

from config import (
    START_DATE, END_DATE, GALLERY_TYPE, TARGET_GALLERY, 
    BASE_URL, SLEEP_TIME, MAX_RETRIES
)
from save import save_data

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MabiCrawler:
    def __init__(self):
        self.driver = self._setup_driver()
        self.posts: List[Tuple] = []
        self.comments: List[Tuple] = []
        
    def _setup_driver(self) -> webdriver.Chrome:
        """크롬 드라이버를 설정하고 반환합니다."""
        options = Options()
        options.add_argument('--headless')  # 헤드리스 모드
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    
    def _get_page_with_retry(self, url: str, retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
        """페이지를 가져오고 파싱합니다. 실패시 재시도합니다."""
        for i in range(retries):
            try:
                self.driver.get(url)
                sleep(SLEEP_TIME)
                return BeautifulSoup(self.driver.page_source, "html.parser")
            except WebDriverException as e:
                logger.error(f"페이지 로드 실패 (시도 {i+1}/{retries}): {str(e)}")
                if i == retries - 1:
                    return None
                sleep(SLEEP_TIME * 2)
    
    def crawl(self):
        """크롤링을 실행합니다."""
        page = 1
        while True:
            url = f"{BASE_URL}/{GALLERY_TYPE}/board/lists/?id={TARGET_GALLERY}&page={page}"
            soup = self._get_page_with_retry(url)
            if not soup:
                break
                
            article_list = soup.select("tr.ub-content")
            if not article_list:
                break
                
            # 날짜 범위 검사
            try:
                latest_date = "20" + article_list[-1].select_one("td.gall_date").text.strip()
                latest_time = datetime.strptime(latest_date, "%Y.%m.%d")
            except Exception as e:
                logger.error(f"날짜 파싱 실패: {str(e)}")
                break
                
            if START_DATE < latest_time:
                page += 1
                continue
            elif latest_time < END_DATE:
                break
                
            self._process_articles(article_list)
            page += 1
            
        self.driver.quit()
        save_data(self.posts, self.comments)
        
    def _process_articles(self, article_list):
        """게시글 목록을 처리합니다."""
        for article in article_list:
            head = article.select_one("td.gall_subject").text.strip()
            if head in ["공지", "AD", "설문"]:
                continue
                
            try:
                title_tag = article.select_one("a")
                title = title_tag.text.strip()
                gall_id = article.select_one("td.gall_num").text.strip()
                post_url = BASE_URL + title_tag['href']
                
                self._process_single_article(gall_id, title, post_url, article)
            except Exception as e:
                logger.error(f"게시글 처리 실패: {str(e)}")
                
    def _process_single_article(self, gall_id: str, title: str, post_url: str, article):
        """단일 게시글을 처리합니다."""
        post_soup = self._get_page_with_retry(post_url)
        if not post_soup:
            return
            
        try:
            content = post_soup.select_one("div.write_div").text.strip()
        except:
            content = ""
            
        post_date = "20" + article.select_one("td.gall_date").text.strip()
        self.posts.append((gall_id, title, content, post_date))
        
        self._process_comments(post_soup, gall_id)
        
    def _process_comments(self, post_soup: BeautifulSoup, gall_id: str):
        """댓글을 처리합니다."""
        reply_blocks = post_soup.select("li.ub-content")
        for r in reply_blocks:
            try:
                rid = r.select_one("em").text.strip()
                rdate = r.select_one("span.date_time").text.strip()
                rtext = r.select_one("p.ub-word").text.strip()
                self.comments.append((gall_id, rid, rtext, rdate))
            except Exception as e:
                logger.error(f"댓글 처리 실패: {str(e)}")
                continue

if __name__ == "__main__":
    crawler = MabiCrawler()
    crawler.crawl()
