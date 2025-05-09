import time
import os
import logging
import traceback
import requests
from dotenv import load_dotenv


load_dotenv()
logging.basicConfig(filename='huinya_name.log', level=logging.ERROR)

WEBHOOK_LINK = os.getenv("WEBHOOK_LINK")
FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")
PLAYER_ID = "a793eef2-4a07-49ec-b768-7623a85ce49d"

data = {"content": "test "}

headers = {"Authorization": f"Bearer {FACEIT_API_KEY}"}


def get_last_match(player_id):
    match = requests.get(
        f"https://open.faceit.com/data/v4/players/{player_id}/history",
        headers=headers,
        params={"game": "cs2", "limit": 1},
    )
    return match.json()["items"][0]


def get_match_stat(match_id):
    match_info = requests.get(
        f"https://open.faceit.com/data/v4/matches/{match_id}/stats", headers=headers
    )
    return match_info.json()


def get_last_stat(player_id):
    match_stat = requests.get(f"https://open.faceit.com/data/v4/players/{player_id}/games/cs2/stats", headers=headers, params={"limit": 1},)
    return match_stat.json()['items'][0]

def get_player_elo(player_id):
    elo = requests.get(
        f"https://open.faceit.com/data/v4/players/{player_id}", headers=headers
    )
    return elo.json()["games"]["cs2"]["faceit_elo"]


def get_player_team(match):
    for player in match["teams"]["faction1"]["players"]:
        if player["player_id"] == PLAYER_ID:
            return "faction1"

    for player in match["teams"]["faction2"]["players"]:
        if player["player_id"] == PLAYER_ID:
            return "faction2"

    return None


def main():
    last_match_id = None

    while True:
        match = get_last_match(PLAYER_ID)
        match_id = match["match_id"]
        match_status = match["status"]
        discord_msg = ""

        if last_match_id and last_match_id != match_id:
            elo = get_player_elo(PLAYER_ID)
            stat = get_last_stat(PLAYER_ID)['stats']
            kd_ratio = stat['K/D Ratio']
            kda = f"{stat['Kills']}/{stat['Deaths']}/{stat['Assists']}"
            if get_player_team(match) == match["results"]["winner"]:
                discord_msg = f"🎮 Володя закінчив грати... і виграв. Привітання в чат 🎉"
                if float(kd_ratio) < 1.0:
                    discord_msg += f"\nЧел навіть в КД не вийшов: {kd_ratio} 🤡"
                else:
                    discord_msg += f"\nХарош хочаб в Кд вийшов: {kd_ratio} 🤓"
            else:
                discord_msg = (
                    f"🎮 Володя закінчив грати... і програв. Анлука 😞"
                )
                if float(kd_ratio) < 1.0:
                    discord_msg += f"\nЧел навіть в КД не вийшов: {kd_ratio} 🤡"
                else:
                    discord_msg += f"\nХарош хочаб в Кд вийшов: {kd_ratio} 🤓"
            discord_msg += f"\n👴 Повна статистика: {kda}. Elo: {elo} 👴"
            requests.post(WEBHOOK_LINK, json={"content": discord_msg})

        if match_status != "ongoing":
            last_match_id = match_id

        time.sleep(90)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error("Сталася помилка:\n%s", traceback.format_exc())

# print(match.json()["items"][0])
# with open("data.json",'w') as file:
#     json.dump(match.json(), file, indent=4)
