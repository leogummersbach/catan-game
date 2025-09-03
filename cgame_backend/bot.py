import random
import time

import requests

from game import *
from packer import *

class Bot(Player):
    def __init__(self, color: str, key: int):
        super().__init__(color)
        self.color: str = color
        self.active_player: str = ""
        self.state: GameState = GameState.END
        self.key = key
        self.address: str = f"http://localhost:8000/cgameapi/games/{self.key}/"

    def load(self):
        response = requests.get(self.address + "meta")
        while response.status_code == 404:
            time.sleep(1)
            print("try again..")
            response = requests.get(self.address + "meta")
        meta = response.json()
        self.state = meta["state"]
        self.active_player = meta["active_player"]

    def place_random_settlement(self):
        game = readGame(self.key)
        locations = game.map.corners
        locations = list(filter(lambda x: x.owner.color == "shadow", locations.values()))
        location = random.choice(locations)
        requests.put(self.address + f"move/settlement_build/{self.color}/{location.x}/{location.y}/{location.where}")

    def place_random_street(self):
        game = readGame(self.key)
        locations = game.map.edges
        locations = list(filter(lambda x: x.owner.color == "shadow", locations.values()))
        location = random.choice(locations)
        requests.put(self.address + f"move/street_build/{self.color}/{location.x}/{location.y}/{location.where}")

    def return_random_cards(self, amount):
        game = readGame(self.key)
        me = list(filter(lambda player: player.color == self.color, game.players))[0]
        left = amount

        wood = 0
        if me.inventory.wood >= left:
            wood = left
        else:
            wood = me.inventory.wood
        left -= wood

        clay = 0
        if me.inventory.clay >= left:
            clay = left
        else:
            clay = me.inventory.clay
        left -= clay

        sheep = 0
        if me.inventory.sheep >= left:
            sheep = left
        else:
            sheep = me.inventory.sheep
        left -= sheep

        wheat = 0
        if me.inventory.wheat >= left:
            wheat = left
        else:
            wheat = me.inventory.wheat
        left -= wheat

        ore = 0
        if me.inventory.ore >= left:
            ore = left
        else:
            ore = me.inventory.ore
        left -= ore

        return wood, clay, sheep, wheat, ore

    def get_robable(self):
        g = readGame(self.key)
        x = None
        y = None
        for field_key in g.map.field_figures:
            field = g.map.field_figures[field_key]
            if field.type == "robber":
                x = field_key[0]
                y = field_key[1]
        to_draw = g.map.getAdjacentPlayersForField(x, y)
        return list(filter(lambda color: g.players[g.active_player].color != color, to_draw))

    def mainloop(self):
        while True:
            time.sleep(0.1)
            print(f"reload bot {self.color}..")
            self.load()
            if self.active_player == self.color:
                if self.state == 1:
                    requests.put(self.address + f"move/dice_throw/{self.color}")
                elif self.state == 2:
                    self.place_random_settlement()
                    print(f"bot {self.color} placed a settlements")
                    self.load()
                    self.place_random_street()
                    print(f"bot {self.color} placed a street")
                elif self.state == 3:
                    requests.put(self.address + f"move/dice_throw/{self.color}")
                elif self.state == 4:
                    requests.put(self.address + f"move/end/{self.color}")
                elif self.state == 5:
                    requests.put(self.address + f"move/move_robber/{self.color}/{0}/{0}")
                elif self.state == 6:
                    amount = readGame(self.key).compute_returns[self.color]
                    wood, clay, sheep, wheat, ore = self.return_random_cards(amount)
                    requests.put(self.address + f"move/return_cards/{self.color}/{wood}/{clay}/{sheep}/{wheat}/{ore}")
                elif self.state == 7:
                    robable = self.get_robable()
                    rob = random.choice(robable)
                    requests.put(self.address + f"move/rob_player/{self.color}/{rob}")
                elif self.state == 8:
                    requests.put(self.address + f"move/reply_to_active_trade/{self.color}/0")
