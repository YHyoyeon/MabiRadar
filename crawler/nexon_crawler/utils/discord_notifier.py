from discord_webhook import DiscordWebhook, DiscordEmbed
from typing import Dict
from pathlib import Path

from config import DISCORD_WEBHOOK_URL
from crawler.nexon_crawler.utils.utils import setup_logging

logger = setup_logging()

class DiscordNotifier:
    def __init__(self, webhook_url: str = DISCORD_WEBHOOK_URL):
        self.webhook_url = webhook_url
        
    def send_notification(self, post: Dict, post_url: str, type: str = None, image_path: str = None, start_date: str = None, end_date: str = None):        
        webhook = DiscordWebhook(url=self.webhook_url)

        max_description_length = 50

        # Convert Path object to string if necessary
        image_path_str = str(image_path) if image_path else None

        embed = DiscordEmbed(
            title=f"[새로운 {type}] {post['title']}",
            description=post.get('content', '')[:max_description_length] + "..." if len(post.get('content', '')) > max_description_length else post.get('content', ''),
            color=0x3498db  # 파란색
        )
        
        # 게시글 URL 추가
        embed.add_embed_field(name="공지사항 링크", value=f"[게시글 보기]({post_url})")
        if start_date:
            embed.add_embed_field(name="시작일", value=f"**{start_date}**")
        if end_date:
            embed.add_embed_field(name="종료일", value=f"**{end_date}**")
        
        # 이미지가 있는 경우에만 이미지 추가
        if image_path_str:
            embed.set_image(url=f"attachment://{Path(image_path_str).name}")
        
        webhook.add_embed(embed)
        
        try:
            # 이미지가 있는 경우 파일 첨부
            if image_path_str and Path(image_path_str).exists():
                with open(image_path_str, "rb") as f:
                    webhook.add_file(file=f.read(), filename=Path(image_path_str).name)
            
            response = webhook.execute()
            if response.status_code == 200:
                logger.info(f"{post['title']} 에 대한 알림을 전송했습니다.")
            else:
                logger.error(f"Webhook status code {response.status_code}: {response.text}")
                logger.error(f"알림 전송 실패: {response.status_code}")
        except Exception as e:
            logger.error(f"알림 전송 중 오류 발생: {str(e)}") 