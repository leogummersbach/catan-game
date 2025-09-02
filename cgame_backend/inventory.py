import random

from developments import EmptyDevelopments


class CardInventory:
    def __init__(self, game_mode: str = "standard"):
        # standard
        self.sheep = 0
        self.wood = 0
        self.ore = 0
        self.clay = 0
        self.wheat = 0

    def json(self):
        return {"wheat": self.wheat, "ore": self.ore, "clay": self.clay, "wood": self.wood,
                "sheep": self.sheep}

    def cardNames(self):
        return ["sheep", "wood", "ore", "clay", "wheat"]

    def fromDict(self, d):
        for key in d:
            if key in self.cardNames():
                setattr(self, key, d[key])

    def size(self):
        sum = 0
        for prop in self.cardNames():
            sum += getattr(self, prop)
        return sum


class Inventory(CardInventory):
    def __init__(self, owner: str, game_mode: str = "standard"):
        # standard
        super().__init__(game_mode)
        self.owner = owner
        self.streets = 15
        self.settlements = 5
        self.cities = 4
        self.bank_trade_costs = {}
        for itemName in self.cardNames():
            self.bank_trade_costs[itemName] = 4
        self.hidden_developments = EmptyDevelopments()

    def json(self):
        return {"owner": self.owner, "wheat": self.wheat, "ore": self.ore, "clay": self.clay, "wood": self.wood,
                "sheep": self.sheep, "street": self.streets, "settlement": self.settlements, "city": self.cities,
                "hidden_developments": self.hidden_developments.json(),
                "bank_trade_costs": self.bank_trade_costs}

    def add(self, resource: str, count: int = 1):
        if resource == "sheep":
            self.sheep += count
        if resource == "wood":
            self.wood += count
        if resource == "ore":
            self.ore += count
        if resource == "clay":
            self.clay += count
        if resource == "wheat":
            self.wheat += count
        if resource == "streets":
            self.streets += count
        if resource == "settlements":
            self.settlements += count
        if resource == "cities":
            self.cities += count

    def get(self, resource: str):
        if resource == "sheep":
            return self.sheep
        if resource == "wood":
            return self.wood
        if resource == "ore":
            return self.ore
        if resource == "clay":
            return self.clay
        if resource == "wheat":
            return self.wheat
        if resource == "streets":
            return self.streets
        if resource == "settlements":
            return self.settlements
        if resource == "cities":
            return self.cities

    def make_item_list(self, game_mode: str = "standard"):
        out = []
        for i in range(self.wood):
            out.append("wood")
        for i in range(self.clay):
            out.append("clay")
        for i in range(self.wheat):
            out.append("wheat")
        for i in range(self.sheep):
            out.append("sheep")
        for i in range(self.ore):
            out.append("ore")
        return out

    def draw_random_item(self, game_mode: str = "standard"):
        items = self.make_item_list(game_mode)
        if len(items) == 0:
            return None
        random.shuffle(items)
        draw = items.pop(0)
        self.add(draw, -1)
        return draw

    def size(self, game_mode: str = "standard"):
        items = self.make_item_list(game_mode)
        return len(items)

    def __repr__(self):
        return f"Inventory of {self.owner}: sheep: {self.sheep}, wood: {self.wood}, ore: {self.ore}, clay: {self.clay}, " \
               f"wheat: {self.wheat}, streets: {self.streets}, settlements: {self.settlements}, " \
               f"cities: {self.cities}, hidden_developments: {self.hidden_developments}"
