import random
import os
from enum import Enum

from costs import Costs
from developments import DevelopmentsManager
from dice import Dices, Dice_six
from map import Map, Field, Settlement, City, FieldFigure, Harbor
from placements import *
from player import Player


class GameState(Enum):
    SETUP_PHASE_ROLL = 1
    SETUP_PHASE_PLACE = 2
    AWAIT_ROLL = 3
    TRADE_BUILD = 4
    MOVE_ROBBER = 5
    RETURN_CARDS = 6
    ROB_PLAYER = 7
    ACCEPT_DEAL = 8
    BUILD_STREET = 9
    GET_CARDS = 10
    MONOPOLY = 11
    END = 12


class Game:
    def __init__(self):
        self.key = self.getNewKey()
        self.map = Map()
        self.players = []
        self.active_player = 0
        self.dice = Dices()
        self.developments = DevelopmentsManager()
        self.costs = Costs()
        self.state = GameState.SETUP_PHASE_ROLL
        self.start_placements = 2
        self.game_mode = "standard"
        self.alreadyReturned = []
        self.active_trade = None
        self.trade_accepted = []
        self.get_player = None  # player of things to get, such as cards, street etc., depending on the game state
        self.get_amount = None  # amount of things to get, such as cards, street etc., depending on the game state
        self.longest_road = None
        self.largest_army = None
        self.winning_points = 10
        self.winner = None

    def __repr__(self):
        out = str(self.map)
        out += "\n"
        for player in self.players:
            out += str(player)
            out += "\n"
        return out

    def getNewKey(self):
        used_keys = [int(k) for k in os.listdir("games") if not os.path.isfile(os.path.join("games", k))]
        if len(used_keys) == 0:
            return 0
        used_keys.sort()
        candidate = used_keys[-1] + 1
        while candidate in used_keys:
            candidate += 1
        return candidate


    def json(self):
        l = []
        for d in self.dice.dices:
            l.append({"state": d.state})
        dice = {"dices": l, "sum": self.dice.state}
        players = []
        for player in self.players:
            players.append({"color": player.color,
                            "score": self.count_victory_points(player),
                            "longest_trading_route": self.map.computeLongestTradingRoute(player),
                            "knights": player.knights,
                            "last_dice": player.last_dice,
                            "items": player.inventory.size()})
        active_trade = None
        if self.active_trade is not None:
            active_trade = self.active_trade.json()
        get_player = None
        if self.get_player is not None:
            get_player = self.get_player.color
        winner = None
        if self.winner is not None:
            winner = self.winner.color
        return {"key": self.key, "players": players, "active_player": self.players[self.active_player].color, "dice": dice,
                "state": self.state.value, "active_trade": active_trade, "players_accepted": self.trade_accepted,
                "get_player": get_player, "get_amount": self.get_amount, "winning_points": self.winning_points,
                "winner": winner}

    def makeStandardGame(self):
        self.dice = Dices([Dice_six(), Dice_six()])
        self.costs.addStandardCosts()
        fields = []
        fields.extend(1 * ["desert"])
        fields.extend(3 * ["ore"])
        fields.extend(3 * ["clay"])
        fields.extend(4 * ["sheep"])
        fields.extend(4 * ["wheat"])
        fields.extend(4 * ["wood"])
        numbers = []
        numbers.extend(1 * [2])
        numbers.extend(2 * [3])
        numbers.extend(2 * [4])
        numbers.extend(2 * [5])
        numbers.extend(2 * [6])
        numbers.extend(2 * [8])
        numbers.extend(2 * [9])
        numbers.extend(2 * [10])
        numbers.extend(2 * [11])
        numbers.extend(1 * [12])
        placements = standard_placements()
        for placement in placements:
            if len(fields) == 0:
                raise Exception("placing landscapes: not enough landscapes given")
            x = placement[0]
            y = placement[1]
            field_choice = random.choice(fields)
            if len(numbers) == 0 and field_choice != "desert":
                raise Exception("placing landscapes: not enough numbers given")
            if field_choice == "desert":
                number_choice = None
                self.map.placeFieldFigure(FieldFigure(x, y, "robber"))
            else:
                number_choice = random.choice(numbers)
            self.map.placeLandscape(Field(field_choice, x, y, number_choice))
            fields.remove(field_choice)
            if number_choice is not None:
                numbers.remove(number_choice)

        harbors = []
        harbors.extend(4 * ["all"])
        harbors.extend(1 * ["wood"])
        harbors.extend(1 * ["clay"])
        harbors.extend(1 * ["sheep"])
        harbors.extend(1 * ["wheat"])
        harbors.extend(1 * ["ore"])
        placements = standard_harbor_placements()
        for placement in placements:
            if len(harbors) == 0:
                raise Exception("placing harbors: not enough harbors given")
            x = placement[0]
            y = placement[1]
            where = placement[2]
            harbor_choice = random.choice(harbors)
            self.map.placeHarbor(Harbor(x, y, where, harbor_choice))
            harbors.remove(harbor_choice)

    def start(self):
        if len(self.players) == 0:
            return
        self.state = GameState.SETUP_PHASE_ROLL

    def count_victory_points(self, player: Player):
        points = 0
        color = player.color
        for corner in self.map.corners:
            if self.map.corners[corner].owner.color == color:
                if isinstance(self.map.corners[corner], Settlement):
                    points += 1
                if isinstance(self.map.corners[corner], City):
                    points += 2
        if self.longest_road == player:
            points += 2
        if self.largest_army == player:
            points += 2
        return points

    def draw_development_card(self, player: Player):
        if self.costs.affordable(player.inventory, "development"):
            self.costs.afford(player.inventory, "development")
            card = self.developments.drawCard()
            player.inventory.hidden_developments.pile.append(card)
            return True
        return False

    def remove_development_card(self, player: Player, card: str):
        keep = []
        found = False
        for cards in player.inventory.hidden_developments.pile:
            if found or cards.kind != card:
                keep.append(cards)
            else:
                found = True
        player.inventory.hidden_developments.pile = keep

    def compute_returns(self):
        out = {}
        for player in self.players:
            if player.inventory.size() > player.inventory_threshold and player.color not in self.alreadyReturned:
                out[player.color] = int(player.inventory.size() / 2)
        return out

    def check_active_trade(self):
        if self.active_trade is None:
            return
        accepted = []
        for player in self.players:
            if player.color == self.active_trade.initiator.color:
                continue
            if player.color not in self.active_trade.responses.keys():
                return  # not completely responded
            if self.active_trade.responses[player.color]:
                accepted.append(player.color)
        if len(accepted) != 0:
            self.state = GameState.ACCEPT_DEAL
        else:
            self.state = GameState.TRADE_BUILD
            self.active_trade = None
        self.trade_accepted = accepted

    def monopoly(self, player: Player, item: str):
        sum = 0
        for p in self.players:
            amount = p.inventory.get(item)
            p.inventory.add(item, -amount)
            sum += amount
        player.inventory.add(item, sum)

    def compute_bank_trade_costs(self):
        for player in self.players:
            for item in player.inventory.cardNames():
                best = 4
                for key in self.map.corners:
                    corner = self.map.corners[key]
                    if corner.owner == player:
                        harbor_locations = self.map.getAdjacentHarborsForCorner(key[0], key[1], key[2])
                        for harbor_location in harbor_locations:
                            if harbor_location in self.map.harbors:
                                if self.map.harbors[harbor_location].trading == "all":
                                    if 3 < best:
                                        best = 3
                                if self.map.harbors[harbor_location].trading == item:
                                    best = 2
                player.inventory.bank_trade_costs[item] = best

    def compute_largest_army(self):
        for player in self.players:
            if self.largest_army != player:
                if self.largest_army is None and player.knights >= 3:
                    self.largest_army = player
                elif self.largest_army is not None and self.largest_army.knights < player.knights:
                    self.largest_army = player

    def compute_longest_road(self):
        for player in self.players:
            if self.longest_road != player:
                player_road = self.map.computeLongestTradingRoute(player)
                if self.longest_road is None and player_road >= 5:
                    self.longest_road = player
                elif self.longest_road is not None and self.map.computeLongestTradingRoute(
                        self.longest_road) < player_road:
                    self.longest_road = player

    def check_victory(self):
        for player in self.players:
            points = self.count_victory_points(player)
            for card in player.inventory.hidden_developments.pile:
                if card.kind == "victory":
                    points += 1
            if points >= self.winning_points:
                self.winner = player
                self.state = GameState.END
                break

    def give_start_resources(self, color, x, y, where):
        p: Player = None
        for player in self.players:
            if player.color == color:
                p = player
                break
        if p is None:
            raise Exception(f"Player with color {color} does not exist")
        fields = self.map.getAdjacentFieldsForCorner(x, y, where)
        for field in fields:
            if field in self.map.fields:
                resource = self.map.fields[field].landscape
                p.inventory.add(resource)
