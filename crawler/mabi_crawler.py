from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime, timedelta
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
        logger.info("크롬 드라이버 설정 시작")
        options = Options()
        # 헤드리스 옵션 완전 비활성화
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        # navigator.webdriver 속성 우회
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        return driver
    
    def _get_page_with_retry(self, url: str, retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
        logger.info(f"페이지 로드 시도: {url}")
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
        logger.info("크롤링 시작")
        logger.info(f"현재시간 : {START_DATE}")
        logger.info(f"종료시간 : {END_DATE}")
        
        page = 1
        while True:
            url = f"{BASE_URL}/{GALLERY_TYPE}/board/lists/?id={TARGET_GALLERY}&page={page}"
            soup = self._get_page_with_retry(url)
            if not soup:
                logger.error("페이지 로드 실패 - soup이 없습니다")
                break
                
            # 첫 페이지 HTML 저장 (디버깅용)
            if page == 1:
                with open("debug_first_page.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())
                
            # 게시글 목록 찾기
            article_list = soup.select("tr.ub-content")
            if not article_list:
                logger.error("게시글을 찾을 수 없습니다")
                break

            logger.info(f"url: {url}")
            logger.info(f"게시글 수: {len(article_list)}개")
                
            # 현재 페이지의 게시글 처리
            self._process_articles(article_list)
            page += 1
                
        self.driver.quit()
        save_data(self.posts, self.comments)
        
    def _process_articles(self, article_list):
        logger.info(f"게시글 목록 처리 시작: {len(article_list)}개")
        for article in article_list:
            try:
                # 게시글 제목 찾기
                title_td = article.select_one("td.gall_tit")
                if not title_td:
                    logger.error("gall_tit를 찾을 수 없습니다")
                    continue
                    
                title_link = title_td.select_one("a")
                if not title_link:
                    logger.error("제목 링크를 찾을 수 없습니다")
                    continue
                
                # 설문 게시글 체크
                if title_link.get('href', '').startswith('javascript:;'):
                    logger.info("설문 게시글 건너뜁니다")
                    continue
                
                # 제목에서 아이콘 제거
                icon = title_link.select_one("em.icon_img")
                if icon:
                    icon.decompose()
                    
                title = title_link.text.strip()
                
                # 게시글 번호 찾기
                gall_id = article.select_one("td.gall_num")
                if not gall_id:
                    logger.error("게시글 번호를 찾을 수 없습니다")
                    continue
                    
                gall_id = gall_id.text.strip()
                post_url = BASE_URL + title_link['href']
                
                # 게시글 종류 확인 (공지, 일반 등)
                subject_td = article.select_one("td.gall_subject")
                if not subject_td:
                    logger.error("gall_subject를 찾을 수 없습니다")
                    continue
                    
                subject = subject_td.select_one("b")
                if subject:
                    subject = subject.text.strip()
                else:
                    subject = subject_td.text.strip()
                    
                if subject in ["공지", "AD", "설문"]:
                    logger.info(f"제외 게시글 건너뜁니다: {subject}")
                    continue
                
                logger.info(f"게시글 발견: {title} (ID: {gall_id})")
                self._process_single_article(gall_id, title, post_url, article)
            except Exception as e:
                logger.error(f"게시글 처리 실패: {str(e)}")
                
    def _process_single_article(self, gall_id: str, title: str, post_url: str, article):
        logger.info(f"단일 게시글 처리 시작")
        
        # 날짜 체크
        try:
            date_td = article.select_one("td.gall_date")
            if not date_td:
                logger.error("날짜 정보를 찾을 수 없습니다")
                return
                
            # title 속성에서 날짜 가져오기
            post_date = date_td.get('title', '')
            if not post_date:
                logger.error("날짜 title 속성을 찾을 수 없습니다")
                return
                
            logger.info(f"post_date: {post_date}")
            post_time = datetime.strptime(post_date, "%Y-%m-%d %H:%M:%S")
            
            if post_time < START_DATE:
                logger.info(f"START_DATE({START_DATE})보다 이전 게시글 발견, 크롤링 종료")
                self.driver.quit()
                save_data(self.posts, self.comments)
                exit(0)
            elif post_time > END_DATE:
                logger.info(f"END_DATE({END_DATE})보다 이후 게시글 발견, 크롤링 종료")
                self.driver.quit()
                save_data(self.posts, self.comments)
                exit(0)
        except Exception as e:
            logger.error(f"날짜 파싱 실패: {str(e)}")
            return
            
        post_soup = self._get_page_with_retry(post_url)
        if not post_soup:
            return            
        try:            
            content = post_soup.select_one("div.write_div").text.strip()
        except:
            content = ""
            
        self.posts.append((gall_id, title, content, post_date))
        
        # self._process_comments(post_soup, gall_id)
        
    # def _process_comments(self, post_soup: BeautifulSoup, gall_id: str):
    #     logger.info(f"댓글 처리 시작: {gall_id}")
    #     reply_blocks = post_soup.select("li.ub-content")
    #     for r in reply_blocks:
    #         try:
    #             rid = r.select_one("em").text.strip()
    #             rdate = r.select_one("span.date_time").text.strip()
    #             rtext = r.select_one("p.ub-word").text.strip()
    #             self.comments.append((gall_id, rid, rtext, rdate))
    #         except Exception as e:
    #             logger.error(f"댓글 처리 실패: {str(e)}")
    #             continue

if __name__ == "__main__":
    crawler = MabiCrawler()
    crawler.crawl()
