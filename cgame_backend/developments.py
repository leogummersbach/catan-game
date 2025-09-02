import random


class DevelopmentCard:
    def __init__(self, kind: str):
        self.kind = kind

    def __repr__(self):
        return self.kind


class Developments:
    def __init__(self, cards: dict):
        pile = []
        for key in cards:
            for i in range(cards[key]):
                pile.append(DevelopmentCard(key))
        random.shuffle(pile)
        self.pile = pile

    def __repr__(self):
        return f"Developments ({self.get_length()}): {self.pile}"

    def json(self):
        cards = []
        for card in self.pile:
            cards.append({"card": str(card)})
        return cards

    def get_length(self):
        return len(self.pile)


class EmptyDevelopments(Developments):
    def __init__(self):
        super().__init__({})


class StandardDevelopments(Developments):
    def __init__(self):
        super().__init__({"knight": 14, "street_build": 2, "plenty_year": 2, "monopoly": 2, "victory": 5})


class DevelopmentsManager:
    def __init__(self, mode: str = "standard"):
        if mode == "standard":
            self.draw_pile = StandardDevelopments()
            self.discard_pile = EmptyDevelopments()

    def __repr__(self):
        return f"Draw pile: {str(self.draw_pile)}\nDiscard pile: {str(self.discard_pile)}"

    def checkDrawPile(self):
        if self.draw_pile.get_length() <= 0:
            to_shuffle = self.discard_pile.pile
            random.shuffle(to_shuffle)
            self.draw_pile.pile = to_shuffle
            self.discard_pile.pile = []

    def drawCard(self):
        drew = self.draw_pile.pile.pop(0)
        self.checkDrawPile()
        return drew

    def discardCard(self, card: DevelopmentCard):
        self.discard_pile.pile.append(card)
