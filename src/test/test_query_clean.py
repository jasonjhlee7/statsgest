import requests

url = "https://statsapi.mlb.com/api/v1/schedule"

def query_game(date):
    params = {
        "sportId": 1,
        "date": date,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    games = [
        game 
        for schedule_date in data.get("dates",[]) 
        for game in schedule_date.get("games", [])
        ]

    for game_number, game in enumerate(games, start=1):
        game_pk = game.get("gamePk")
        home = game["teams"]["home"]["team"]["name"]
        away = game["teams"]["away"]["team"]["name"]

        print(f"Game {game_number}: {away} @ {home}, gamePk = {game_pk}")


    
        

(query_game("2026-09-16"))