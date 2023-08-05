import json

from sherdog_parser import scrape_all_fighters


db_name = "sherdog_db"

with open(f"{db_name}.json", 'r') as file:
    data = json.load(file)

last_entry = next(reversed(data.keys()))

last_figter_id = data[last_entry]["id"]

scrape_all_fighters(filename=db_name, filetype="json", fighter_index=last_figter_id)