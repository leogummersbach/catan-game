import time
from threading import Thread

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from bot import Bot
from costs import ResourceList
from developments import DevelopmentCard
from game import *
from inventory import CardInventory
from map import City, Street, Settlement
from move import DiceThrow
from packer import *
from trade import Trade

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:1234",
    "http://leoseite.de",
    "http://dyndns.leoseite.de",
    "leoseite.de",
    "dyndns.leoseite.de"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_games = []
ended_games = []
"""
g = Game()
print(g.key)
g.makeStandardGame()
p1 = Player("yellow")
p2 = Bot("red", g)
p3 = Bot("green", g)
g.players.append(p1)
g.players.append(p2)
g.players.append(p3)
bots = filter(lambda player: isinstance(player, Bot), g.players)
for bot in bots:
    thread = Thread(target=bot.mainloop)
    thread.start()
g.start()
writeGame(g)
active_games.append(g.key)
"""
writeMeta(active_games, ended_games)

@app.get("/cgameapi")
def get_main():
    return readMeta()


@app.get("/cgameapi/games/{key}/map")
def get_map(key):
    return readGame(key).map.json()


@app.get("/cgameapi/games/{key}/hud")
def get_hud(key):
    players = readGame(key).players
    inventories = []
    for player in players:
        inventories.append(player.inventory.json())
    return {"inventories": inventories}


@app.get("/cgameapi/games/{key}/meta")
def get_meta(key):
    return readGame(key).json()


@app.get("/cgameapi/games/{key}/score/{color}")
def get_score(key, color):
    p = None
    g = readGame(key)
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        return {"error": f"no player with color {color} found"}
    victory_points = g.count_victory_points(p)
    longest_trading_route = g.map.computeLongestTradingRoute(p)
    return {"victory points": victory_points, "longest trading route": longest_trading_route}


@app.put("/cgameapi/games/{key}/move/end/{color}")
def end_turn(key, color):
    g = readGame(key)
    if g.players[g.active_player].color != color:
        raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")
    if g.state == GameState.TRADE_BUILD or g.state == GameState.SETUP_PHASE_PLACE or g.state == GameState.SETUP_PHASE_ROLL:
        if g.active_player + 1 >= len(g.players):
            g.active_player = 0
            if g.state == GameState.SETUP_PHASE_ROLL:
                g.players.sort(key=lambda p: -p.last_dice)
                g.state = GameState.SETUP_PHASE_PLACE
                g.map.safe_original()
                g.map.shadowSettlements()
                writeGame(g)
            elif g.state == GameState.SETUP_PHASE_PLACE:
                g.start_placements -= 1
                g.players.reverse()
                if g.start_placements == 0:
                    g.state = GameState.AWAIT_ROLL
                else:
                    g.map.safe_original()
                    g.map.shadowSettlements()
                writeGame(g)
            elif g.state == GameState.TRADE_BUILD:
                g.state = GameState.AWAIT_ROLL
            writeGame(g)
        else:
            g.active_player += 1
            if g.state == GameState.SETUP_PHASE_PLACE:
                g.map.safe_original()
                g.map.shadowSettlements()
            elif g.state == GameState.TRADE_BUILD:
                g.state = GameState.AWAIT_ROLL
            writeGame(g)
    else:
        raise HTTPException(status_code=403, detail="Game does not await a turn ending")


@app.put("/cgameapi/games/{key}/move/dice_throw/{color}")
def dice_throw(key, color):
    g = readGame(key)
    if not g.state == GameState.AWAIT_ROLL and not g.state == GameState.SETUP_PHASE_ROLL:
        raise HTTPException(status_code=403, detail="Game does not await a dice throw")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=404, detail=f"no player with color {color} found")
    if g.players[g.active_player] != p:
        raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")
    DiceThrow(g)
    p.last_dice = g.dice.state
    if g.state == GameState.SETUP_PHASE_ROLL:
        end_turn(color) #TODO hier fehl das argument key. dieser fehler sollte sehr häufig vorkommen
    else:
        if g.dice.state == 7:
            return_cards = g.compute_returns()
            if len(return_cards) == 0:
                g.state = GameState.MOVE_ROBBER
            else:
                g.state = GameState.RETURN_CARDS
        else:
            g.state = GameState.TRADE_BUILD
    writeGame(g)
    return g.json()["dice"]


@app.put("/cgameapi/games/{key}/move/move_robber/{color}/{x}/{y}")
def move_robber(key, color, x, y):
    g = readGame(key)
    x = int(x)
    y = int(y)
    if not g.state == GameState.MOVE_ROBBER:
        raise HTTPException(status_code=403, detail="Game does not await robber move")
    if not g.players[g.active_player].color == color:
        raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")
    new_field = {}
    for field_key in g.map.field_figures:
        field = g.map.field_figures[field_key]
        if field.type == "robber":
            if field.x == x and field.y == y:
                raise HTTPException(status_code=403, detail="The robber is already there")
        else:
            new_field[field_key] = field
    new_field[(x, y)] = FieldFigure(x, y, "robber")
    g.map.field_figures = new_field
    to_draw = get_robable()
    if len(to_draw) == 0:
        g.state = GameState.TRADE_BUILD
    else:
        g.state = GameState.ROB_PLAYER
    writeGame(g)
    return to_draw


@app.get("/cgameapi/games/{key}/robable")
def get_robable(key):
    g = readGame(key)
    x = None
    y = None
    for field_key in g.map.field_figures:
        field = g.map.field_figures[field_key]
        if field.type == "robber":
            x = field_key[0]
            y = field_key[1]
    if x is None or y is None:
        raise HTTPException(status_code=404, detail="No robber found")
    to_draw = g.map.getAdjacentPlayersForField(x, y)
    return list(filter(lambda color: g.players[g.active_player].color != color, to_draw))


@app.get("/cgameapi/games/{key}/card_return")
def card_return(key):
    g = readGame(key)
    if g.state != GameState.RETURN_CARDS:
        raise HTTPException(status_code=403, detail="Game does not await card return")
    return g.compute_returns()


@app.put("/cgameapi/games/{key}/move/bank_trade/{color}/{give_name}/{get_name}")
def bank_trade(key, color, give_name, get_name):
    g = readGame(key)
    if g.state != GameState.TRADE_BUILD:
        raise HTTPException(status_code=403, detail="Game does not await bank trade")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=403, detail=f"no player with color {color} found")
    if g.players[g.active_player] != p:
        raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")
    costs = Costs()
    costs.addCosts("bank_trade", ResourceList({give_name: p.inventory.bank_trade_costs[give_name]}))
    if not costs.affordable(p.inventory, "bank_trade"):
        raise HTTPException(status_code=403, detail=f"player with color {color} has not enough {give_name}")
    costs.afford(p.inventory, "bank_trade")
    p.inventory.add(get_name)
    writeGame(g)


@app.put("/cgameapi/games/{key}/move/player_trade/{color}/{give_wood}/{give_clay}/{give_sheep}/{give_wheat}/{give_ore}/{get_wood}/{"
         "get_clay}/{get_sheep}/{get_wheat}/{get_ore}")
def player_trade(key, color, give_wood, give_clay, give_sheep, give_wheat, give_ore, get_wood, get_clay, get_sheep,
                 get_wheat, get_ore):
    g = readGame(key)
    give = {"wood": int(give_wood), "clay": int(give_clay), "sheep": int(give_sheep), "wheat": int(give_wheat),
            "ore": int(give_ore)}
    get = {"wood": int(get_wood), "clay": int(get_clay), "sheep": int(get_sheep), "wheat": int(get_wheat),
           "ore": int(get_ore)}
    if g.state != GameState.TRADE_BUILD:
        raise HTTPException(status_code=403, detail="Game does not await player trade")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=403, detail=f"no player with color {color} found")
    if g.players[g.active_player] != p:
        raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")
    if g.active_trade is not None:
        raise HTTPException(status_code=403, detail=f"there is already an active trade, please wait")
    costs = Costs()
    costs.addCosts("give", ResourceList(give))
    if not costs.affordable(p.inventory, "give"):
        raise HTTPException(status_code=403, detail=f"player with color {color} has not enough items")
    give_inventory = CardInventory()
    give_inventory.fromDict(give)
    get_inventory = CardInventory()
    get_inventory.fromDict(get)
    if give_inventory.size() == 0 or get_inventory.size() == 0:
        raise HTTPException(status_code=403, detail=f"items cannot be gifted")
    g.active_trade = Trade(p, get_inventory, give_inventory)
    writeGame(g)


@app.put("/cgameapi/games/{key}/move/reply_to_active_trade/{color}/{reply}")
def reply_to_active_trade(key, color, reply):
    g = readGame(key)
    reply = bool(int(reply))
    if g.state != GameState.TRADE_BUILD:
        raise HTTPException(status_code=403, detail="Game does not await player trade reply")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=403, detail=f"no player with color {color} found")
    if g.players[g.active_player] == p:
        raise HTTPException(status_code=403, detail=f"you cannot reply to your own trade")
    if g.active_trade is None:
        raise HTTPException(status_code=403, detail=f"there is not an active trade")
    if reply:
        costs = Costs()
        costs.addCosts("give", ResourceList(g.active_trade.get.json()))
        if not costs.affordable(p.inventory, "give"):
            raise HTTPException(status_code=403, detail=f"player {color} has not enough items")
    g.active_trade.respond(p, reply)
    g.check_active_trade()
    writeGame(g)


@app.put("/cgameapi/games/{key}/move/fulfill_trade/{color1}/{color2}")
def fulfill_trade(key, color1, color2):
    g = readGame(key)
    if g.state != GameState.ACCEPT_DEAL:
        raise HTTPException(status_code=403, detail="Game does not await trade")
    p1 = None
    for player in g.players:
        if player.color == color1:
            p1 = player
            break
    if p1 is None:
        raise HTTPException(status_code=403, detail=f"no player with color {color1} found")
    p2 = None
    for player in g.players:
        if player.color == color2:
            p2 = player
            break
    if p2 is None:
        raise HTTPException(status_code=403, detail=f"no player with color {color2} found")
    if g.players[g.active_player] != p1:
        raise HTTPException(status_code=403, detail=f"it is not player {color1}'s turn")
    if color2 not in g.trade_accepted:
        raise HTTPException(status_code=403, detail=f"{color2} said no to the trade")
    p1_give = Costs()
    p1_give.addCosts("trade", ResourceList(g.active_trade.give.json()))
    if not p1_give.affordable(p1.inventory, "trade"):
        raise HTTPException(status_code=403, detail=f"{color1} has not enough items")
    p2_give = Costs()
    p2_give.addCosts("trade", ResourceList(g.active_trade.get.json()))
    if not p2_give.affordable(p2.inventory, "trade"):
        raise HTTPException(status_code=403, detail=f"{color2} has not enough items")

    p1_give.afford(p1.inventory, "trade")
    p1_give.give(p2.inventory, "trade")
    p2_give.afford(p2.inventory, "trade")
    p2_give.give(p1.inventory, "trade")
    g.active_trade = None
    g.state = GameState.TRADE_BUILD
    writeGame(g)


@app.put("/cgameapi/games/{key}/move/cancel_trade/{color}/")
def cancel_trade(key, color):
    g = readGame(key)
    if g.state != GameState.ACCEPT_DEAL:
        raise HTTPException(status_code=403, detail="Game does not await trade")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=403, detail=f"no player with color {color} found")
    if g.players[g.active_player] != p:
        raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")
    g.active_trade = None
    g.state = GameState.TRADE_BUILD
    writeGame(g)


@app.put("/cgameapi/games/{key}/move/return_cards/{color}/{wood}/{clay}/{sheep}/{wheat}/{ore}")
def return_cards(key, color, wood, clay, sheep, wheat, ore):
    g = readGame(key)
    wood = int(wood)
    clay = int(clay)
    sheep = int(sheep)
    wheat = int(wheat)
    ore = int(ore)
    if g.state != GameState.RETURN_CARDS:
        raise HTTPException(status_code=403, detail="Game does not await card return")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=403, detail=f"no player with color {color} found")
    return_cards = g.compute_returns()
    if color not in return_cards:
        raise HTTPException(status_code=403, detail=f"Player {color} must not return any cards")
    sum = wood + clay + sheep + wheat + ore
    if return_cards[color] != sum:
        raise HTTPException(status_code=403, detail=f"Wrong number of cards, expected {return_cards[color]}, got {sum}")
    costs = Costs()
    costs.addCosts("return", ResourceList({"wood": wood, "clay": clay, "sheep": sheep, "wheat": wheat, "ore": ore}))
    if not costs.affordable(p.inventory, "return"):
        raise HTTPException(status_code=403,
                            detail=f"player with color {color} cant return these items because not all are owned")
    costs.afford(p.inventory, "return")
    g.alreadyReturned.append(color)
    if len(g.compute_returns()) <= 0:
        g.state = GameState.MOVE_ROBBER
        g.alreadyReturned = []
    writeGame(g)


@app.put("/cgameapi/games/{key}/move/rob_player/{color_robber}/{color_robbed}")
def rob_player(key, color_robber, color_robbed):
    g = readGame(key)
    if not g.state == GameState.ROB_PLAYER:
        raise HTTPException(status_code=403, detail="Game does not await a robbery")
    p_robber = None
    for player in g.players:
        if player.color == color_robber:
            p_robber = player
            break
    if p_robber is None:
        return {"error": f"no player with color {color_robber} found"}
    p_robbed = None
    for player in g.players:
        if player.color == color_robbed:
            p_robbed = player
            break
    if p_robbed is None:
        return {"error": f"no player with color {color_robbed} found"}
    if g.players[g.active_player] != p_robber:
        raise HTTPException(status_code=403, detail=f"it is not player {color_robber}'s turn")
    x = None
    y = None
    for field_key in g.map.field_figures:
        field = g.map.field_figures[field_key]
        if field.type == "robber":
            x = field_key[0]
            y = field_key[1]
    to_draw = g.map.getAdjacentPlayersForField(x, y)
    if color_robbed not in to_draw:
        raise HTTPException(status_code=403, detail=f"you cannot rob player {color_robbed}")
    robbed_item = p_robbed.inventory.draw_random_item(g.game_mode)
    p_robber.inventory.add(robbed_item, 1)
    g.state = GameState.TRADE_BUILD
    writeGame(g)
    return robbed_item


@app.put("/cgameapi/games/{key}/move/street_build/{color}/{x}/{y}/{where}")
def street_build(key, color, x, y, where):
    g = readGame(key)
    if not g.state == GameState.TRADE_BUILD and not g.state == GameState.SETUP_PHASE_PLACE and not g.state == GameState.BUILD_STREET:
        raise HTTPException(status_code=403, detail="Game does not await a street build")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        return {"error": f"no player with color {color} found"}
    if g.state == GameState.BUILD_STREET:
        if g.get_player != p:
            raise HTTPException(status_code=403, detail=f"Game does not await a street build of player {color}")
        if g.get_amount <= 0:
            raise HTTPException(status_code=403,
                                detail="Game does not await a street build because the amount is zero or less")
    else:
        if g.players[g.active_player] != p:
            raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")

    locations = g.map.getPossibleStreetLocations(p)
    if g.state == GameState.TRADE_BUILD:
        if not g.costs.affordable(p.inventory, "street"):
            return {"error": f"player with color {color} has not enough items"}
        for location in locations:
            if location == (int(x), int(y), int(where)):
                # placeable!
                g.map.load_original()
                g.costs.afford(p.inventory, "street")
                g.map.place_street(Street(p, int(x), int(y), int(where)))
                g.compute_longest_road()
                g.check_victory()
                writeGame(g)
                return {"success": f"placed street!"}
        return {"error": f"position not valid!"}

    if g.state == GameState.BUILD_STREET:
        for location in locations:
            if location == (int(x), int(y), int(where)):
                # placeable!
                g.map.load_original()
                g.map.place_street(Street(p, int(x), int(y), int(where)))
                g.get_amount -= 1
                if g.get_amount <= 0:
                    g.state = GameState.TRADE_BUILD
                    g.get_player = None
                else:
                    street_locations(color)
                g.compute_longest_road()
                g.check_victory()
                writeGame(g)
                return {"success": f"placed street!"}
        return {"error": f"position not valid!"}

    if g.state == GameState.SETUP_PHASE_PLACE:
        for location in locations:
            if location == (int(x), int(y), int(where)):
                # placeable!
                g.map.load_original()
                g.map.place_street(Street(p, int(x), int(y), int(where)))
                end_turn(color)
                g.compute_longest_road()
                g.check_victory()
                writeGame(g)
                return {"success": f"placed street!"}
        return {"error": f"position not valid!"}


@app.put("/cgameapi/games/{key}/move/settlement_build/{color}/{x}/{y}/{where}")
def settlement_build(key, color, x, y, where):
    g = readGame(key)
    if not g.state == GameState.TRADE_BUILD and not g.state == GameState.SETUP_PHASE_PLACE:
        raise HTTPException(status_code=403, detail="Game does not await a settlement build")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        return {"error": f"no player with color {color} found"}
    if g.players[g.active_player] != p:
        raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")

    if g.state == GameState.TRADE_BUILD:
        if not g.costs.affordable(p.inventory, "settlement"):
            raise HTTPException(status_code=403, detail=f"player with color {color} has not enough items")
        locations = g.map.getPossibleSettlementLocations(p)
        for location in locations:
            if location == (int(x), int(y), int(where)):
                # placeable!
                g.map.load_original()
                g.costs.afford(p.inventory, "settlement")
                g.map.place_settlement(Settlement(p, int(x), int(y), int(where)))
                g.compute_bank_trade_costs()
                g.check_victory()
                writeGame(g)
                return {"success": f"placed settlement!"}
        raise HTTPException(status_code=403, detail=f"position not valid")
    if g.state == GameState.SETUP_PHASE_PLACE:
        g.map.load_original()
        g.map.place_settlement(Settlement(p, int(x), int(y), int(where)))
        if g.start_placements == 1:
            g.give_start_resources(color, int(x), int(y), int(where))
        street_locations(color, must_connect=(int(x), int(y), int(where)))
        g.compute_bank_trade_costs()
        g.check_victory()
        return {"success": f"placed settlement!"}


@app.put("/cgameapi/games/{key}/move/city_build/{color}/{x}/{y}/{where}")
def city_build(key, color, x, y, where):
    g = readGame(key)
    if not g.state == GameState.TRADE_BUILD and not g.state == GameState.SETUP_PHASE_PLACE:
        raise HTTPException(status_code=403, detail="Game does not await a city build")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        return {"error": f"no player with color {color} found"}
    if g.state == GameState.TRADE_BUILD:
        if g.players[g.active_player] != p:
            raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")
        if not g.costs.affordable(p.inventory, "city"):
            return {"error": f"player with color {color} has not enough items"}
        g.map.load_original()
        locations = g.map.getPossibleCityLocations(p)
        print(locations)
        for location in locations:
            if location == (int(x), int(y), int(where)):
                # placeable!
                g.map.load_original()
                g.costs.afford(p.inventory, "city")
                g.map.place_city(City(p, int(x), int(y), int(where)))
                g.check_victory()
                writeGame(g)
                return {"success": f"placed city!"}
        return {"error": f"position not valid!"}
    if g.state == GameState.SETUP_PHASE_PLACE:
        g.map.load_original()
        g.map.place_city(City(p, int(x), int(y), int(where)))
        g.check_victory()
        writeGame(g)
        return {"success": f"placed city!"}


@app.put("/cgameapi/games/{key}/options/street_locations/{color}")
def street_locations(key, color, must_connect=None):
    g = readGame(key)
    g.map.load_original()
    g.map.safe_original()
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        return {"error": f"no player with color {color} found"}
    else:
        locations = g.map.getPossibleStreetLocations(p, must_connect)
        for location in locations:
            g.map.edges[(location[0], location[1], location[2])] = Street(Player("shadow"), location[0], location[1],
                                                                          location[2])
        writeGame(g)
        return {"success": f"streets are shown for player {color}"}


@app.put("/cgameapi/games/{key}/options/settlement_locations/{color}",
         description="Puts shadow settlements in the map to indicate given players possible settlement locations")
def settlement_locations(key, color):
    g = readGame(key)
    g.map.load_original()
    g.map.safe_original()
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=404, detail=f"no player with color {color} found")
    else:
        locations = g.map.getPossibleSettlementLocations(p)
        for location in locations:
            g.map.corners[(location[0], location[1], location[2])] = Settlement(Player("shadow"), location[0],
                                                                                location[1], location[2])
            writeGame(g)
        return {"success": f"settlements are shown for player {color}"}


@app.put("/cgameapi/games/{key}/options/city_locations/{color}",
         description="Puts shadow cities in the map to indicate given players possible city locations")
def city_locations(key, color):
    g = readGame(key)
    g.map.load_original()
    g.map.safe_original()
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=404, detail=f"no player with color {color} found")
    else:
        locations = g.map.getPossibleCityLocations(p)
        for location in locations:
            g.map.corners[(location[0], location[1], location[2])] = City(Player("shadow"), location[0],
                                                                          location[1], location[2])
            writeGame(g)
        return {"success": f"cities are shown for player {color}"}


@app.put("/cgameapi/games/{key}/options/clear")
def clear_options(key):
    # resets map to original state
    g = readGame(key)
    g.map.load_original()
    writeGame(g)
    return "success"


@app.put("/cgameapi/games/{key}/move/draw_development_card/{color}",
         description="Player with specified color buys a development card.")
def draw_development_card(key, color: str):
    g = readGame(key)
    if not g.state == GameState.TRADE_BUILD:
        raise HTTPException(status_code=403, detail="Game does not await a development card draw")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=404, detail=f"no player with color {color} found")
    if g.players[g.active_player] != p:
        raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")
    else:
        result = g.draw_development_card(p)
        if not result:
            raise HTTPException(status_code=403, detail=f"player {color} has not enough items")
        else:
            g.check_victory()
            writeGame(g)
            return "success"


@app.put("/cgameapi/games/{key}/move/play_development_card/{color}/{card}")
def play_development_card(key, color: str, card: str):
    g = readGame(key)
    if not g.state == GameState.TRADE_BUILD:
        raise HTTPException(status_code=403, detail="Game does not await a development card play")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=404, detail=f"no player with color {color} found")
    if g.players[g.active_player] != p:
        raise HTTPException(status_code=403, detail=f"it is not player {color}'s turn")
    exists = False
    for cards in p.inventory.hidden_developments.pile:
        if cards.kind == card:
            exists = True
    if not exists:
        raise HTTPException(status_code=403, detail=f"player {color} does not have a development card of kind {card}")
    if card == "victory":
        raise HTTPException(status_code=403, detail="A victory card cannot be played")

    g.remove_development_card(p, card)
    if card == "knight":
        g.state = GameState.MOVE_ROBBER
        p.knights += 1
        g.compute_largest_army()
    if card == "plenty_year":
        g.state = GameState.GET_CARDS
        g.get_player = p
        g.get_amount = 2
    if card == "street_build":
        g.state = GameState.BUILD_STREET
        g.get_player = p
        g.get_amount = 2
        street_locations(color)
    if card == "monopoly":
        g.state = GameState.MONOPOLY
        g.get_player = p
        g.get_amount = 1

    writeGame(g)


@app.put("/cgameapi/games/{key}/move/get_cards/{color}/{wood}/{clay}/{sheep}/{wheat}/{ore}")
def get_cards(key, color, wood, clay, sheep, wheat, ore):
    g = readGame(key)
    wood = int(wood)
    clay = int(clay)
    sheep = int(sheep)
    wheat = int(wheat)
    ore = int(ore)
    if not g.state == GameState.GET_CARDS:
        raise HTTPException(status_code=403, detail="Game does not await a card get")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=404, detail=f"no player with color {color} found")
    if g.get_player != p:
        raise HTTPException(status_code=403, detail=f"Game does not await a card get from player {color}")
    sum = wood + clay + sheep + wheat + ore
    if sum != g.get_amount:
        raise HTTPException(status_code=403, detail=f"Game does not await a card get of amount {sum}")
    p.inventory.add("wood", wood)
    p.inventory.add("clay", clay)
    p.inventory.add("sheep", sheep)
    p.inventory.add("wheat", wheat)
    p.inventory.add("ore", ore)
    g.state = GameState.TRADE_BUILD
    g.get_player = None
    writeGame(g)


@app.put("/cgameapi/games/{key}/move/monopoly/{color}/{item}")
def get_cards(key, color, item):
    g = readGame(key)
    if not g.state == GameState.MONOPOLY:
        raise HTTPException(status_code=403, detail="Game does not await a monopoly")
    p = None
    for player in g.players:
        if player.color == color:
            p = player
            break
    if p is None:
        raise HTTPException(status_code=404, detail=f"no player with color {color} found")

    g.monopoly(p, item)
    g.state = GameState.TRADE_BUILD
    writeGame(g)


@app.get("/cgameapi/images/{name}")
async def main(name):
    return FileResponse(f"images/{name}")


# for debugging
def current(key):
    g = readGame(key)
    return g.players[g.active_player].color


def other(key):
    g = readGame(key)
    return g.players[(g.active_player + 1) % 2].color


# DEBUG
"""
dice_throw("yellow")
dice_throw("red")

settlement_build(current(), 0, 0, 0)
street_build(current(), 0, 0, 0)
p2.place_random_settlement(setup=True)



settlement_build(current(), 1, 1, 0)
street_build(current(), 1, 1, 0)
settlement_build(current(), 0, 0, 1)
street_build(current(), 0, 1, 1)
settlement_build(current(), 2, 2, 0)
street_build(current(), 2, 2, 1)

dice_throw(current())

print(g.state)
# play_development_card(current(), "street_build")
print(g.state)

print(move_robber(current(), 0, 0))
print(g.players[g.active_player])
print(p1.inventory.size(), p2.inventory.size())
print(rob_player("yellow", "red"))
print(p1.inventory.size(), p2.inventory.size())
"""
dice_throw(0, "yellow")