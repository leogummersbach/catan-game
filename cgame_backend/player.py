from inventory import Inventory


class Player:
    def __init__(self, color: str, game_mode: str = "standard"):
        self.color = color
        self.inventory = Inventory(color, game_mode)
        self.last_dice = 0
        self.inventory_threshold = 7
        self.knights = 0

    def __repr__(self):
        return self.color
