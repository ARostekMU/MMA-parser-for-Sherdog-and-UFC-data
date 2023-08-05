import json
from datetime import date, datetime

from dataclasses import dataclass


@dataclass
class Fighter():
    name: str
    matches: ["Match"]

    @classmethod
    def load_from_db(cls, name: str) -> "Fighter":
        filename = "sherdog_db.json"

        with open(filename, 'r') as file:
            data = json.load(file)

        if name in data:
            matches = data[name]["matches"]
            match_objs = []

            for match in matches:
                match_objs.append(
                    Match(
                        opponent=match["opponent"],
                        result=match["result"],
                        date=datetime.strptime(match["date"], '%b / %d / %Y').date(),
                    )
                )
        else:
            raise Exception(f"No data available for {name}")
        
        return cls(name=name, matches=match_objs)
    
    def evaluate(self, date: date) -> float:
        wins = 0
        losses = 0

        for match in self.matches:
            if match.date < date:
                if match.result == "win":
                    wins += 1
                elif match.result == "loss":
                    losses += 1

        # ensure no division by zero error occurs by checking if losses is zero
        ratio = wins / losses if losses else "Infinity"

        print(self.name, ratio, "wins", wins, "losses", losses)
        return ratio

    def calculate_odds(self, opponent: "Fighter", date: date) -> None:
        self.evaluate(date=date)
        opponent.evaluate(date=date)


@dataclass
class Match():
    opponent: str # Fighter name
    result: str # win, loss, draw
    date: date


fighter1 = Fighter.load_from_db(name="Jim Mullen")
print(fighter1)
fighter2 = Fighter.load_from_db(name="Patrick Smith")
print(fighter2)

fighter1.calculate_odds(opponent=fighter2, date=date(2001, 4, 29))