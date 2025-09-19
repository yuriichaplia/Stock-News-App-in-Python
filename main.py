import pandas
import requests
from os import environ
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
account_sid = environ.get("ACCOUNT_SID")
auth_token = environ.get("AUTH_TOKEN")

url = "https://www.alphavantage.co/query"
parameters = {
    "function" : "TIME_SERIES_DAILY",
    "symbol" : STOCK,
    "apikey" : environ.get("API_KEY")
}

daily_series = requests.get(url=url, params=parameters)
daily_series.raise_for_status()
print(daily_series.json())

if 'Time Series (Daily)' not in daily_series.json():
    print("Error from Alpha Vantage.")
    exit()

daily_series_json = pandas.DataFrame(daily_series.json()['Time Series (Daily)']).transpose()

mark = ""

if float(daily_series_json.iloc[0,3]) > float(daily_series_json.iloc[4,3]):
    step_1 = float(daily_series_json.iloc[0,3]) - float(daily_series_json.iloc[4,3])
    step_2 = (step_1*100)/float(daily_series_json.iloc[0,3])
    mark = "🔺"
elif float(daily_series_json.iloc[4,3]) > float(daily_series_json.iloc[0,3]):
    step_1 = float(daily_series_json.iloc[4,3]) - float(daily_series_json.iloc[0,3])
    step_2 = (step_1*100)/float(daily_series_json.iloc[4,3])
    mark = "🔻"
else:
    step_2 = 0

percent = round(step_2)
print(percent)

if percent >= 5:
    url_2 = "https://newsapi.org/v2/everything"
    parameters_2 = {
        "q": "tesla",
        "apiKey": environ.get("API_KEY_2")
    }

    tesla_news = requests.get(url=url_2, params=parameters_2)
    tesla_news.raise_for_status()
    tesla_news_json = tesla_news.json()

    client = Client(account_sid, auth_token)

    for index in range(0, 3):
        author = f"Author: {tesla_news_json['articles'][index]['author']}"
        title = f"Title: {tesla_news_json['articles'][index]['title']}"
        description = tesla_news_json['articles'][index]['description']
        message_full = f'TSLA: {mark}{percent}%\n{title}\n{description}'

        print(message_full.encode("utf-8"))

        message = client.api.account.messages.create(
            from_=environ.get("TWILIO_PHONE_NUMBER"),
            body = message_full,
            to = environ.get("MY_PHONE_NUMBER")
        )
        print(message.sid)
        print(message.status)