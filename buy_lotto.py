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

    # chrome 브라우저를 실행
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Go to https://dhlottery.co.kr/user.do?method=login
    page.goto("https://dhlottery.co.kr/user.do?method=login")

    # Click [placeholder="아이디"]
    page.click("[placeholder=\"아이디\"]")

    # Fill [placeholder="아이디"]
    page.fill("[placeholder=\"아이디\"]", USER_ID)

    # Press Tab
    page.press("[placeholder=\"아이디\"]", "Tab")

    # Fill [placeholder="비밀번호"]
    page.fill("[placeholder=\"비밀번호\"]", USER_PW)

    # Press Tab
    page.press("[placeholder=\"비밀번호\"]", "Tab")

    # Press Enter
    # with page.expect_navigation(url="https://ol.dhlottery.co.kr/olotto/game/game645.do"):
    with page.expect_navigation():
        page.press("form[name=\"jform\"] >> text=로그인", "Enter")

    time.sleep(5)

    page.goto(url="https://ol.dhlottery.co.kr/olotto/game/game645.do")
    # "비정상적인 방법으로 접속하였습니다. 정상적인 PC 환경에서 접속하여 주시기 바랍니다." 우회하기
    page.locator("#popupLayerAlert").get_by_role("button", name="확인").click()
    print(page.content())

    # Click text=자동번호발급
    page.click("text=자동번호발급")
    #page.click('#num2 >> text=자동번호발급')

    # 구매할 개수를 선택
    # Select 1
    page.select_option("select", str(COUNT))

    # Click text=확인
    page.click("text=확인")

    # Click input:has-text("구매하기")
    page.click("input:has-text(\"구매하기\")")

    time.sleep(2)
    # Click text=확인 취소 >> input[type="button"]
    page.click("text=확인 취소 >> input[type=\"button\"]")

    # Click input[name="closeLayer"]
    page.click("input[name=\"closeLayer\"]")
    # assert page.url == "https://el.dhlottery.co.kr/game/TotalGame.jsp?LottoId=LO40"

    # 오늘 구매한 복권 결과
    now_date = __get_now().date().strftime("%Y%m%d")
    page.goto(
        url=f"https://dhlottery.co.kr/myPage.do?method=lottoBuyList&searchStartDate={now_date}&searchEndDate={now_date}&lottoId=&nowPage=1"
    )
    a_tag_href = page.query_selector(
        "tbody > tr:nth-child(1) > td:nth-child(4) > a"
    ).get_attribute("href")
    detail_info = re.findall(r"\d+", a_tag_href)
    page.goto(
        url=f"https://dhlottery.co.kr/myPage.do?method=lotto645Detail&orderNo={detail_info[0]}&barcode={detail_info[1]}&issueNo={detail_info[2]}"
    )
    result_msg = ""
    for result in page.query_selector_all("div.selected li"):
        result_msg += ", ".join(result.inner_text().split("\n")) + "\n"
    send_message(f"이번주 나의 행운의 번호는?!\n{result_msg}")

    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
