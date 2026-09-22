import requests, json #json unused

url = "https://statsapi.mlb.com/api/v1/schedule"

def query_game(date):
    params = {
        "sportId": 1,
        "date": date,
    }

    response = requests.get(url, params=params) #raise status is missing
    data = response.json()
    games = data["dates"][0]["games"]#crashed when no games are scheduled

    game_number = 1 #game_number can be replaced with enum
    for game in games:
        gamePk = game.get("gamePk") #gamePk should conventionally be game_pk
        home = game["teams"]["home"]["team"]["name"]
        away = game["teams"]["away"]["team"]["name"]
        print(f"Game {game_number}: {away} @ {home}, gamePk = {gamePk}")
        game_number += 1

print(query_game("2026-09-16")) #Prints None because it already prints inside loop