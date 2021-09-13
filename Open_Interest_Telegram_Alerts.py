
import telegram
import schedule
import time
import datetime as dt

from urllib.request import urlopen
from bs4 import BeautifulSoup
import json


API_Token = '1987736013:AAHIiIvGOoTM71j1EDgIquVYtv-1kECuEZc'
Chat_Id = -1001495701812
bot = telegram.Bot(token = API_Token)

funding_history_before_btc = 0
funding_history_before_usdt = 0
long_history_before_btc = 0
short_history_before_btc = 0



def telegram_send_message(telegram_message):
    bot.send_message(chat_id = Chat_Id, text = telegram_message)

def job():
    
    the_message = ''
    now = dt.datetime.now()
    now_minutes = now.minute
    the_message = "current time = " + str(now)

    if(now_minutes % 5 == 0):
        the_message = longshort_ratio_func()
        if(the_message != ""):
            telegram_send_message(the_message)


def longshort_ratio_func():

    output_text_return = ""
    global funding_history_before_btc
    global funding_history_before_usdt
    global long_history_before_btc
    global short_history_before_btc

    funding_history_raw = urlopen("https://www.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=5m")
    funding_history_parser = BeautifulSoup(funding_history_raw, "html.parser")
    Interest_Datas = str(funding_history_parser)
    Interest_Datas = json.loads(Interest_Datas)


    sumOpenInterest = round(float(Interest_Datas[29]['sumOpenInterest']),3)
    sumOpenInterestValue = int(round(float(Interest_Datas[29]['sumOpenInterestValue']),0))



    if(funding_history_before_btc == 0):
        output_text_return += "미결제 약정\n" + "{:0,.3f}".format(sumOpenInterest) + " BTC ( - )\n\n"

    else:
        if(sumOpenInterest - funding_history_before_btc > 0):
            output_text_return += "미결제 약정\n" + "{:0,.3f}".format(sumOpenInterest) + " BTC (+" + "{:0,.3f}".format(sumOpenInterest - funding_history_before_btc) + ")\n\n"
        
        else:
            output_text_return += "미결제 약정\n" + "{:0,.3f}".format(sumOpenInterest) + " BTC (" + "{:0,.3f}".format(sumOpenInterest - funding_history_before_btc) + ")\n\n"
        



    if(funding_history_before_usdt == 0):
        output_text_return += "미결제 약정의 명목 가치\n" + "{:0,.0f}".format(sumOpenInterestValue) + " USDT ( - )\n\n"

    else:
        if(sumOpenInterestValue - funding_history_before_usdt > 0):
            output_text_return += "미결제 약정의 명목 가치\n" + "{:0,.0f}".format(sumOpenInterestValue) + " USDT (+" + "{:0,.0f}".format(sumOpenInterestValue - funding_history_before_usdt) + ")\n\n"
        
        else:
            output_text_return += "미결제 약정의 명목 가치\n" + "{:0,.0f}".format(sumOpenInterestValue) + " USDT (" + "{:0,.0f}".format(sumOpenInterestValue - funding_history_before_usdt) + ")\n\n"
        


    if(sumOpenInterest == funding_history_before_btc):
        output_text_return = ""
        return output_text_return
        


    funding_history_before_btc = sumOpenInterest
    funding_history_before_usdt = sumOpenInterestValue



    longshort_ratio_raw = urlopen("https://www.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m")

    longshort_ratio_parser = BeautifulSoup(longshort_ratio_raw, "html.parser")
    longshort_ratio_datas = str(longshort_ratio_parser)
    longshort_ratio_datas = json.loads(longshort_ratio_datas)

    longshort_ratio_longAccount = float("{:0,.2f}".format(float(longshort_ratio_datas[29]['longAccount']) * 100))
    longshort_ratio_shortAccount = float("{:0,.2f}".format(float(longshort_ratio_datas[29]['shortAccount']) * 100))



    if(long_history_before_btc == 0):
        output_text_return += "롱 계정 : " + str(longshort_ratio_longAccount) + "% ( - )\n"

    else:
        if(longshort_ratio_longAccount - long_history_before_btc > 0):
            output_text_return += "롱 계정 : " + str(longshort_ratio_longAccount) + "% (+" + str("{:0,.2f}".format(round(longshort_ratio_longAccount - long_history_before_btc))) + ")\n"
        
        else:
            output_text_return += "롱 계정 : " + str(longshort_ratio_longAccount) + "% (" + str("{:0,.2f}".format(round(longshort_ratio_longAccount - long_history_before_btc))) + ")\n"
        


    if(short_history_before_btc == 0):
        output_text_return += "숏 계정 : " + str(longshort_ratio_shortAccount) + "% ( - )"

    else:
        if(longshort_ratio_shortAccount - short_history_before_btc > 0):
            output_text_return += "숏 계정 : " + str(longshort_ratio_shortAccount) + "% (+" + str("{:0,.2f}".format(round(longshort_ratio_shortAccount - short_history_before_btc))) + ")"
        
        else:
            output_text_return += "숏 계정 : " + str(longshort_ratio_shortAccount) + "% (" + str("{:0,.2f}".format(round(longshort_ratio_shortAccount - short_history_before_btc))) + ")"
        


    long_history_before_btc = longshort_ratio_longAccount
    short_history_before_btc = longshort_ratio_shortAccount

    return output_text_return




schedule.every(1).minutes.do(job)


while True:
    schedule.run_pending()
    time.sleep(1)
    
