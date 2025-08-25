# slack_webhook.py
import requests
from typing import Optional
from config import CONFIG  # or store your webhook in .env

class SlackWebhook:
    def __init__(self, webhook_url: Optional[str] = None):
        """
        webhook_url: Slack Incoming Webhook URL
        """
        self.webhook_url = webhook_url or CONFIG.SLACK_WEBHOOK_URL

    def send_message(self, text: str):
        """
        Send a simple text message to Slack
        """
        payload = {"text": text}
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return {"ok": True, "status_code": response.status_code}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_block_message(self, blocks: list):
        """
        Send a Slack message with blocks
        """
        payload = {"blocks": blocks}
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return {"ok": True, "status_code": response.status_code}
        except Exception as e:
            return {"ok": False, "error": str(e)}
