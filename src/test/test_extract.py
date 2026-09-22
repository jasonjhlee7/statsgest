import requests
import json
import random

url = "https://statsapi.mlb.com/api/v1/schedule"
params = {
    "sportId": 1,
    "date": "2024-06-01",
}

response = requests.get(url, params=params)
data = response.json()

def write_response():
    

    with open ("test_response.json", "w") as f:
        json.dump(data, f, indent=2)


# Print telemetry of a game using gamePk
def write_telemetry():
    games = [
        game
        for date in data.get("dates", [])
        for game in date.get("games", [])
    ]

    game_Pk = random.choice(games)["gamePk"]

    telemetry = requests.get(f"https://statsapi.mlb.com/api/v1.1/game/746952/feed/live")

    with open ("test_telemetry.json", "w") as f:
        json.dump(telemetry.json(), f, indent=2)

write_telemetry()