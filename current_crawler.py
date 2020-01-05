# -*- encoding: utf-8 -*-

import sys
import requests
from bs4 import BeautifulSoup

EXPECTED_USD = 1155.0

def get_usd():
    url = "https://search.daum.net/search?w=tot&DA=UME&t__nil_searchbox=suggest&sug=&sugo=15&sq=%ED%99%98%EC%9C%A8&o=1&q=%ED%99%98%EC%9C%A8"

    response = requests.get(url)

    usd = 0.0
    if response.status_code == 200:
        response_text = response.text

        obj = BeautifulSoup(response_text, "html.parser")
        aa = obj.select("div.stock_up.inner_price em.txt_num")
        if aa is not None and len(aa)>0:
            usd = float(aa[0].get_text())
        
    return usd

def get_last_usd():
    last_usd = 0.0
    return last_usd

def save_last_usd(current_usd):
    # SQLite를 활용해서 저장하기 
    pass

def send_slack_alart_mesg(current_usd, last_usd):
    pass

def send_slack_info_mesg(current_usd, last_usd):
    pass

def main(argv):
    # US 달러를 가져온다. 
    usd = get_usd()
    print(usd)

    # 가져온 USD가 기준 점 이하인가 체크한다. 
    if usd < EXPECTED_USD:
        # 지난 번에 수집했던 USD랑 비교해서 가격이 하락 경우엔 slack를 현재 USD 가격을 보낸다. 
        last_usd = get_last_usd()
        if last_usd > usd:
            send_slack_alart_mesg(usd, last_usd)
        else:
            send_slack_info_mesg(usd, last_usd)
    else:
        print("Because current ${} is greater than ${}, this process is skipped.".format(usd, EXPECTED_USD))

    save_last_usd(usd)


if __name__ == "__main__":
    main(sys.argv[1:])    