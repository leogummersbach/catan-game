import { Assets, Graphics, Sprite, Text } from "pixi.js";
import { Cgame } from "./cgame";
import { BankTrade, PlayerTrade } from "./window";

class bank_trade_costs{
    public wheat: number;
    public wood: number;
    public sheep: number;
    public ore: number;
    public clay: number;
    constructor(){
        this.wheat = 4;
        this.wood = 4;
        this.sheep = 4;
        this.ore = 4;
        this.clay = 4;
    }
}


export class inventory{
    public owner: string;
    public wheat: number;
    public wood: number;
    public sheep: number;
    public ore: number;
    public clay: number;
    public street: number;
    public settlement: number;
    public city: number;
    public hidden_developments: card[];
    public bank_trade_costs: bank_trade_costs;
    constructor(owner: string, wheat: number, wood: number, sheep: number, ore: number, clay: number, street: number, settlement: number, city: number){
        this.owner = owner;
        this.wheat = wheat;
        this.wood = wood;
        this.sheep = sheep;
        this.ore = ore;
        this.clay = clay;
        this.street = street;
        this.settlement = settlement;
        this.city = city;
        this.hidden_developments = [];
        this.bank_trade_costs = new bank_trade_costs();
    }

}

export class dice{
    public status: number;
    constructor(status: number){
        this.status = status;
    }
}

export class card{
    public card: string;
    constructor(card: string){
        this.card = card;
    }
}


export class Hud extends Graphics  {
    public parentObject: Cgame;
    private screenHeight: number;
    private screenWidth: number;
    private color: string;
    private scaleer: number;
    private mapHeight: number;
    public inventories: inventory[];
    private dices: dice[];
    private url: string;
    private base_url: string;
    private streetclicked: boolean;
    private clickedcolorcode: number;
    private unavailablecolorcode: number;
    private defaultcolorcode: number;
    private settlementclicked: boolean;
    private cityclicked: boolean;
    constructor(parentObject: Cgame, screenWidth: number, screenHeight: number, mapHeight: number, color: string, scaleer: number, url: string, base_url: string) {
        super();
        this.parentObject = parentObject;
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        this.color = color;
        this.scaleer = scaleer;
        this.mapHeight = mapHeight;
        this.inventories = []
        this.dices = [];
        this.url = url;
        this.base_url = base_url;
        this.streetclicked = false;
        this.clickedcolorcode = 0xD0D0D0;
        this.unavailablecolorcode = 0x8F8F8F;
        this.defaultcolorcode = 0xFFFFFF;
        this.settlementclicked = false;
        this.cityclicked = false
        this.drawHud();
        this.beginFill(0x8b1818)
        this.drawRect(0, this.mapHeight, this.screenWidth, this.screenHeight)
        
    
        let self = this;
        self.loadHud();
        
        setInterval(function() {
            self.loadHud();
        }, 100);
        
    }
    private drawHud(): void{
        this.clear_hud()
        
        this.drawInventory()
    }

    private drawInventory(): void{
        let myInventory: inventory = this.inventories.find(inv => inv.owner == this.color) as inventory
        if(!myInventory){
            let error = new Text("No inventory found for '"+this.color+"'")
            error.x = this.screenWidth / 2
            error.y = this.screenHeight / 2 + this.mapHeight;
            this.addChild(error)
            return
        }
        let items = ["wood", "clay", "sheep", "wheat", "ore"] as const;
        for(let i = 0; i< items.length; i++){
            Assets.load(this.base_url + "images/" + items[i]+"_item.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.screenWidth / 2 + i*100;
                item.y = this.screenHeight / 2 + this.mapHeight;

                let number = new Text(myInventory[items[i]]);
                number.y = item.y + this.scaleer/2;
                number.x = item.x;
                number.anchor.set(0.5);

                
                let bankTrade = new Text(myInventory.bank_trade_costs[items[i]]+":1")
                bankTrade.y = item.y - this.scaleer/2;
                bankTrade.x = item.x;
                bankTrade.style.fill = "white"
                bankTrade.anchor.set(0.5);
                bankTrade.alpha = 0.2;
                if(myInventory[items[i]] >= myInventory.bank_trade_costs[items[i]]){
                    bankTrade.alpha = 1;
                    bankTrade.interactive = true;
                    bankTrade.on("pointerdown", () => {this.bankTrade(items[i], myInventory.bank_trade_costs[items[i]])}, this)
                }
                
                this.addChild(item)
                this.addChild(number)
                this.addChild(bankTrade)
            })
        }
        let buildables = ["street", "settlement", "city"] as const;
        for(let i = 0; i< buildables.length; i++){
            Assets.load(this.base_url + "images/" + buildables[i]+"_"+this.color+".png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/200, this.scaleer/200)
                item.anchor.set(0.5);
                item.x = this.screenWidth / 2 - buildables.length*100 + (i)*100;
                item.y = this.screenHeight / 2 + this.mapHeight;
                if(buildables[i] == "street"){
                    item.on("pointerdown", this.buildStreetStep1, this)
                    if(myInventory["wood"] < 1 || myInventory["clay"] < 1){
                        item.tint = this.unavailablecolorcode;
                        item.interactive = false;
                    }
                    else if(this.streetclicked){
                        item.tint = this.clickedcolorcode;
                        item.interactive = true;
                    }
                    else{
                        item.tint = this.defaultcolorcode;
                        item.interactive = true;
                    }
                }
                if(buildables[i] == "settlement"){
                    item.on("pointerdown", this.buildSettlementStep1, this)
                    if(myInventory["wood"] < 1 || myInventory["clay"] < 1 || myInventory["wheat"] < 1 || myInventory["sheep"] < 1){
                        item.tint = this.unavailablecolorcode;
                        item.interactive = false;
                    }
                    else if(this.settlementclicked){
                        item.tint = this.clickedcolorcode;
                        item.interactive = true;
                    }
                    else{
                        item.tint = this.defaultcolorcode;
                        item.interactive = true;
                    }
                }
                if(buildables[i] == "city"){
                    item.on("pointerdown", this.buildCityStep1, this)
                    if(myInventory["ore"] < 3 || myInventory["wheat"] < 2){
                        item.tint = this.unavailablecolorcode;
                        item.interactive = false;
                    }
                    else if(this.cityclicked){
                        item.tint = this.clickedcolorcode;
                        item.interactive = true;
                    }
                    else{
                        item.tint = this.defaultcolorcode;
                        item.interactive = true;
                    }
                }
                

                let number = new Text(String(myInventory[buildables[i]]));
                number.y = item.y + this.scaleer/2;
                number.x = item.x;
                number.anchor.set(0.5);

                this.addChild(item)
                this.addChild(number)
                
            })
        }
        Assets.load(this.base_url + "images/" + "trade_button.png").then(texture => {
            let item = Sprite.from(texture)
            item.scale.set(this.scaleer/2000, this.scaleer/2000)
            item.anchor.set(0.5);
            item.x = this.screenWidth / 2 - buildables.length*100 - 100;
            item.y = this.screenHeight / 2 + this.mapHeight;
            item.interactive = true;
            item.on("pointerdown", this.playerTrade, this)
            this.addChild(item)
        })
        Assets.load(this.base_url + "images/" + "development_card.png").then(texture => {
            let item = Sprite.from(texture)
            item.scale.set(this.scaleer/2000, this.scaleer/2000)
            item.anchor.set(0.5);
            item.x = this.screenWidth / 2 - buildables.length*100 - 200;
            item.y = this.screenHeight / 2 + this.mapHeight;
            item.interactive = true;
            item.on("pointerdown", this.buyDevelopmentCard, this)
            if(myInventory["wheat"] < 1 || myInventory["ore"] < 1 || myInventory["sheep"] < 1){
                item.tint = this.unavailablecolorcode;
                item.interactive = false;
            }
            else{
                item.tint = this.defaultcolorcode;
                item.interactive = true;
            }
            this.addChild(item)
        })
        let hiddem_developments = myInventory.hidden_developments
        for(let i = 0; i< hiddem_developments.length; i++){
            let name = hiddem_developments[i].card;
            Assets.load(this.base_url + "images/" + name+".png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.screenWidth / 2 - buildables.length*100 - 300 - (i)*60;
                item.y = this.screenHeight / 2 + this.mapHeight;
                item.interactive = true;
                item.on("pointerdown", () => {this.playDevelopmentCard(name)}, this)
                this.addChild(item)
            })
        }
        
        for(let i = 0; i< this.dices.length; i++){
            let status = this.dices[i].status;
            Assets.load(this.base_url + "images/" + "dice_"+status+".png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.screenWidth / 2 + items.length*100 + (i)*60;
                item.y = this.screenHeight / 2 + this.mapHeight;
                item.interactive = true;
                item.on("pointerdown", this.trowDice, this)
                this.addChild(item)
            })
        }

        Assets.load(this.base_url + "images/" + "arrow_button.png").then(texture => {
            let end_turn = Sprite.from(texture)
            end_turn.scale.set(this.scaleer/2000, this.scaleer/2000)
            end_turn.anchor.set(0.5);
            end_turn.x = this.screenWidth / 2 + items.length*100 + this.dices.length*60 + 0;
            end_turn.y = this.screenHeight / 2 + this.mapHeight;
            end_turn.on("pointerdown", this.endTurn, this);
            end_turn.interactive = true;
            this.addChild(end_turn)
        })
        
    }

    private clear_hud(): void{
        while(this.children[0]) { 
            this.removeChild(this.children[0]);
        }
    }
    public loadHud(): any {
        let self = this;
        const xhttp = new XMLHttpRequest();
        xhttp.onload = function() {
            self.inventories = JSON.parse(this.responseText).inventories;
            self.drawHud();
            }
        xhttp.open("GET", this.url+"hud", true);
        xhttp.send();
        const xhttp2 = new XMLHttpRequest();
        xhttp2.onload = function() {
            let dices = JSON.parse(this.responseText).dice.dices;
            self.dices = [];
            for(let i = 0; i < dices.length; i++){
                self.dices.push(new dice(dices[i].state))
            }
            self.drawHud();
            }
        xhttp2.open("GET", this.url+"meta", true);
        xhttp2.send();
    }
    
    private trowDice(): any {
        const xhttp = new XMLHttpRequest();
        xhttp.open("PUT", this.url+"move/dice_throw/"+this.color, true);
        let self = this;
        xhttp.onload = function() {
            self.loadHud();
            self.parentObject.meta?.loadMeta();
        }
        xhttp.send();
    }

    private endTurn(): any {
        const xhttp = new XMLHttpRequest();
        xhttp.open("PUT", this.url+"move/end/"+this.color, true);
        let self = this;
        xhttp.onload = function() {
            self.loadHud();
            self.parentObject.meta?.loadMeta();
        }
        xhttp.send();
    }

    private buyDevelopmentCard(): any {
        if(confirm("Do you want to buy a development card?")){
            const xhttp = new XMLHttpRequest();
            xhttp.open("PUT", this.url+"move/draw_development_card/"+this.color, true);
            let self = this;
            xhttp.onload = function() {
                self.loadHud();
            }
            xhttp.send(); 
        }       
    }

    private playDevelopmentCard(card: string): any {
        let name = card;
        if(name == "plenty_year"){
            name = "plenty year"
        }
        else if (card == "street_build"){
            name = "street build"
        }
        if(card == "victory"){
            alert("You can not play a victory card!")
        }
        else if(confirm("Do you want to play a "+name+" card?")){
            const xhttp = new XMLHttpRequest();
            xhttp.open("PUT", this.url+"move/play_development_card/"+this.color+"/"+card, true);
            let self = this;
            xhttp.onload = function() {
                self.parentObject.reload()
            }
            xhttp.send(); 
        }       
    }

    public buildStreetStep1(): any {
        if(!this.streetclicked){
            const xhttp = new XMLHttpRequest();
            let self = this;
            xhttp.open("PUT", this.url+"options/street_locations/"+this.color, true);
            xhttp.onload = function() {
                self.streetclicked = true
                self.loadHud()
                self.parentObject.map?.loadMap()
            }
            xhttp.send();
        }
        else{
            const xhttp = new XMLHttpRequest();
            let self = this;
            xhttp.open("PUT", this.url+"options/clear", true);
            xhttp.onload = function() {
                self.streetclicked = false
                self.loadHud()
                self.parentObject.map?.loadMap()
            }
            xhttp.send();
        }   
    }
    public buildSettlementStep1(): any {
        if(!this.settlementclicked){
            const xhttp = new XMLHttpRequest();
            let self = this;
            xhttp.open("PUT", this.url+"options/settlement_locations/"+this.color, true);
            xhttp.onload = function() {
                self.settlementclicked = true
                self.loadHud()
                self.parentObject.map?.loadMap()
            }
            xhttp.send();
        }
        else{
            const xhttp = new XMLHttpRequest();
            let self = this;
            xhttp.open("PUT", this.url+"options/clear", true);
            xhttp.onload = function() {
                self.settlementclicked = false
                self.loadHud()
                self.parentObject.map?.loadMap()
            }
            xhttp.send();
        }   
    }
    public buildCityStep1(): any {
        if(!this.cityclicked){
            const xhttp = new XMLHttpRequest();
            let self = this;
            xhttp.open("PUT", this.url+"options/city_locations/"+this.color, true);
            xhttp.onload = function() {
                self.cityclicked = true
                self.loadHud()
                self.parentObject.map?.loadMap()
            }
            xhttp.send();
        }
        else{
            const xhttp = new XMLHttpRequest();
            let self = this;
            xhttp.open("PUT", this.url+"options/clear", true);
            xhttp.onload = function() {
                self.cityclicked = false
                self.loadHud()
                self.parentObject.map?.loadMap()
            }
            xhttp.send();
        }   
    }
    public bankTrade(item: string, count: number): any {
        if(this.parentObject.window == undefined){
            let items = ["wood", "clay", "sheep", "wheat", "ore"];
            let bankTradeWindow = new BankTrade(this.parentObject, 600, 500, this.parentObject.screen.width, this.parentObject.screen.height, 100, items, count, item, this.color, this.url, this.base_url)
            this.parentObject.setWindow(bankTradeWindow)
            this.parentObject.stage.addChild(bankTradeWindow)
            this.parentObject.reload()
        }
    }
    public playerTrade(): any {
        if(this.parentObject.window == undefined){
            let items = ["wood", "clay", "sheep", "wheat", "ore"];
            let playerTradeWindow = new PlayerTrade(this.parentObject, 500, 700, this.parentObject.screen.width, this.parentObject.screen.height, 100, items, this.color, this.url, this.base_url)
            this.parentObject.setWindow(playerTradeWindow)
            this.parentObject.stage.addChild(playerTradeWindow)
            this.parentObject.reload()
        }
    }
}