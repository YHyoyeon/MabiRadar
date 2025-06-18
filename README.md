# 📡 MabiRadar Crawler

 **마비노기 모바일**의 게시글 및 댓글을 크롤링하는 Python 기반 크롤러입니다.  
게시글 제목, 본문, 댓글을 수집하여 `contents.csv`, `replies.csv` 파일로 저장 후 원하는 처리를 합니다.


## ⚙️ 설치 및 실행 방법

### 1. Python 설치 확인
python3 --version

2. 의존성 설치
cd crawler
pip install -r requirements.txt

3. 크롤러 실행
python mabi_crawler.py

⚙️ 설정 변경
config.py

🧪 주의사항
Selenium을 사용하므로 크롬 브라우저가 자동으로 실행됩니다.
webdriver-manager가 자동으로 드라이버를 설치합니다.
요청이 너무 빠르면 차단당할 수 있으니 sleep(1) 이상 유지하는 것이 좋습니다.
빈 내용의 게시물, 이미지/디시콘만 있는 댓글은 건너뛰거나 누락될 수 있습니다.

📝 향후 개선 아이디어
디시 사이트에 요약 API 연동 후 비속어를 제외한 공략 글 정리
게시글 ID로 중복 제거 및 재수집 방지
주기적 실행을 위한 배치 스크립트 구성