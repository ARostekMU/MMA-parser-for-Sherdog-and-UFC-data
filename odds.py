import json
import random

from datetime import date, datetime
from dataclasses import dataclass


with open("sherdog_db.json", 'r') as file:
    data = json.load(file)


class FighterNotFound(Exception):
    pass


@dataclass
class Fighter():
    name: str
    matches: ["Match"]

    @classmethod
    def load_from_db(cls, name: str) -> "Fighter":
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
            raise FighterNotFound(f"No data available for {name}")
        
        return cls(name=name, matches=match_objs)
    
    def evaluate(self, date: date, remaining_depth: int, default_weighted_win_rate: float) -> float:
        print(f"evaluating {self.name}")

        wins = 0
        weighted_wins = 0
        losses = 0
        weighted_losses = 0
        draws = 0
        weighted_draws = 0

        for match in self.matches:
            if match.date < date:
                if remaining_depth >= 1:
                    try:
                        opponent = Fighter.load_from_db(name=match.opponent)
                        weight = 2*opponent.evaluate(date=match.date, remaining_depth=remaining_depth-1, default_weighted_win_rate=default_weighted_win_rate)
                    except FighterNotFound:
                        weight = 1
                else:
                    weight = 1

                if match.result == "win":
                    wins += 1
                    weighted_wins += 1*weight
                elif match.result == "loss":
                    losses += 1
                    weighted_losses += 1*weight
                elif match.result == "draw":
                    draws += 1
                    weighted_draws += 1*weight

        try:
            weighted_win_rate = (weighted_wins + 0.5 * weighted_draws)/sum((weighted_wins, weighted_losses, weighted_draws))
            win_rate = (wins + 0.5 * draws)/sum((wins, losses, draws))
        except ZeroDivisionError:
            weighted_win_rate = default_weighted_win_rate
            win_rate = default_weighted_win_rate

        print(self.name)
        print("win_rate", win_rate, "wins", wins, "losses", losses, "draws", draws)
        print("weighted_win_rate", weighted_win_rate, "weighted_wins", weighted_wins, "weighted_losses", weighted_losses, "weighted_draws", weighted_draws)
        return weighted_win_rate

    def calculate_odds(self, opponent: "Fighter", date: date, depth: int, default_weighted_win_rate: float) -> None:
        wr1 = self.evaluate(date=date, remaining_depth=depth, default_weighted_win_rate=default_weighted_win_rate)
        wr2 = opponent.evaluate(date=date, remaining_depth=depth, default_weighted_win_rate=default_weighted_win_rate)

        try:
            fighter1_chance = wr1/(wr1+wr2)
            fighter2_chance = wr2/(wr1+wr2)
        except ZeroDivisionError:
            fighter1_chance = 0.5
            fighter2_chance = 0.5

        print("Chances to win")
        print(self.name, "vs", opponent.name)
        print(f"{fighter1_chance*100} %", "vs", f"{fighter2_chance*100} %")
        print(f"sum {fighter1_chance+fighter2_chance}")

        return fighter1_chance, fighter2_chance


@dataclass
class Match():
    opponent: str # Fighter name
    result: str # win, loss, draw
    date: date


#fighter1 = Fighter.load_from_db(name="Trinity Boykin")
#fighter2 = Fighter.load_from_db(name="Ted Opalinski")
#
#fighter1.calculate_odds(opponent=fighter2, date=date(2001, 3, 24), depth=1)
#fighter2.calculate_odds(opponent=fighter1, date=date(2001, 4, 29))


def test_algo(depth: int, samples: int, uncertainty: float, default_weighted_win_rate: float):
    predicted = 0
    not_found = 0
    uncertain = 0

    fighters = [Fighter.load_from_db(name=name) for name in random.sample(list(data.keys()), samples)]
    for fighter in fighters:
        match = random.choice(fighter.matches)
        print("Real match", match.opponent, match.date, match.result)

        try:
            opponent = Fighter.load_from_db(name=match.opponent)
        except FighterNotFound:
            not_found += 1
            continue
        f1chance, f2chance = fighter.calculate_odds(opponent=opponent, date=match.date, depth=depth, default_weighted_win_rate=default_weighted_win_rate)

        if f1chance < 0.5+uncertainty and f1chance > 0.5-uncertainty:
            uncertain += 1
            continue


        if f1chance > f2chance and match.result == "win":
            predicted += 1
        elif f1chance < f2chance and match.result == "loss":
            predicted += 1

    print("samples", samples)
    print("uncertain", uncertain)
    print("predicted", predicted)
    print("not_found", not_found)
    print("success rate", f"{predicted/(samples-not_found-uncertain)*100} %")

test_algo(depth=1, samples=1000, uncertainty=0.05, default_weighted_win_rate=0.5)
