import { Assets, Graphics, Sprite, Text } from "pixi.js";
import { Cgame } from "./cgame";
import { GetCard, Monopoly, PlayerTradeAnswer, ReturnCard } from './window';
import { inventory } from "./hud";

class CardInventory{
    public wood: number;
    public clay: number;
    public sheep: number;
    public wheat: number;
    public ore: number;
    constructor(inv: CardInventory){
        this.wood = inv.wood;
        this.clay = inv.clay;
        this.sheep = inv.sheep;
        this.wheat = inv.wheat;
        this.ore = inv.ore;
    }
    public length(){
        return this.wood + this.clay + this.sheep + this.wheat + this.ore
    }
    public names(){
        return ["wood", "clay", "sheep", "wheat", "ore"]
    }
    public get(s: string){
        if(s == "wood" || s == "clay" || s == "sheep" || s == "wheat" || s == "ore"){
            return this[s]
        }
        else{
            return 0
        }
    }
}

export class Trade {
    public initiator: string;
    public get: CardInventory;
    public give: CardInventory;
    constructor(trade: Trade){
        this.initiator = trade.initiator;
        this.get = new CardInventory(trade.get);
        this.give = new CardInventory(trade.give);
    }
    public flip(){
        let get = this.get;
        this.get = this.give;
        this.give = get;
    }
}

export class Player {
    public name: string;
    public color: string;
    public score: number;
    public longest_trading_route: number;
    public knights: number;
    public last_dice: number;
    public items: number;
    constructor(name: string, color: string, score: number, longest_trading_route: number, knights: number, last_dice: number, items: number){
        this.name = name;
        this.color = color;
        this.score = score;
        this.longest_trading_route = longest_trading_route;
        this.knights = knights;
        this.last_dice = last_dice;
        this.items = items;
    }
}

export class Meta extends Graphics {
    private status: number;
    private players: Array<Player>;
    public parentObject: Cgame;
    private screenWidth: number;
    private screenHeight: number;
    private scaleer: number;
    private url: string;
    private base_url: string;
    private activePlayer: string;
    private robable: string[];
    public items: string[];
    public returner: string;
    private color: string;
    public window: ReturnCard | PlayerTradeAnswer | GetCard | undefined;
    public active_trade: Trade | null;
    public players_accepted: string[];
    public get_player: string | undefined;
    public get_amount: number;
    public winner: string | undefined;
    constructor(parentObject: Cgame, screenWidth: number, screenHeight: number, scale: number, url: string, base_url: string, items: string[], color: string) {
        super();
        this.parentObject = parentObject;
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        this.scaleer = scale;
        this.status = 0;
        this.players = [];
        this.robable = [];
        this.activePlayer = "";
        this.url = url;
        this.base_url = base_url;
        this.items = items;
        this.returner = "";
        this.color = color;
        this.window = undefined;
        this.active_trade = null;
        this.players_accepted = [];
        this.get_player = undefined;
        this.get_amount = 0;
        this.beginFill(0xFFFFFF);
        this.drawRect(0, 0, this.screenWidth, this.screenHeight);
        this.loadMeta();
        setInterval(() => {
            this.loadMeta()
        }, 100)
    }
    public getStatus(){
        return this.status;
    }
    public getPlayerColor(name: string){
        let found = this.players.find(player => player.name == name) as Player
        return found.color
    }
    public getPlayerName(color: string){
        let found = this.players.find(player => player.color == color) as Player
        return found.name
    }
    public loadMeta(){
        let self = this;
        const xhttp = new XMLHttpRequest();
        xhttp.onload = function() {
            self.status = JSON.parse(this.responseText).state;
            self.players = JSON.parse(this.responseText).players;
            self.activePlayer = JSON.parse(this.responseText).active_player;
            self.players_accepted = JSON.parse(this.responseText).players_accepted;
            self.get_player = JSON.parse(this.responseText).get_player;
            self.get_amount = JSON.parse(this.responseText).get_amount;
            self.winner = JSON.parse(this.responseText).winner;
            let trade = JSON.parse(this.responseText).active_trade;
            if(trade == null){
                self.active_trade = null;
            }
            else{
                self.active_trade = new Trade(JSON.parse(this.responseText).active_trade);
            }
            if(self.status == 6){
                const xhttp3 = new XMLHttpRequest();
                xhttp3.onload = function() {
                    self.returner = self.makeupText(this.responseText);
                    let own = JSON.parse(this.responseText)[self.color]
                    if(own != undefined && self.window == undefined){
                        self.window = new ReturnCard(self.parentObject, 500, 500, self.parentObject.screen.width, self.parentObject.screen.height, 100, self.items, own, self.color, self.url, self.base_url);
                        self.parentObject.setWindow(self.window)
                        self.parentObject.stage.addChild(self.window)
                    }
                    self.drawMeta()
                }
                xhttp3.open("GET", self.url+"card_return", true);
                xhttp3.send()
            }
            self.drawMeta();
            }
        xhttp.open("GET", this.url+"meta", true);
        xhttp.send();
        const xhttp2 = new XMLHttpRequest();
        xhttp2.open("GET", this.url+"robable", true);
        xhttp2.onload = function() {
            self.robable = JSON.parse(this.responseText);
            self.drawMeta();
        }
        xhttp2.send();
        self.drawMeta();
    }
    private clearMeta(){
        this.clear()
        this.beginFill(0xFFFFFF);
        this.drawRect(0, 0, this.screenWidth, this.screenHeight);
        while(this.children[0]) {
            this.removeChild(this.children[0]);
        }
    }
    private drawMeta(){
        this.clearMeta();
        let text = "";
        if(this.status == 1 || this.status == 3){
            text = "Player "+this.activePlayer+", please roll the dice.";
            if(this.window != undefined){
                this.window.destroy()
                this.window = undefined
                this.parentObject.removeWindow()
            }
        }
        else if(this.status == 2){
            text = "Player "+this.activePlayer+", please settle somewhere.";
            if(this.window != undefined){
                this.window.destroy()
                this.window = undefined
                this.parentObject.removeWindow()
            }
        }
        else if(this.status == 4){
            text = "Player "+this.activePlayer+", please make your moves.";
            if(this.active_trade != null){
                if(this.active_trade.initiator == this.color){
                    text = "Please wait while your trade is getting looked at.";
                }
                else{
                    text = "Please answer player "+this.active_trade.initiator+"'s trade."
                    if(this.window == undefined){
                        this.window = new PlayerTradeAnswer(this.parentObject, 500, 500, this.parentObject.screen.width, this.parentObject.screen.height, 100, this.active_trade, this.color, this.url, this.base_url);
                        this.parentObject.setWindow(this.window)
                        this.parentObject.stage.addChild(this.window)
                    }
                }
            }
            else{
                if(this.window != undefined){
                    this.window.destroy()
                    this.window = undefined
                    this.parentObject.removeWindow()
                }
            }
        }
        else if(this.status == 5){
            text = "Player "+this.activePlayer+", please move the robber.";
            if(this.window != undefined){
                this.window.destroy()
                this.window = undefined
                this.parentObject.removeWindow()
            }
        }
        else if(this.status == 6){
            text = "The following players must return some cards: "+this.returner;
        }
        else if(this.status == 7){
            text = "Player "+this.activePlayer+", please rob one of the following players: "+this.robable+".";
            if(this.window != undefined){
                this.window.destroy()
                this.window = undefined
                this.parentObject.removeWindow()
            }
        }
        else if(this.status == 8){
            text = "The following players accepted the deal: "+this.players_accepted+".";
            if(this.window != undefined){
                this.window.destroy()
                this.window = undefined
                this.parentObject.removeWindow()
            }
        }
        else if(this.status == 9){
            if(this.get_amount == 1){
                text = "Player "+this.get_player+", please build "+this.get_amount+" street.";
            }
            else{
                text = "Player "+this.get_player+", please build "+this.get_amount+" streets.";
            }
            if(this.window != undefined){
                this.window.destroy()
                this.window = undefined
                this.parentObject.removeWindow()
            }
        }
        else if(this.status == 10){
            if(this.get_amount == 1){
                text = "Player "+this.get_player+", please choose "+this.get_amount+" item.";
            }
            else{
                text = "Player "+this.get_player+", please choose "+this.get_amount+" items.";
            }
            if(this.get_player == this.color && this.window == undefined){
                this.window = new GetCard(this.parentObject, 500, 500, this.parentObject.screen.width, this.parentObject.screen.height, 100, this.items, this.get_amount, this.color, true, this.url, this.base_url);
                this.parentObject.setWindow(this.window)
                this.parentObject.stage.addChild(this.window)
            }
        }
        else if(this.status == 11){
            text = "Player "+this.get_player+", please choose an item.";
            if(this.get_player == this.color && this.window == undefined){
                this.window = new Monopoly(this.parentObject, 500, 500, this.parentObject.screen.width, this.parentObject.screen.height, 100, this.items, this.color, this.url, this.base_url);
                this.parentObject.setWindow(this.window)
                this.parentObject.stage.addChild(this.window)
            }
        }
        else if(this.status == 12){
            text = "Player "+this.winner+" has won the game!";
        }
        let statustext = new Text(text, {
            fontSize: this.scaleer/5,
            wordWrap: true,
            wordWrapWidth: this.width
        })
        statustext.x = 0;
        statustext.y = 0;
        this.addChild(statustext);
        let statusheight = statustext.height + 30;
        let counter = 0;

        for(let i = 0; i < this.players.length; i++){
            let player = this.players[i]
            let y = statusheight+40*i+counter;
            
            Assets.load(this.base_url + "images/" + "street_"+player.color+".png").then(texture => {
                let playerSign = Sprite.from(texture)
                playerSign.scale.set(this.scaleer/500, this.scaleer/500);
                playerSign.anchor.set(0);
                playerSign.x = 10;
                playerSign.y = y;
                this.addChild(playerSign);
            })
            let score = player.score
            if(player.color == this.color){
                if(this.parentObject.hud != undefined){
                    let myInventory: inventory = this.parentObject.hud.inventories.find(inv => inv.owner == this.color) as inventory
                        if(myInventory){
                            let victory_cards = myInventory.hidden_developments.filter(card => card.card == "victory").length
                            score += victory_cards;
                        }
                }
            }
            let content = "Score: "+score + "\nItems: " + player.items + "\nLongest Road: "+player.longest_trading_route + "\nKnights: "+player.knights;
            if(this.status == 1){
                if(player.last_dice == 0){
                    content = ""
                }
                else{
                    content = "Dice: "+player.last_dice;
                }
            }
            let text = new Text(content, {
                fontSize: this.scaleer/5,
                wordWrap: true,
                wordWrapWidth: this.width
            })
            text.x = 30;
            text.y = y;
            this.addChild(text);
            counter += text.height;
        }
    }

    private makeupText(s: string): string{
        let obj = JSON.parse(s);
        let out = "\n";
        for (let k in obj){
            out += k;
            out += ": ";
            out += obj[k];
            out += "\n"
        }
        return out;
    }
}