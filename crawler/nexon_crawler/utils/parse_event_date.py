import re
from datetime import datetime

class EventDateParser:
    def parse_event_date(self, event_date: str):
        # 정규식으로 날짜 구간 추출
        match = re.match(r"(.+?)\s*~\s*(.+?까지)", event_date)
        if not match:
            raise ValueError("날짜 형식이 올바르지 않습니다.")

        start_str, end_str = match.groups()
        start_date = self._parse_single_date(start_str, is_start=True)
        end_date = self._parse_single_date(end_str, is_start=False)
        return start_date, end_date

    def _parse_single_date(self, date_str: str, is_start: bool):
        # 점검 후 → 오전 6시
        date_str = date_str.replace("점검 후", "오전 6시")

        # 날짜 및 시간 추출
        date_match = re.match(r"(\d{4})\.(\d{1,2})\.(\d{1,2})\([월화수목금토일]\)\s*(오전|오후)?\s*(\d{1,2})(시)?\s*(\d{1,2})?분?", date_str)
        if not date_match:
            # 시간이 명시되어 있지 않은 경우 기본 시간 설정
            date_match = re.match(r"(\d{4})\.(\d{1,2})\.(\d{1,2})", date_str)
            if not date_match:
                raise ValueError(f"날짜 파싱 실패: {date_str}")
            year, month, day = map(int, date_match.groups())
            hour, minute = (6, 0) if is_start else (5, 59)
        else:
            year, month, day, ampm, hour, _, minute = date_match.groups()
            year, month, day = int(year), int(month), int(day)
            hour = int(hour)
            minute = int(minute) if minute else 0

            if ampm == '오후' and hour != 12:
                hour += 12
            if ampm == '오전' and hour == 12:
                hour = 0

        return datetime(year, month, day, hour, minute)