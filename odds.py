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
        draws = 0

        for match in self.matches:
            if match.date < date:
                weight = 1

                if match.result == "win":
                    wins += 1*weight
                elif match.result == "loss":
                    losses += 1*weight
                elif match.result == "draw":
                    draws += 1*weight

        # ensure no division by zero error occurs by checking if losses are zero
        weighted_win_rate = (wins + 0.5 * draws)/sum((wins, losses, draws))

        print(self.name, "weighted_win_rate", weighted_win_rate, "wins", wins, "losses", losses, "draws", draws)
        return weighted_win_rate

    def calculate_odds(self, opponent: "Fighter", date: date) -> None:
        wr1 = self.evaluate(date=date)
        wr2 = opponent.evaluate(date=date)

        fighter1_chance = wr1/(wr1+wr2)
        fighter2_chance = wr2/(wr1+wr2)

        print("Chances to win")
        print(self.name, "vs", opponent.name)
        print(f"{fighter1_chance*100} %", "vs", f"{fighter2_chance*100} %")
        print(f"sum {fighter1_chance+fighter2_chance}")


@dataclass
class Match():
    opponent: str # Fighter name
    result: str # win, loss, draw
    date: date


fighter1 = Fighter.load_from_db(name="Patrick Smith")
print(fighter1)
fighter2 = Fighter.load_from_db(name="Mark Walker")
print(fighter2)

fighter1.calculate_odds(opponent=fighter2, date=date(2003, 4, 29))
#fighter2.calculate_odds(opponent=fighter1, date=date(2001, 4, 29))