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
    