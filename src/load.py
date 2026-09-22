import json
import duckdb
import pandas as pd
from pathlib import Path
from mlb_api.transform import parse_game_hits
from src.extract import fetch_game_by_date, fetch_telemetry

def create_tables(db_path="data/statcast.duckdb"):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(db_path)) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS hits (
                game_pk BIGINT,
                play_id VARCHAR,
                team VARCHAR,
                opp_team VARCHAR,
                inning SMALLINT,
                half_inning VARCHAR,
                batter VARCHAR,
                pitcher VARCHAR,
                event VARCHAR,
                description VARCHAR,
                exit_velocity DOUBLE,
                launch_angle DOUBLE,
                distance INTEGER,
                is_hard_hit BOOL,
                PRIMARY KEY (game_pk, play_id)
            )
        """)
    return db_path


def save_hits(hits_list, db_path="data/statcast.duckdb"):
    '''
    Takes list of dictionaries.
    If the list is empty, return early.
    Deletes previous rows for those game_pks to ensure idempotency.
    Inserts the new rows into the hits table. 
    (Hint: In DuckDB, if you convert your list of dicts to a Pandas DataFrame 
    df = pd.DataFrame(hits_list), you can literally run:
    conn.execute("INSERT INTO hits SELECT * FROM df")!)
    '''

    if not hits_list:
        return db_path

    '''
    with duckdb.connect(str(db_path)) as con:
        df = pd.DataFrame(hits_list)
        for hit_dict in hits_list:
            game_pk = hit_dict["game_pk"]
            
            con.execute(f"""
            DELETE FROM hits 
            WHERE EXISTS (
                SELECT * FROM hits
                WHERE game_pk = {game_pk}
            )""")
            con.register("df", df)
            con.execute("INSERT INTO hits SELECT * FROM df")
        con.close()
    '''
    with duckdb.connect(str(db_path)) as conn:
        df = pd.DataFrame(hits_list)

        game_pks = sorted({int(hit["game_pk"]) for hit in hits_list})
        if game_pks:
            placeholders = ", ".join("?" for _ in game_pks)
            conn.execute(
                f"DELETE FROM hits WHERE game_pk IN ({placeholders})", game_pks
            )
        conn.register("df", df)
        # conn.execute("INSERT INTO hits SELECT * FROM df")
        conn.execute("INSERT INTO hits BY NAME SELECT * FROM df") # to avoid schema inconsistencies


    return db_path


def get_team_digest(team_name, game_pk=None, db_path="data/statcast.duckdb"):
    '''
    Runs a SQL query to fetch:
    Top 3 hardest hits by that team (ordered by exit_velocity DESC).
    Any home runs hit by that team (ordered by distance DESC).
    Returns those records so the Discord notifier can format them!
    '''
    with duckdb.connect(str(db_path)) as conn:
        params = [team_name]

        query = "SELECT * FROM hits WHERE team = ?"

        if game_pk is not None:
            query += " AND game_pk = ?"
            params.append(game_pk)

        hardest_hits = query + " AND exit_velocity IS NOT NULL AND exit_velocity >= 95.0 ORDER BY exit_velocity DESC LIMIT 3"
        homers = query + " AND distance IS NOT NULL AND event = 'Home Run' ORDER BY distance DESC"

        
        # hard_hits_output = conn.execute(hardest_hits, params).fetchall()
        # homers_output = conn.execute(homers, params).fetchall()
        # fetchall turns output into tuples; instead return dictionary
        hard_hits_output = conn.execute(hardest_hits, params).df().to_dict(orient="records")
        homers_output = conn.execute(homers, params).df().to_dict(orient="records")
        
    return hard_hits_output, homers_output
                



# if __name__ == "__main__":
#     print(create_tables())

#     games = fetch_game_by_date("2026-09-16")

#     for game in games:
#         telemetry = fetch_telemetry(game["game_pk"])
#         output = parse_game_hits(telemetry)

#         save_hits(output)
        # filtered_output = [
        #     item for item in output
        #     if item.get("exit_velocity") is not None and item.get("exit_velocity") >= 95.0]

        # sort_by_exit_velo = sorted(filtered_output, key=lambda x: x["exit_velocity"], reverse=True)
        # top_three_hard_hits = sort_by_exit_velo[:3]

        # homer_events = [
        #     item for item in filtered_output
        #     if item.get("event") == "Home Run" and item.get("distance") is not None]
        
        # sort_by_distance = sorted(homer_events, key=lambda x: x["distance"], reverse=True)
        # top_three_longest_hr = sort_by_distance[:3]

        # save_hits(top_three_hard_hits)
        # save_hits(top_three_longest_hr)

