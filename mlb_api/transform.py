from src.extract import fetch_game_by_date, fetch_telemetry
import json

# helper functions
def safe_float(val):
    try:
        return float(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def safe_int(val):
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None
    

def parse_game_hits(telemetry_json):
    '''
    1. Identifiers
        - Game ID 
        - Play ID
    2. Context & Team
        - Team
        - Opp Team
        - Inning
        - Half Inning (e.g. top)
    3. People & Outcome
        - Batter & Pitcher
        - Event (e.g. homerun, single, flyout, etc.)
        - Description of Event
    4. Statcast Telemetry
        - Exit Velo, Launch Angle, Distance, etc.
    '''

    output = []

    game_pk = telemetry_json["gamePk"]
    home_team = telemetry_json.get("gameData", {}).get("teams", {}).get("home", {}).get("name", "")
    away_team = telemetry_json.get("gameData", {}).get("teams", {}).get("away", {}).get("name", "")

    plays = telemetry_json.get("liveData", {}).get("plays", {})

    for play in plays.get("allPlays", []):
        half_inning = play.get("about", {}).get("halfInning","")
        inning = safe_int(play.get("about", {}).get("inning", ""))

        # batter & pitcher
        batter = play.get("matchup", {}).get("batter", {}).get("fullName", "")
        pitcher = play.get("matchup", {}).get("pitcher", {}).get("fullName", "")

        # play outcome
        event = play.get("result", {}).get("event", "")
        event_description = play.get("result", {}).get("description", "")

        # loop through all plays and finds all batted balls that have hitData and collect them into a list of clean dictionaries
        for play_event in play.get("playEvents", []):
            play_id = play_event.get("playId", "")
            event_hit_data = play_event.get("hitData", {})

            if event_hit_data:
                launch_speed = safe_float(event_hit_data.get("launchSpeed", ""))
                launch_angle = safe_float(event_hit_data.get("launchAngle", ""))
                distance = safe_int(event_hit_data.get("totalDistance", ""))

                if safe_float(launch_speed) is not None and safe_float(launch_speed) >= 95.0:
                    is_hard_hit = True
                else:
                    is_hard_hit = False
                
                if half_inning == "top":
                    batting_team = away_team
                    fielding_team = home_team
                else:
                    batting_team = home_team
                    fielding_team = away_team

                parsed_data = {
                    "game_pk": game_pk,
                    "play_id": play_id, 
                    "team": batting_team,
                    "opp_team": fielding_team,
                    "inning": inning,
                    "half_inning": half_inning,
                    "batter": batter,
                    "pitcher": pitcher,
                    "event": event,
                    "description": event_description,
                    "exit_velocity": launch_speed,
                    "launch_angle": launch_angle,
                    "distance": distance,
                    "is_hard_hit": is_hard_hit
                    }

                output.append(parsed_data)

    return output


# if __name__ == "__main__":
#     games = fetch_game_by_date("2026-09-16")

#     # for game in games:
#     #     telemetry = fetch_telemetry(game["game_pk"])
#     #     hits = parse_game_hits(telemetry)

#     #     print(telemetry["gamePk"])
#     #     print(hits)

#     if games:
#         first_game = games[0]

#         telemetry = fetch_telemetry(first_game["game_pk"])

#         output = parse_game_hits(telemetry)

#         sort_by_exit_velo = sorted(output, key=lambda x: x["exit_velocity"], reverse=True)
#         top_three_hard_hits = sort_by_exit_velo[:3]
#         print(json.dumps(top_three_hard_hits, indent=2))

#         homer_events = [item for item in output if item["event"] == "Home Run"]
#         sort_by_distance = sorted(homer_events, key=lambda x: x["distance"], reverse=True)
#         top_three_longest_hr = sort_by_distance[:3]
#         print(json.dumps(top_three_longest_hr, indent=2))