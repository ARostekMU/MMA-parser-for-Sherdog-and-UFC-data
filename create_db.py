import json

from sherdog_parser import scrape_all_fighters


db_name = "sherdog_db_part2"

with open(f"sherdog_db.json", 'r') as file:
    data = json.load(file)

if data == {}:
    last_figter_id = 0
else:
    last_entry = next(reversed(data.keys()))
    last_figter_id = data[last_entry]["id"]

scrape_all_fighters(filename=db_name, filetype="json", fighter_index=last_figter_id+1)
