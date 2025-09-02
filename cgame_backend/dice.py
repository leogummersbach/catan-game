import random


class Dice_six:
    def __init__(self):
        self.state = 3

    def trigger(self):
        self.state = random.randint(1, 6)


class Dices:
    def __init__(self, dices=None):
        if dices is None:
            dices = []
        self.state = 0
        self.dices = dices

    def trigger(self):
        sum = 0
        for dice in self.dices:
            dice.trigger()
            sum += dice.state
        self.state = sum
