import copy

from player import Player

class Field:
    def __init__(self, landscape, x, y, number):
        self.landscape: str = landscape
        self.x: int = x
        self.y: int = y
        self.number: int = number

    def __repr__(self):
        return f"Field on position {self.x, self.y} with landscape {self.landscape} and number {self.number}."

    def json(self):
        return {"x": self.x, "y": self.y, "type": self.landscape, "number": self.number}


class Street:
    def __init__(self, owner: Player, x: int, y: int, where: int):
        if 0 <= where <= 2:
            self.owner = owner
            self.where = where
            self.x = x
            self.y = y
        else:
            raise Exception("street's where must be 0, 1 or 2")

    def __repr__(self):
        return f"Street on position {self.x, self.y, self.where} with owner {self.owner}."

    def json(self):
        return {"x": self.x, "y": self.y, "type": "street", "where": self.where, "owner": self.owner.color}


class Settlement:
    def __init__(self, owner: Player, x: int, y: int, where: int):
        if 0 <= where <= 1:
            self.owner = owner
            self.where = where
            self.x = x
            self.y = y
        else:
            raise Exception("settlement's where must be 0 or 1")

    def __repr__(self):
        return f"Settlement on position {self.x, self.y, self.where} with owner {self.owner}."

    def json(self):
        return {"x": self.x, "y": self.y, "type": "settlement", "where": self.where, "owner": self.owner.color}


class City:
    def __init__(self, owner: Player, x: int, y: int, where: int):
        if 0 <= where <= 1:
            self.owner = owner
            self.where = where
            self.x = x
            self.y = y
        else:
            raise Exception("city's where must be 0 or 1")

    def __repr__(self):
        return f"City on position {self.x, self.y, self.where} with owner {self.owner}."

    def json(self):
        return {"x": self.x, "y": self.y, "type": "city", "where": self.where, "owner": self.owner.color}


class FieldFigure:
    def __init__(self, x: int, y: int, type: str):
        self.x = x
        self.y = y
        self.type = type

    def __repr__(self):
        return f"{self.type} on position {self.x, self.y}."

    def json(self):
        return {"x": self.x, "y": self.y, "type": self.type}


class Harbor:
    def __init__(self, x: int, y: int, where: int, trading: str):
        self.x = x
        self.y = y
        self.where = where
        self.trading = trading

    def __repr__(self):
        return f"Harbor on position {self.x, self.y, self.where}, trading {self.trading}."

    def json(self):
        return {"x": self.x, "y": self.y, "where": self.where, "type": "harbor", "trading": self.trading}

def stringToTuple(s):
    return tuple(map(lambda x: int(x), s[1:][:-1].split(",")))

class Map:
    def __init__(self):
        self.fields = {}
        self.field_figures = {}
        self.edges = {}
        self.corners = {}
        self.harbors = {}
        self.original = (self.fields, self.edges, self.corners)

    def reworkKeys(self):
        dicts = [self.fields, self.field_figures, self.edges, self.corners, self.harbors, self.original[0], self.original[1], self.original[2]]
        original = [self.original[0], self.original[1], self.original[2]]
        new_dicts = []
        for d in dicts:
            new_d = {}
            for key in d:
                if type(key) is str:
                    new_d[stringToTuple(key)] = d[key]
            new_dicts.append(new_d)
        self.fields, self.field_figures, self.edges, self.corners, self.harbors, original[0], original[1], original[2] = new_dicts
        self.original = (original[0], original[1], original[2])
    def json(self):
        fields = []
        for field in self.fields.values():
            fields.append(field.json())
        edges = []
        for edge in self.edges.values():
            edges.append(edge.json())
        corners = []
        for corner in self.corners.values():
            corners.append(corner.json())
        field_figures = []
        for field_figure in self.field_figures.values():
            field_figures.append(field_figure.json())
        harbors = []
        for harbor in self.harbors.values():
            harbors.append(harbor.json())
        return {"map": fields + harbors + edges + corners + field_figures}

    def __repr__(self):
        out = ""
        for key in self.fields.keys():
            out += str(self.fields[key])
            out += "\n"
        for key in self.edges.keys():
            out += str(self.edges[key])
            out += "\n"
        for key in self.corners.keys():
            out += str(self.corners[key])
            out += "\n"
        return out

    def placeLandscape(self, landscape: Field):
        x = landscape.x
        y = landscape.y
        if (x, y) in self.fields:
            raise Exception("there is already a field on that position")
        self.fields[(x, y)] = landscape

    def placeFieldFigure(self, field_figure: FieldFigure):
        x = field_figure.x
        y = field_figure.y
        if (x, y) in self.field_figures:
            raise Exception("there is already a field figure on that position")
        self.field_figures[(x, y)] = field_figure

    def placeHarbor(self, harbor: Harbor):
        x = harbor.x
        y = harbor.y
        where = harbor.where
        if (x, y, where) in self.harbors:
            raise Exception("there is already a harbor on that position")
        self.harbors[(x, y, where)] = harbor

    def place_street(self, street: Street):
        x = street.x
        y = street.y
        where = street.where
        if (x, y, where) in self.edges:
            raise Exception("there is already a street on that position")
        self.edges[(x, y, where)] = street

    def place_settlement(self, settlement: Settlement):
        x = settlement.x
        y = settlement.y
        where = settlement.where
        if (x, y, where) in self.corners:
            raise Exception("there is already a settlement on that position")
        self.corners[(x, y, where)] = settlement

    def place_city(self, city: City):
        x = city.x
        y = city.y
        where = city.where
        if (x, y, where) in self.corners:
            if isinstance(self.corners[(x, y, where)], City):
                raise Exception("there is already a city on that position")
            if not isinstance(self.corners[(x, y, where)], Settlement):
                raise Exception("there must be a settlement to place a city")
            self.corners[(x, y, where)] = city
            return
        raise Exception("there must be a settlement to place a city")

    def getNumberCoordinates(self, number: int):
        out = []
        for key in self.fields:
            if self.fields[key].number == number:
                out.append((self.fields[key].x, self.fields[key].y))
        return out

    def getAdjacentSettlementsForField(self, x: int, y: int, get_all=False):
        # returns adjacent settlements and cities for a specified tile
        coordinates = [(x, y + 1, 0), (x, y - 1, 1)]
        coordinates.extend([(x, y, 0), (x, y, 1)])
        if y % 2 == 0:
            coordinates.extend([(x - 1, y + 1, 0), (x - 1, y - 1, 1)])
        else:
            coordinates.extend([(x + 1, y + 1, 0), (x + 1, y - 1, 1)])
        if get_all:
            return coordinates
        out = []
        for c in coordinates:
            if c in self.corners:
                out.append(self.corners[c])
        return out

    def getAdjacentHarborsForCorner(self, x: int, y: int, where: int):
        # returns adjacent harbors for a specified corner
        if where == 0:
            coordinates = [(x, y, 0), (x, y, 1)]
            if y % 2 == 0:
                coordinates.extend([(x - 1, y - 1, 4), (x - 1, y - 1, 5), (x, y - 1, 2), (x, y - 1, 3)])
            else:
                coordinates.extend([(x, y - 1, 4), (x, y - 1, 5), (x + 1, y - 1, 2), (x + 1, y - 1, 3)])
        else:
            coordinates = [(x, y, 3), (x, y, 4)]
            if y % 2 == 0:
                coordinates.extend([(x - 1, y + 1, 0), (x - 1, y + 1, 5), (x, y + 1, 1), (x, y + 1, 2)])
            else:
                coordinates.extend([(x, y + 1, 0), (x, y + 1, 5), (x + 1, y + 1, 1), (x + 1, y + 1, 2)])
        return coordinates

    def getAdjacentFieldsForCorner(self, x: int, y: int, where: int):
        # returns adjacent harbors for a specified corner
        if where == 0:
            coordinates = [(x, y)]
            if y % 2 == 0:
                coordinates.extend([(x-1, y-1), (x, y-1)])
            else:
                coordinates.extend([(x, y - 1), (x + 1, y - 1)])
        else:
            coordinates = [(x, y)]
            if y % 2 == 0:
                coordinates.extend([(x - 1, y + 1), (x, y + 1)])
            else:
                coordinates.extend([(x, y + 1), (x + 1, y + 1)])
        return coordinates

    def getAdjacentPlayersForField(self, x: int, y: int):
        # returns adjacent settlements and cities for a specified tile
        settlements = self.getAdjacentSettlementsForField(x, y)
        players = []
        for settlement in settlements:
            players.append(self.corners[(settlement.x, settlement.y, settlement.where)].owner.color)
        return list(dict.fromkeys(players))

    def getAdjacentStreetsForStreet(self, street: Street):
        # returns adjacent street locations for a street
        x = street.x
        y = street.y
        where = street.where
        if y % 2 == 0:
            if where == 0:
                return [(x, y, 1), (x, y - 1, 2), (x + 1, y, 1), (x + 1, y, 2)]
            if where == 1:
                return [(x, y, 2), (x, y, 0), (x, y - 1, 2), (x - 1, y, 0)]
            if where == 2:
                return [(x, y, 1), (x - 1, y, 0), (x - 1, y + 1, 0), (x - 1, y + 1, 1)]
        else:
            if where == 0:
                return [(x, y, 1), (x + 1, y - 1, 2), (x + 1, y, 1), (x + 1, y, 2)]
            if where == 1:
                return [(x, y, 2), (x, y, 0), (x + 1, y - 1, 2), (x - 1, y, 0)]
            if where == 2:
                return [(x, y, 1), (x - 1, y, 0), (x, y + 1, 0), (x, y + 1, 1)]

    def getAdjacentStreetsForCorner(self, corner):
        # returns adjacent street locations for a street
        x = corner.x
        y = corner.y
        where = corner.where
        if y % 2 == 0:
            if where == 0:
                return [(x, y, 0), (x, y, 1), (x, y - 1, 2)]
            if where == 1:
                return [(x - 1, y + 1, 0), (x, y + 1, 1), (x, y + 1, 2)]
        else:
            if where == 0:
                return [(x, y, 0), (x, y, 1), (x + 1, y - 1, 2)]
            if where == 1:
                return [(x, y + 1, 0), (x + 1, y + 1, 1), (x + 1, y + 1, 2)]

    def getAdjacentCornerForStret(self, street):
        # returns adjacent corner for a street
        x = street.x
        y = street.y
        where = street.where
        if y % 2 == 0:
            if where == 0:
                return [(x, y, 0), (x, y - 1, 1)]
            if where == 1:
                return [(x, y, 0), (x - 1, y - 1, 1)]
            if where == 2:
                return [(x - 1, y - 1, 1), (x - 1, y + 1, 0)]
        else:
            if where == 0:
                return [(x, y, 0), (x + 1, y - 1, 1)]
            if where == 1:
                return [(x, y, 0), (x, y - 1, 1)]
            if where == 2:
                return [(x, y - 1, 1), (x, y + 1, 0)]

    def getAdjacentCornerForCorner(self, corner):
        # returns adjacent corner for a corner
        x = corner.x
        y = corner.y
        where = corner.where
        if y % 2 == 0:
            if where == 0:
                return [(x, y - 2, 1), (x - 1, y - 1, 1), (x, y - 1, 1)]
            if where == 1:
                return [(x, y + 2, 0), (x - 1, y + 1, 0), (x, y + 1, 0)]
        else:
            if where == 0:
                return [(x, y - 2, 1), (x, y - 1, 1), (x + 1, y - 1, 1)]
            if where == 1:
                return [(x, y + 2, 0), (x, y + 1, 0), (x + 1, y + 1, 0)]

    def getAdjacentFieldsForStreet(self, street):
        # returns adjacent fields for a street
        x = street.x
        y = street.y
        where = street.where
        if y % 2 == 0:
            if where == 0:
                return [(x, y), (x, y-1)]
            if where == 1:
                return [(x, y), (x-1, y-1)]
            if where == 2:
                return [(x, y), (x-1, y)]
        else:
            if where == 0:
                return [(x, y), (x+1, y-1)]
            if where == 1:
                return [(x, y), (x, y-1)]
            if where == 2:
                return [(x, y), (x-1, y)]

    def getPossibleStreetLocations(self, player: Player, must_connect=None):
        # returns possible locations for new streets for a specified player
        # first check players streets
        streets = []
        for street in self.edges.values():
            if street.owner == player:
                if must_connect is not None:
                    adjacent_corners = self.getAdjacentCornerForStret(street)
                    if must_connect not in adjacent_corners:
                        continue
                streets.append(street)
        out = []
        for street in streets:
            out.extend(self.getAdjacentStreetsForStreet(street))
        # check player settlements and cities
        corners = []
        for corner in self.corners.values():
            if corner.owner == player:
                if must_connect is not None:
                    if must_connect[0] != corner.x or must_connect[1] != corner.y or must_connect[2] != corner.where:
                        continue
                corners.append(corner)
        for corner in corners:
            out.extend(self.getAdjacentStreetsForCorner(corner))

        # remove occupied
        keep = []
        for possible in out:
            if not (possible[0], possible[1], possible[2]) in self.edges or \
                    self.edges[possible].owner.color == "shadow":
                keep.append(possible)

        # remove streets next to no fields
        out = []
        for possible in keep:
            fields = self.getAdjacentFieldsForStreet(Street(Player("no-one"), possible[0], possible[1], possible[2]))
            for field in fields:
                if field in self.fields.keys():
                    out.append(possible)
                    break
        out = list(dict.fromkeys(out))
        return out

    def getPossibleSettlementLocations(self, player: Player):
        # returns possible locations for new settlements for a specified player
        # check players streets
        streets = []
        for street in self.edges.values():
            if street.owner == player:
                streets.append(street)
        out = []
        for street in streets:
            out.extend(self.getAdjacentCornerForStret(street))

        # remove occupied
        keep = []
        for possible in out:
            if not (possible[0], possible[1], possible[2]) in self.corners or \
                    self.corners[possible].owner.color == "shadow":
                keep.append(possible)

        # remove settlements directly next to another settlement
        out = []
        for possible in keep:
            nexts = self.getAdjacentCornerForCorner(Settlement(Player("no-one"), possible[0], possible[1], possible[2]))
            assumption = True
            for next in nexts:
                if (next[0], next[1], next[2]) in self.corners:
                    if self.corners[next].owner.color != "shadow":
                        assumption = False
                        break
            if assumption:
                out.append(possible)
        out = list(dict.fromkeys(out))
        return out

    def getPossibleCityLocations(self, player: Player):
        # returns possible locations for new cites for a specified player
        # check players settlements
        settlements = []
        for settlement in self.corners.values():
            if isinstance(settlement, Settlement):
                if settlement.owner == player:
                    settlements.append((settlement.x, settlement.y, settlement.where))
        return settlements

    def safe_original(self):
        self.original = (copy.copy(self.fields), copy.copy(self.edges), copy.copy(self.corners))

    def load_original(self):
        self.fields = self.original[0]
        self.edges = self.original[1]
        self.corners = self.original[2]

    def computeLongestTradingRouteRecursive(self, player: Player, start: Street, already_observed: list[Street],
                                            onway: bool = True):
        # get all neighbors
        neighbors = self.getAdjacentStreetsForStreet(start)
        neighbors = list(filter(lambda s: s in self.edges, neighbors))
        neighbors = list(filter(lambda s: self.edges[s].owner == player, neighbors))

        def filter_directions(street: Street, already_observed_in: list[Street]):
            neighbor_corners = self.getAdjacentCornerForStret(street)
            for neighbor_corner in neighbor_corners:
                neighbor_streets = self.getAdjacentStreetsForCorner(
                    Settlement(Player("no-one"), neighbor_corner[0], neighbor_corner[1], neighbor_corner[2]))
                count = 0
                for neighbor_street_in in neighbor_streets:
                    for already_observed_street in already_observed_in:
                        if neighbor_street_in[0] == already_observed_street.x and neighbor_street_in[
                            1] == already_observed_street.y and neighbor_street_in[2] == already_observed_street.where:
                            count += 1
                if count <= 1:
                    # correct corner
                    return self.getAdjacentStreetsForCorner(
                        Settlement(Player("no-one"), neighbor_corner[0], neighbor_corner[1], neighbor_corner[2]))

        if onway:
            neighbors = list(filter(lambda s: s in filter_directions(start, already_observed), neighbors))
        neighbors = list(filter(lambda s: self.edges[s] not in already_observed, neighbors))
        if len(neighbors) == 0:
            return 1
        else:
            children_score = []
            for neighbor in neighbors:
                neighbor_street = self.edges[neighbor]
                already_observed_extra = already_observed + [neighbor_street]
                children_score.append(
                    self.computeLongestTradingRouteRecursive(player, neighbor_street, already_observed_extra))
            return 1 + max(children_score)

    def computeLongestTradingRoute(self, player: Player):
        # get all streets
        streets = []
        for street in self.edges.values():
            if street.owner == player:
                streets.append(street)

        # remove streets in the middle
        side_streets = []
        for street in streets:
            adjacent = self.getAdjacentCornerForStret(street)
            count = 0
            for adjacent_corner in adjacent:
                adjacent_streets = self.getAdjacentStreetsForCorner(
                    Settlement(Player("no-one"), adjacent_corner[0], adjacent_corner[1], adjacent_corner[2]))
                for adjacent_street in adjacent_streets:
                    if adjacent_street in self.edges:
                        if self.edges[adjacent_street].owner == player:
                            if self.edges[adjacent_street] != street:
                                count += 1
                                break
            if count <= 1:
                side_streets.append(street)

        # compute route
        max_score = 0
        for street in side_streets:
            score = self.computeLongestTradingRouteRecursive(player, street, [street], onway=False)
            if score > max_score:
                max_score = score
        return max_score

    def shadowSettlements(self):
        for key in self.fields:
            corners = self.getAdjacentSettlementsForField(key[0], key[1], get_all=True)
            # remove occupied
            keep = []
            for possible in corners:
                if not (possible[0], possible[1], possible[2]) in self.corners:
                    keep.append(possible)

            # remove settlements directly next to another settlement
            out = []
            for possible in keep:
                nexts = self.getAdjacentCornerForCorner(
                    Settlement(Player("no-one"), possible[0], possible[1], possible[2]))
                assumption = True
                for next in nexts:
                    if (next[0], next[1], next[2]) in self.corners:
                        if self.corners[next].owner.color != "shadow":
                            assumption = False
                            break
                if assumption:
                    out.append(possible)
            for to_place in out:
                self.place_settlement(Settlement(Player("shadow"), to_place[0], to_place[1], to_place[2]))
