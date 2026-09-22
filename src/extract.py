import requests


SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule"
TELEMETRY_URL = "https://statsapi.mlb.com/api/v1.1/game/{}/feed/live"

'''
Gets game data from MLB Statcasts API using date (YYYY-MM-DD).
Returns home team, away team, and gamePk(game ID) in dictionary format.
'''

def fetch_game_by_date(date):
    params = {
        "sportId": 1,
        "date": date,
    }

    response = requests.get(SCHEDULE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    games = [
        game 
        for schedule_date in data.get("dates",[]) 
        for game in schedule_date.get("games", [])
        ]

    output = []

    for game in games:
        output.append({
            "game_pk": game["gamePk"],
            "home_team": game["teams"]["home"]["team"]["name"],
            "away_team": game["teams"]["away"]["team"]["name"],
        })

    return output


def fetch_telemetry(game_pk):
    response = requests.get(
        TELEMETRY_URL.format(game_pk),
        timeout=10)
    response.raise_for_status()
    return response.json()