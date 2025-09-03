import copy

from game import Game
from map import City
from packer import writeGame


class DiceThrow:
    def __init__(self, game: Game, number: int = None):
        # self.pre = copy.deepcopy(game)
        if number is None:
            game.dice.trigger()
            number = game.dice.state
        self.number = number
        triggered_fields = game.map.getNumberCoordinates(number)
        for field in triggered_fields:
            resource = game.map.fields[field].landscape
            corners = game.map.getAdjacentSettlementsForField(field[0], field[1])
            for corner in corners:
                owner = corner.owner
                count = 1
                if type(corner) == City:
                    count = 2
                owner.inventory.add(resource, count)
        writeGame(game)
        # self.post = copy.deepcopy(game)
