import json
import jsonpickle

meta_path = "data/meta.json"

def readMeta():
    try:
        with open(meta_path, "r") as f:
            out = json.load(f)
            f.close()
    except IOError:
        print("No such file")
        out = None
    return out

def writeMeta(active_games, ended_games):
    with open(meta_path, "w") as f:
        d = {"active_games": active_games, "ended_games": ended_games}
        json.dump(d, f)
        f.close()

def readGame(key):
    try:
        with open(f"games/{key}.json", "r") as f:
            game_json = json.load(f)
            f.close()
    except IOError:
        print("No such file")

    game = jsonpickle.decode(game_json)
    game.map.reworkKeys()
    return game

def writeGame(game):
    with open(f"games/{game.key}.json", "w") as f:
        json.dump(jsonpickle.encode(game), f)
        f.close()


"""
class Packer:
    def __init__(self, game: Game):
        self.game = game
        
        players = game.players
        inventories = []
        for player in players:
            inventories.append(player.inventory.json())
        self.map = jsonpickle.encode(game.map)
        self.hud = {"inventories": inventories}
        self.meta = game.json()
        self.key = game.key
        os.makedirs(f"games/{self.key}", exist_ok=True)
        

    def write_file(self):
        with open(f"games/{self.game.key}.json", "w") as f:
            json.dump(jsonpickle.encode(self.game), f)
            f.close()
        
        with open(f"games/{self.key}/map.json", "w") as f:
            json.dump(self.map, f)
            f.close()
        with open(f"games/{self.key}/hud.json", "w") as f:
            json.dump(self.hud, f)
            f.close()
        with open(f"games/{self.key}/meta.json", "w") as f:
            json.dump(self.meta, f)
            f.close()
        

    def read_map(self):
        try:
            with open(f"games/{self.key}/map.json", "r") as f:
                out = jsonpickle.decode(json.load(f))
                f.close()
        except IOError:
            print("No such file")
            out = None
        return out

    def read_hud(self):
        try:
            with open(f"games/{self.key}/hud.json", "r") as f:
                out = jsonpickle.decode(json.load(f))
                f.close()
        except IOError:
            print("No such file")
            out = None
        return out

    def read_meta(self):
        try:
            with open(f"games/{self.key}/meta.json", "r") as f:
                out = jsonpickle.decode(json.load(f))
                f.close()
        except IOError:
            print("No such file")
            out = None
        return out
"""