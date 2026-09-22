import json

with open ("/Users/jasonlee/Desktop/statsgest/test_telemetry.json", "r") as f:
    telemetry_json = json.load(f)

    types_of_results = set()
    eventType = set()
    types_of_trajectory = set()
    hardness = set()

    for play in telemetry_json.get("liveData", {}).get("plays", {}).get("allPlays", []):
        types_of_results.add(play.get("result", {}).get("type", ""))
        eventType.add(play.get("result", {}).get("eventType", ""))

        for playEvent in play.get("playEvents", []):
            hit_data = playEvent.get("hitData")
            if hit_data:
                types_of_trajectory.add(hit_data.get("trajectory", ""))
                hardness.add(hit_data.get("hardness", ""))


print(types_of_results)
print(eventType)
print(types_of_trajectory)
print(hardness)