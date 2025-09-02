from enum import Enum

from inventory import CardInventory
from player import Player


class Trade:
    def __init__(self, player: Player, get: CardInventory, give: CardInventory):
        self.initiator = player
        self.get = get
        self.give = give
        self.responses = {}

    def respond(self, player, respond: bool):
        self.responses[player.color] = respond

    def json(self):
        return {
            "initiator": self.initiator.color,
            "get": self.get.json(),
            "give": self.give.json(),
            "responses": self.responses
        }
