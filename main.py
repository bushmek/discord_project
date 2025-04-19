import time
import os

import requests
from dotenv import load_dotenv

load_dotenv()

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


def get_match_info(match_id):
    match_info = requests.get(
        f"https://open.faceit.com/data/v4/matches/{match_id}", headers=headers
    )
    return match_info.json()


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
    elo = None

    while True:
        match = get_last_match(PLAYER_ID)
        match_id = match["match_id"]
        match_status = match["status"]
        discord_msg = ""

        if last_match_id and last_match_id != match_id:
            elo = get_player_elo(PLAYER_ID)
            if get_player_team(match) == match["results"]["winner"]:
                discord_msg = f"🎮 Володя закінчив грати... і виграв. Привітання в чат 🎉\nElo: {elo} 🤓"
            else:
                discord_msg = (
                    f"🎮 Володя закінчив грати... і програв. Анлука 😞\nElo: {elo} 🤡"
                )
            requests.post(WEBHOOK_LINK, json={"content": discord_msg})

        if match_status != "ongoing":
            last_match_id = match_id

        time.sleep(90)


if __name__ == "__main__":
    main()


# print(match.json()["items"][0])
# with open("data.json",'w') as file:
#     json.dump(match.json(), file, indent=4)
