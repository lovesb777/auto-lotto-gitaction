import time
import sys
import re
from datetime import datetime, timedelta

from requests import get, Response
from playwright.sync_api import Playwright, sync_playwright

# 동행복권 아이디와 패스워드를 설정
USER_ID = sys.argv[1]
USER_PW = sys.argv[2]

# 구매 개수를 설정
COUNT = sys.argv[3]

# 텔레그램 봇 토큰을 설정
TELEGRAM_BOT_TOKEN = sys.argv[4]
TELEGRAM_BOT_CHANNEL_ID = sys.argv[5]

def __get_now() -> datetime:
    now_utc = datetime.utcnow()
    korea_timezone = timedelta(hours=9)
    now_korea = now_utc + korea_timezone
    return now_korea

def send_message(message: str) -> Response:
    korea_time_str = __get_now().strftime("%Y-%m-%d %H:%M:%S")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": TELEGRAM_BOT_CHANNEL_ID,
        "text": f"> {korea_time_str} *로또 자동 구매 봇 알림* \n {message}",
    }
    headers = { "Content-Type": "application/json" }
    res = get(url, params=params, headers=headers)
    return res

def run(playwright: Playwright) -> None:
    send_message(f"이번주 나의 행운의 번호는?! 테스트!")

with sync_playwright() as playwright:
    run(playwright)
