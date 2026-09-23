import os
import requests
from dotenv import load_dotenv

load_dotenv()
webhook_url = os.getenv("DISCORD_WEBHOOK_URL")


'''
Formatter:

    Responsibility: Loop through those hits, format them into human-readable strings 
                    (e.g. batter, speed, distance), and assemble Discord's JSON payload.
    
    Discord's Embed Structure: Discord expects a dictionary with:
        title (string)
        description (string)
        fields (a list of dictionaries, where each dict has a "name" and a "value")
    
    Output: A dictionary ready to be sent as JSON.

Sender:

    Input: The payload dictionary and your webhook URL (loaded from .env or os.getenv).

    Responsibility: Send a POST request using requests and raise an error if Discord rejects it.
'''

def build_discord_payload(team_name, date, hardest_hits, homers):
    """
    Takes the real query results from get_team_digest() and builds
    a formatted Discord embed dictionary.
    """
    
    # 1. Format the Top 3 Hardest Hits text (e.g. "1. Shohei Ohtani - 114.2 mph (Single)")
    away_team = hardest_hits[0]["opp_team"]
    hard_hits_lines = []
    for index, hit in enumerate(hardest_hits, start=1):
        hard_hits_text = f"{index}. {hit['batter']} - {hit['exit_velocity']} mph ({hit['event']})"
        hard_hits_lines.append(hard_hits_text)

    hard_hits_msg = "\n".join(hard_hits_lines) if hard_hits_lines else "No hard hits recorded."
    

    homers_lines = []
    for index, homer in enumerate(homers, start=1):
        homer_text = f"{index}. **{homer['batter']}** — {homer['distance']} feet"
        homers_lines.append(homer_text)

    homers_msg = "\n".join(homers_lines) if homers_lines else "No homers recorded."

    payload = {
        "username": "MLB Statcast Bot ⚾",
        "embeds": [
            {
                "title": f"⚾ Game Recap: {team_name} vs {away_team}",
                "description": f"Statcast telemetry highlights for **{date}**",
                "color": 3447003,  # Dodger/Yankee Blue hex integer
                "fields": [
                    {
                        "name": "🚀 Hardest Hits (≥ 95 mph)",
                        "value": hard_hits_msg,
                        "inline": False
                    },
                    {
                        "name": "💣 Home Runs",
                        "value": homers_msg,
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Powered by Apache Airflow & DuckDB"
                }
            }
        ]
    }

    return payload


def send_discord_digest(payload, webhook_url=None):
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")

    if not url:
        raise ValueError("DISCORD_WEBHOOK_URL is not set!")
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    print("Digest sent successfully!")



if __name__ == "__main__":
    from src.load import get_team_digest

    team = "Los Angeles Dodgers"
    hard_hits, homers = get_team_digest(team_name=team)

    payload = build_discord_payload(
        team_name=team,
        date="2026-09-18",
        hardest_hits=hard_hits,
        homers=homers
    )

    send_discord_digest(payload=payload)