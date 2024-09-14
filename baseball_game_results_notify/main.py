import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from linebot.v3.messaging import ApiClient, Configuration, MessagingApi, PushMessageRequest

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)


def main():
    url = "https://baseball.yahoo.co.jp/npb/schedule/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    game_results = soup.find("div", id="gm_card")
    sections = game_results.find_all("section")
    output = []
    for section in sections:
        league: str = section.find("h1").text
        game_list = section.find_all("li")
        output.append(f"{league}")
        output.append("-------------------")
        for game in game_list:
            stadium = game.find("span", class_="bb-score__venue")
            inning = game.find("p", class_="bb-score__link")
            home_team = game.find("p", class_="bb-score__homeLogo")
            away_team = game.find("p", class_="bb-score__awayLogo")
            score_left = game.find("span", class_="bb-score__score--left")
            score_right = game.find("span", class_="bb-score__score--right")
            if stadium and inning and home_team and away_team and score_left and score_right:
                output.append(f"{stadium.text}  {inning.text}")
                output.append(f"{home_team.text}  | {score_left.text} - {score_right.text} | {away_team.text}\n")
    output.append(f"{url}")
    output_text = "\n".join(output)
    print(output_text)
    message_dict = {
        "to": LINE_USER_ID,
        "messages": [
            {"type": "text", "text": "今日の結果です"},
            {"type": "text", "text": output_text},
        ],
    }

    with ApiClient(configuration) as api:
        api_instance = MessagingApi(api)
        push_message_request = PushMessageRequest.from_dict(message_dict)
        try:
            res = api_instance.push_message(push_message_request)
            print(f"Successful sending: {res}")
        except Exception as e:
            print(f"Exception : {e}")


if "__main__" == __name__:
    main()
