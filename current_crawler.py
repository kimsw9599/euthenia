# -*- encoding: utf-8 -*-

import sys
import requests
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error
from decimal import *
#from slacker import Slacker
from slack import WebClient
import json


# 우리은행 일별 환율 https://svc.wooribank.com/svc/Dream?withyou=CMCOM0184

myothercontext = Context(prec=3, rounding=ROUND_HALF_DOWN)
setcontext(myothercontext)

EXPECTED_USD = 1193.0
EXPECTED_HIGH_USD=1243.0
DATABASE = r"./exchage_rate.db"

conn = None
slack_m = None
channel_name = "#newfun"
channel_name_noti = "#newfun1"
user_name = "NewFun" #sunfun2"


def set_slacker(token):
#    slack_m = Slacker(token)
    slack_m = WebClient(token)
    return slack_m


def get_slack_token():
    f = open("./slack_token", 'r')
    token = f.readline()
    print(token)
    f.close()

    return token.strip()


def send_slack_alart_mesg(slack_m, current_usd, last_usd):
    if slack_m is not None:
        message = "<@sunfun>  Last $1:{} => Current $1:{}".format(str(last_usd), str(current_usd))
        attachments = [{
            "color": "#ff0000",
            "title": "Check Currency",
            "text" : message 
            }]
#        msg=slack_m.chat.post_message(channel_name, message, username="QuantSun")
        msg = slack_m.chat_postMessage(
                  channel=channel_name_noti
                , username=user_name
                , icon_emoji=":dart:"
                , attachments=attachments)	
        print("---------")
        print(msg)
    else:
        print("??????")


def send_slack_info_mesg(slack_m, current_usd, last_usd):
    if slack_m is not None:
        message = "Last $1:{} => Current $1:{}".format(str(last_usd), str(current_usd))

        msg = slack_m.chat_postMessage(
                channel=channel_name, 
                username=user_name, icon_emoji=":dart:", text=message)	
        #msg = slack_m.chat.post_message(channel_name, message, username="QuantSun")
        print(msg)
    else:
        print("??????")


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("open database")
    except Error as e:
        print(e)
 
    return conn


def get_last_usd(conn):
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT currency_value FROM tbl_currency2 where currency_name='USD' order by crawl_date desc limit 1")

        rows = cur.fetchall()
        print(rows)
        if len(rows) > 0:
            return rows[0][0]
        else:
            return -1
    else:
        return -1


def save_last_usd(conn, current_usd):
    # SQLite를 활용해서 저장하기 
    sql = "insert into tbl_currency2 (currency_name, currency_value) values('USD', ?)"

    cur = conn.cursor()
    cur.execute(sql, (str(current_usd),))
    conn.commit()
    return cur.lastrowid


def get_usd():
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/71.0.3578.98 Safari/537.36User-Agent"
    }

    # url = "https://search.daum.net/search?w=tot&DA=UME&t__nil_searchbox=suggest&sug=&sugo=15&sq=%ED%99%98%EC%9C%A8&o=1&q=%ED%99%98%EC%9C%A8"
    url = "https://search.daum.net/search?nil_suggest=sugsch&w=tot&DA=EKS&sug=totex&q=%EB%8B%AC%EB%9F%AC%20%ED%99%98%EC%9C%A8%EC%A1%B0%ED%9A%8C"

    response = requests.get(url, headers=headers)

    usd = 0.0
    if response.status_code == 200:
        response_text = response.text

        obj = BeautifulSoup(response_text, "html.parser")
        aa = obj.select("div.info_price div.inner_info_price em.txt_num")
        print(aa)
        if aa is not None and len(aa)>0:
            usd = Decimal(aa[0].get_text())
        else:
            print("Cannot crawl USD currency value!!")
        
    return usd


def get_usd2():
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "http://finance.daum.net/exchanges",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/71.0.3578.98 Safari/537.36User-Agent"
    }

    # url = "https://search.daum.net/search?w=tot&DA=UME&t__nil_searchbox=suggest&sug=&sugo=15&sq=%ED%99%98%EC%9C%A8&o=1&q=%ED%99%98%EC%9C%A8"
    url = "http://finance.daum.net/api/exchanges/summaries"

    response = requests.get(url, headers=headers)

    usd = 0.0

    if response.status_code == 200:
        response_text = response.text
        obj = json.loads(response_text)

        if obj["data"] is not None and len(obj["data"]) > 0:
            usd = obj["data"][0]["basePrice"]
        else:
            print(response.status_code)
            print("Cannot crawl USD currency value!!")

    return usd


def main(argv):
    slack_token = get_slack_token()
    slack_m = set_slacker(slack_token)

    conn = create_connection(DATABASE)

    if conn is None:
        print("Error! Can't connect database.")
        return

    last_usd = Decimal(get_last_usd(conn))
    usd = get_usd2()

    print(last_usd)
    print(usd)

    last_usd_s = "%.1f" % (get_last_usd(conn))
    usd_s = str(usd)
    print(usd_s)

    if usd_s != last_usd_s:
        save_last_usd(conn, usd)

        if usd < EXPECTED_USD:
            print("Because current ${} is greater than ${}, this process is skipped.".format(usd, EXPECTED_USD))
            # 지난 번에 수집했던 USD랑 비교해서 가격이 하락 경우엔 slack를 현재 USD 가격을 보낸다.
            if usd < last_usd:
                send_slack_alart_mesg(slack_m, usd, "%.2f" % last_usd)
            send_slack_info_mesg(slack_m, usd, "%.2f" % last_usd)
        elif usd >= EXPECTED_HIGH_USD:
            send_slack_alart_mesg(slack_m, usd, "%.2f" % last_usd)
        else:
            send_slack_info_mesg(slack_m, usd, "%.2f" % last_usd)
    else:
        # send_slack_alart_mesg(slack_m, usd, "%.2f" % last_usd)
        print("Same currency value")


if __name__ == "__main__":
    main(sys.argv[1:])    
