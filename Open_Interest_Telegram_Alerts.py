import telegram
import time
import datetime as dt
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import logging
import socket  # For setting default timeout
from dotenv import load_dotenv  # To load .env file
import os

# Load environment variables
load_dotenv()

API_Token = os.getenv('API_TOKEN')
Chat_Id = os.getenv('CHAT_ID')

if not API_Token or not Chat_Id:
    raise ValueError("API_TOKEN or CHAT_ID is not set in the .env file")

bot = telegram.Bot(token=API_Token)

funding_history_before_btc = 0
funding_history_before_usdt = 0
long_history_before_btc = 0
short_history_before_btc = 0

print("Start Bot")
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logging.info("Bot started")

# Set default timeout for socket operations (e.g., urlopen)
socket.setdefaulttimeout(10)  # Timeout after 10 seconds

def telegram_send_message(telegram_message):
    try:
        bot.send_message(chat_id=Chat_Id, text=telegram_message)
        logging.info(f"Sent message: {telegram_message}")
    except Exception as e:
        print('Error sending message:', e)
        logging.error(f"Error sending message: {e}")

def longshort_ratio_func():
    print("Calculating longshort_ratio_func")
    logging.info("Calculating longshort_ratio_func")
    try:
        output_text_return = ""
        global funding_history_before_btc
        global funding_history_before_usdt
        global long_history_before_btc
        global short_history_before_btc

        funding_history_raw = urlopen(
            "https://www.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=5m"
        )
        funding_history_parser = BeautifulSoup(funding_history_raw, "html.parser")
        Interest_Datas = json.loads(str(funding_history_parser))

        sumOpenInterest = round(float(Interest_Datas[-1]['sumOpenInterest']), 3)
        sumOpenInterestValue = int(round(float(Interest_Datas[-1]['sumOpenInterestValue']), 0))

        if funding_history_before_btc == 0:
            output_text_return += f"Open Interest\n{sumOpenInterest:,.3f} BTC ( - )\n\n"
        else:
            diff = sumOpenInterest - funding_history_before_btc
            output_text_return += f"Open Interest\n{sumOpenInterest:,.3f} BTC ({diff:+,.3f})\n\n"

        if funding_history_before_usdt == 0:
            output_text_return += f"Notional Value of Open Interest\n{sumOpenInterestValue:,.0f} USDT ( - )\n\n"
        else:
            diff_value = sumOpenInterestValue - funding_history_before_usdt
            output_text_return += f"Notional Value of Open Interest\n{sumOpenInterestValue:,.0f} USDT ({diff_value:+,.0f})\n\n"

        if sumOpenInterest == funding_history_before_btc:
            logging.info("No change in Open Interest. Skipping message.")
            return ""

        funding_history_before_btc = sumOpenInterest
        funding_history_before_usdt = sumOpenInterestValue

        longshort_ratio_raw = urlopen(
            "https://www.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m"
        )
        longshort_ratio_parser = BeautifulSoup(longshort_ratio_raw, "html.parser")
        longshort_ratio_datas = json.loads(str(longshort_ratio_parser))

        longAccount = float(longshort_ratio_datas[-1]['longAccount']) * 100
        shortAccount = float(longshort_ratio_datas[-1]['shortAccount']) * 100

        longAccount = round(longAccount, 2)
        shortAccount = round(shortAccount, 2)

        if long_history_before_btc == 0:
            output_text_return += f"Long Account : {longAccount:.2f}% ( - )\n"
        else:
            diff_long = longAccount - long_history_before_btc
            output_text_return += f"Long Account : {longAccount:.2f}% ({diff_long:+.2f})\n"

        if short_history_before_btc == 0:
            output_text_return += f"Short Account : {shortAccount:.2f}% ( - )"
        else:
            diff_short = shortAccount - short_history_before_btc
            output_text_return += f"Short Account : {shortAccount:.2f}% ({diff_short:+.2f})"

        long_history_before_btc = longAccount
        short_history_before_btc = shortAccount

        return output_text_return

    except Exception as e:
        print("Error in longshort_ratio_func:", e)
        logging.error(f"Error in longshort_ratio_func: {e}")
        import traceback
        traceback.print_exc()
        return ''

def wait_until_next_run():
    while True:
        now = dt.datetime.now()
        next_minute = (now.minute // 5 + 1) * 5
        next_hour = now.hour

        if next_minute >= 60:
            next_minute = 0
            next_hour = (now.hour + 1) % 24

        next_run = now.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)
        wait_seconds = (next_run - now).total_seconds()

        if wait_seconds <= 0:
            time.sleep(0.1)
            continue
        print(f"Waiting {wait_seconds:.2f} seconds until next run at {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Waiting {wait_seconds:.2f} seconds until next run at {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(wait_seconds)
        break

def main():
    print("Start")
    logging.info("Main loop started")
    while True:
        try:
            wait_until_next_run()
            the_message = longshort_ratio_func()
            print(f"Message: {the_message}")
            logging.info(f"Generated message: {the_message}")
            if the_message != "":
                telegram_send_message(the_message)
        except Exception as e:
            print(f"Error in main loop: {e}")
            logging.error(f"Error in main loop: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)  # Wait before retrying to avoid rapid failure loops

if __name__ == "__main__":
    main()

