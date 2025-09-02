import random
import time

import requests

from game import *


class Bot(Player):
    def __init__(self, color: str, game: Game):
        super().__init__(color)
        self.color: str = color
        self.active_player: str = ""
        self.state: GameState = GameState.END
        self.game = game
        self.address: str = "http://localhost:8000/cgameapi/"

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
        locations = self.game.map.corners
        locations = list(filter(lambda x: x.owner.color == "shadow", locations.values()))
        location = random.choice(locations)
        requests.put(self.address + f"move/settlement_build/{self.color}/{location.x}/{location.y}/{location.where}")

    def place_random_street(self):
        locations = self.game.map.edges
        locations = list(filter(lambda x: x.owner.color == "shadow", locations.values()))
        location = random.choice(locations)
        requests.put(self.address + f"move/street_build/{self.color}/{location.x}/{location.y}/{location.where}")

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
