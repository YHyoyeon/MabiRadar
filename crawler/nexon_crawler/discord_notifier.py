from discord_webhook import DiscordWebhook, DiscordEmbed
import json
from typing import List, Dict
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class DiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.last_notified_ids = self._load_last_notified_ids()
        
    def _load_last_notified_ids(self) -> set:
        """마지막으로 알림을 보낸 게시글 ID들을 로드"""
        try:
            if os.path.exists('last_notified.json'):
                with open('last_notified.json', 'r') as f:
                    return set(json.load(f))
            return set()
        except Exception as e:
            logger.error(f"마지막 알림 ID 로드 중 오류 발생: {str(e)}")
            return set()
    
    def _save_last_notified_ids(self):
        """알림을 보낸 게시글 ID들을 저장"""
        try:
            with open('last_notified.json', 'w') as f:
                json.dump(list(self.last_notified_ids), f)
        except Exception as e:
            logger.error(f"마지막 알림 ID 저장 중 오류 발생: {str(e)}")
    
    def send_notification(self, posts: List[Dict]):
        """새로운 게시글에 대해 디스코드 알림 전송"""
        new_posts = [post for post in posts if post['id'] not in self.last_notified_ids]
        
        if not new_posts:
            logger.info("새로운 게시글이 없습니다.")
            return
        
        webhook = DiscordWebhook(url=self.webhook_url)
        
        for post in new_posts:
            embed = DiscordEmbed(
                title=f"[{post['type']}] {post['title']}",
                description=post['content'][:1000] + "..." if len(post['content']) > 1000 else post['content'],
                color=0x3498db  # 파란색
            )
            
            # 게시글 URL 추가
            post_url = f"https://mabinogi.nexon.com/News/Notice/{post['id']}"
            embed.add_embed_field(name="링크", value=f"[게시글 보기]({post_url})")
            
            # 날짜 정보 추가
            embed.add_embed_field(name="작성일", value=post['date'])
            
            webhook.add_embed(embed)
            self.last_notified_ids.add(post['id'])
        
        try:
            response = webhook.execute()
            if response.status_code == 204:
                logger.info(f"{len(new_posts)}개의 새로운 게시글에 대한 알림을 전송했습니다.")
                self._save_last_notified_ids()
            else:
                logger.error(f"알림 전송 실패: {response.status_code}")
        except Exception as e:
            logger.error(f"알림 전송 중 오류 발생: {str(e)}") 