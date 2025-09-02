import { Assets, Graphics, Sprite, Text } from "pixi.js";
import { Cgame } from "./cgame";
import { inventory } from "./hud";
import { Trade } from "./meta";

export class Window extends Graphics {
    public parentObject: Cgame;
    protected window_width: number;
    protected window_height: number;
    protected screen_width: number;
    protected screen_height: number;
    protected text: string;
    protected scaleer: number;
    protected denieable: boolean;
    protected confirmButton: Sprite | undefined;
    protected top_x: number;
    protected top_y: number;
    protected url: string;
    protected base_url: string;
    constructor(parentObject: Cgame, width: number, height: number, screen_width: number, screen_height: number, text: string, scaleer: number, denieable: boolean, url: string, base_url: string){
        super()
        this.window_width = width;
        this.window_height = height;
        this.screen_width = screen_width;
        this.screen_height = screen_height;
        this.text = text;
        this.scaleer = scaleer;
        this.parentObject = parentObject;
        this.denieable = denieable;
        this.url = url;
        this.base_url = base_url;
        this.confirmButton = undefined;

        
        this.top_x = this.screen_width/2 - this.window_width/2;
        this.top_y = this.screen_height/2 - this.window_height/2;
        
        this.draw();
    }

    protected draw(){
        while(this.children[0]) { 
            this.removeChild(this.children[0]);
        }
        this.beginFill(0xFFFFFF);
        this.drawRect(this.top_x, this.top_y, this.window_width, this.window_height);
        let title = new Text(this.text);
        title.x = this.top_x
        title.y = this.top_y
        this.addChild(title);
        this.beginFill(0x000000);
        this.drawRect(this.top_x, this.top_y+title.height, this.window_width, 1);
        Assets.load(this.base_url + "images/" + "confirm_button.png").then(texture => {
            let confirm = Sprite.from(texture)
            confirm.scale.set(this.scaleer/2000, this.scaleer/2000)
            confirm.anchor.set(1);
            confirm.x = this.top_x + this.width;
            confirm.y = this.top_y + this.height;
            confirm.on("pointerdown", this.accept, this);
            confirm.interactive = true;
            this.addChild(confirm)
            this.confirmButton = confirm;
        })
        if(this.denieable){
            Assets.load(this.base_url + "images/" + "deny_button.png").then(texture => {
                let confirm = Sprite.from(texture)
                confirm.scale.set(this.scaleer/2000, this.scaleer/2000)
                confirm.anchor.set(1);
                confirm.x = this.top_x + this.width - this.scaleer/2;
                confirm.y = this.top_y + this.height;
                confirm.on("pointerdown", this.deny, this);
                confirm.interactive = true;
                this.addChild(confirm)
            })
        }
    }

    protected accept(){
        this.parentObject.removeWindow()
        this.destroy()
    }
    protected deny(){
        this.parentObject.removeWindow()
        this.destroy()
    }
}


export class ReturnCard extends Window{
    protected items: string[];
    protected count: number;
    protected selected: number;
    protected selectedList: number[];
    protected inventory: inventory | undefined;
    protected color: string;
    protected midtext: string;
    protected plus: boolean;
    protected keep: boolean;
    constructor(parentObject: Cgame, width: number, height: number, screen_width: number, screen_height: number, scaleer: number, items: string[], count: number, color: string, url: string, base_url: string, plus: boolean = false, text1: string = "You must return ", text2: string = " items!", text3: string = "You will keep the follwing items:", keep: boolean = true){
        super(parentObject, width, height, screen_width, screen_height, text1 + count + text2, scaleer, false, url, base_url)
        this.items = items;
        this.count = count;
        this.selectedList = [];
        for(let i = 0; i < this.items.length; i++){
            this.selectedList.push(0)
        }
        this.selected = 0;
        this.color = color;
        this.midtext = text3;
        this.plus = plus;
        this.keep = keep;
        this.drawChild();
    }

    protected load(){
        if(this.parentObject.hud != undefined){
            let myInventory: inventory = this.parentObject.hud.inventories.find(inv => inv.owner == this.color) as inventory
            if(myInventory){
                this.inventory = myInventory;
            }
        }
    }

    protected drawChild(){
        this.draw();
        let item_count = this.items.length;
        for(let i = 0; i<item_count; i++){
            Assets.load(this.base_url + "images/" + this.items[i]+"_item.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + this.height/4;

                let number = new Text(this.selectedList[i]);
                number.y = item.y + this.scaleer/2;
                number.x = item.x;
                number.anchor.set(0.5);

                this.addChild(item);
                this.addChild(number);
                
            })
            Assets.load(this.base_url + "images/" + "minus_button.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/4000, this.scaleer/4000)
                item.anchor.set(1, 0);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + this.height/4 + this.scaleer;
                item.interactive = true;
                item.on("pointerdown", () => this.remove(this.items[i]), this);
                this.addChild(item);
            })
            Assets.load(this.base_url + "images/" + "plus_button.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/4000, this.scaleer/4000)
                item.anchor.set(0);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + this.height/4 + this.scaleer;
                item.interactive = true;
                item.on("pointerdown", () => this.add(this.items[i]), this);
                this.addChild(item)
            })
        }
        if(this.keep){
            let keep = new Text(this.midtext)
            keep.x = this.top_x;
            keep.y = this.top_y + 9*this.height/16;
            this.addChild(keep)
            for(let i = 0; i<item_count; i++){
                Assets.load(this.base_url + "images/" + this.items[i]+"_item.png").then(texture => {
                    let item = Sprite.from(texture)
                    item.scale.set(this.scaleer/2000, this.scaleer/2000)
                    item.anchor.set(0.5);
                    item.x = this.top_x + i*100+50;
                    item.y = this.top_y + 3*this.height/4;
    
                    let stock = 0;
                    let itemName = this.items[i];
                    this.load();
                    if(this.inventory != undefined){
                        if(itemName == "wood" || itemName == "clay" || itemName == "wheat" || itemName == "sheep" || itemName == "ore"){
                            stock = this.inventory[itemName]
                        }
                    }
                    let number = new Text(stock - this.selectedList[i]);
                    if(this.plus){
                        number = new Text(stock + this.selectedList[i]);
                    }
                    number.y = item.y + this.scaleer/2;
                    number.x = item.x;
                    number.anchor.set(0.5);
    
                    this.addChild(item);
                    this.addChild(number);
                    
                })
            }
        }
        

        let status = new Text(this.selected+"/"+this.count)
        status.x = this.top_x + this.width - this.scaleer;
        status.y = this.top_y + this.height;
        status.anchor.set(1);
        this.addChild(status)
    }



    protected override accept(){
        if(this.selected == this.count){
            let xhttp = new XMLHttpRequest;
            let self = this;
            xhttp.onload = function () {
                if(this.status == 200){
                    if(self.parentObject.meta != undefined){
                        self.parentObject.meta.window = undefined;
                    }
                    self.parentObject.reload();
                    self.destroy();
                }
            }
            xhttp.open("PUT", this.parentObject.url+"move/return_cards/"+this.color+"/"+this.getSelectedCount("wood")+"/"+this.getSelectedCount("clay")+"/"+this.getSelectedCount("sheep")+"/"+this.getSelectedCount("wheat")+"/"+this.getSelectedCount("ore"), true)
            xhttp.send()
        }
        else{
            console.log("wrong item count")
        }
    }

    protected add(item: string){
        this.load()
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            if(this.inventory != undefined){
                if(item == "wood" || item == "clay" || item == "wheat" || item == "sheep" || item == "ore"){
                    if(this.inventory[item] > this.selectedList[index]){
                        this.selectedList[index] += 1
                        this.selected += 1
                        this.drawChild()
                    }
                }
            }
        }
    }

    protected remove(item: string){
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            if(this.selectedList[index] > 0){
                this.selectedList[index] -= 1
                this.selected -= 1
                this.drawChild()
            }
        }
    }

    protected getSelectedCount(item: string){
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            return this.selectedList[index]
        }
        else{
            return 0
        }
    }
}


export class GetCard extends ReturnCard{
    constructor(parentObject: Cgame, width: number, height: number, screen_width: number, screen_height: number, scaleer: number, items: string[], count: number, color: string, keep: boolean = true, url: string, base_url: string){
        super(parentObject, width, height, screen_width, screen_height, scaleer, items, count, color, url, base_url, true, "You can choose ", " items.", "You will have the following items:", keep)
    }
    protected override add(item: string){
        this.load()
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            if(item == "wood" || item == "clay" || item == "wheat" || item == "sheep" || item == "ore"){
                this.selectedList[index] += 1
                this.selected += 1
                this.drawChild()
            }
        }
    }
    protected override accept(){
        if(this.selected == this.count){
            let xhttp = new XMLHttpRequest;
            let self = this;
            xhttp.onload = function () {
                if(this.status == 200){
                    if(self.parentObject.meta != undefined){
                        self.parentObject.meta.window = undefined;
                    }
                    self.parentObject.reload();
                    self.destroy();
                }
            }
            xhttp.open("PUT", this.parentObject.url+"move/get_cards/"+this.color+"/"+this.getSelectedCount("wood")+"/"+this.getSelectedCount("clay")+"/"+this.getSelectedCount("sheep")+"/"+this.getSelectedCount("wheat")+"/"+this.getSelectedCount("ore"), true)
            xhttp.send()
        }
        else{
            console.log("wrong item count")
        }
    }
}

export class ChooseItem extends GetCard{
    constructor(parentObject: Cgame, width: number, height: number, screen_width: number, screen_height: number, scaleer: number, items: string[], count: number, color: string, url: string, base_url: string){
        super(parentObject, width, height, screen_width, screen_height, scaleer, items, count, color, false, url, base_url)
    }
}

export class Monopoly extends ChooseItem{
    constructor(parentObject: Cgame, width: number, height: number, screen_width: number, screen_height: number, scaleer: number, items: string[], color: string, url: string, base_url: string){
        super(parentObject, width, height, screen_width, screen_height, scaleer, items, 1, color, url, base_url)
    }
    protected override accept(){
        if(this.selected == this.count){
            let xhttp = new XMLHttpRequest;
            let self = this;
            xhttp.onload = function () {
                if(this.status == 200){
                    if(self.parentObject.meta != undefined){
                        self.parentObject.meta.window = undefined;
                    }
                    self.parentObject.reload();
                    self.destroy();
                }
            }
            let selected = ""
            if(this.getSelectedCount("wood") > 0){
                selected = "wood"
            }
            if(this.getSelectedCount("clay") > 0){
                selected = "clay"
            }
            if(this.getSelectedCount("sheep") > 0){
                selected = "sheep"
            }
            if(this.getSelectedCount("wheat") > 0){
                selected = "wheat"
            }
            if(this.getSelectedCount("ore") > 0){
                selected = "ore"
            }
            xhttp.open("PUT", this.parentObject.url+"move/monopoly/"+this.color+"/"+selected, true)
            xhttp.send()
        }
        else{
            console.log("wrong item count")
        }
    }
}


export class BankTrade extends Window{
    private items: string[];
    private give: number;
    private giveName: string;
    private selectedList: number[];
    private selected: number;
    private getName: string | undefined;
    private inventory: inventory | undefined;
    private color: string;
    constructor(parentObject: Cgame, width: number, height: number, screen_width: number, screen_height: number, scaleer: number, items: string[], give: number, giveName: string, color: string, url: string, base_url: string){
        super(parentObject, width, height, screen_width, screen_height, "Bank trade: you give "+give + " " + giveName +", what do you get?", scaleer, true, url, base_url)
        this.give = give;
        this.giveName = giveName;
        this.items = items;
        this.color = color;
        this.selectedList = [];
        for(let i = 0; i < this.items.length; i++){
            this.selectedList.push(0)
        }
        this.selected = 0;
        this.getName = undefined;
        this.drawChild();
    }

    protected load(){
        if(this.parentObject.hud != undefined){
            let myInventory: inventory = this.parentObject.hud.inventories.find(inv => inv.owner == this.color) as inventory
            if(myInventory){
                this.inventory = myInventory;
            }
        }
    }

    protected drawChild(){
        this.draw();
        let item_count = this.items.length;
        for(let i = 0; i<item_count; i++){
            Assets.load(this.base_url + "images/" + this.items[i]+"_item.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + this.height/4;

                let number = new Text(this.selectedList[i]);
                number.y = item.y + this.scaleer/2;
                number.x = item.x;
                number.anchor.set(0.5);

                this.addChild(item);
                this.addChild(number);
                
            })
            Assets.load(this.base_url + "images/" + "minus_button.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/4000, this.scaleer/4000)
                item.anchor.set(1, 0);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + this.height/4 + this.scaleer;
                item.interactive = true;
                item.on("pointerdown", () => this.remove(this.items[i]), this);
                this.addChild(item);
            })
            Assets.load(this.base_url + "images/" + "plus_button.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/4000, this.scaleer/4000)
                item.anchor.set(0);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + this.height/4 + this.scaleer;
                item.interactive = true;
                item.on("pointerdown", () => this.add(this.items[i]), this);
                this.addChild(item)
            })
        }
        let keep = new Text("You will own the follwing items:")
        keep.x = this.top_x;
        keep.y = this.top_y + 9*this.height/16;
        this.addChild(keep)
        for(let i = 0; i<item_count; i++){
            Assets.load(this.items[i]+"_item.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + 3*this.height/4;

                let stock = 0;
                let itemName = this.items[i];
                this.load();
                if(this.inventory != undefined){
                    if(itemName == "wood" || itemName == "clay" || itemName == "wheat" || itemName == "sheep" || itemName == "ore"){
                        stock = this.inventory[itemName]
                        if(itemName == this.giveName){
                            stock -= this.give;
                        }
                    }
                }
                let number = new Text(stock + this.selectedList[i]);
                number.y = item.y + this.scaleer/2;
                number.x = item.x;
                number.anchor.set(0.5);

                this.addChild(item);
                this.addChild(number);
                
            })
        }

        let status = new Text(this.selected+"/1")
        status.x = this.top_x + this.width - this.scaleer;
        status.y = this.top_y + this.height;
        status.anchor.set(1);
        this.addChild(status)
    }



    protected override accept(){
        if(this.selected == 1){
            let xhttp = new XMLHttpRequest;
            let self = this;
            xhttp.onload = function () {
                if(this.status == 200){
                    if(self.parentObject.meta != undefined){
                        self.parentObject.meta.window = undefined;
                    }
                    self.parentObject.reload();
                    self.parentObject.removeWindow()
                    self.destroy();
                }
            }
            xhttp.open("PUT", this.parentObject.url+"move/bank_trade/"+this.color+"/"+this.giveName+"/"+this.getName, true)
            xhttp.send()
        }
        else{
            console.log("wrong item count")
        }
    }

    private add(item: string){
        this.load()
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            if(this.inventory != undefined){
                if(item == "wood" || item == "clay" || item == "wheat" || item == "sheep" || item == "ore"){
                    this.selectedList[index] += 1
                    this.getName = item;
                    this.selected += 1
                    this.drawChild()
                }
            }
        }
    }

    private remove(item: string){
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            if(this.selectedList[index] > 0){
                this.selectedList[index] -= 1
                this.selected -= 1
                this.drawChild()
            }
        }
    }
}


export class PlayerTrade extends Window{
    private items: string[];
    private give: number[];
    private get: number[];
    private inventory: inventory | undefined;
    private color: string;
    constructor(parentObject: Cgame, width: number, height: number, screen_width: number, screen_height: number, scaleer: number, items: string[], color: string, url: string, base_url: string){
        super(parentObject, width, height, screen_width, screen_height, "Player Trade", scaleer, true, url, base_url)
        this.items = items;
        this.give = [];
        this.get = [];
        for(let i = 0; i < this.items.length; i++){
            this.give.push(0)
            this.get.push(0)
        }
        this.color = color;
        this.drawChild();
    }

    protected load(){
        if(this.parentObject.hud != undefined){
            let myInventory: inventory = this.parentObject.hud.inventories.find(inv => inv.owner == this.color) as inventory
            if(myInventory){
                this.inventory = myInventory;
            }
        }
    }

    protected drawChild(){
        this.draw();
        let item_count = this.items.length;
        for(let i = 0; i<item_count; i++){
            Assets.load(this.base_url + "images/" + this.items[i]+"_item.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + this.height/8;

                let number = new Text(this.give[i]);
                number.y = item.y + this.scaleer/2;
                number.x = item.x;
                number.anchor.set(0.5);

                this.addChild(item);
                this.addChild(number);
                
            })
            Assets.load(this.base_url + "images/" + "minus_button.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/4000, this.scaleer/4000)
                item.anchor.set(1, 0);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + this.height/8 + this.scaleer;
                item.interactive = true;
                item.on("pointerdown", () => this.removeGive(this.items[i]), this);
                this.addChild(item);
            })
            Assets.load(this.base_url + "images/" + "plus_button.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/4000, this.scaleer/4000)
                item.anchor.set(0);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + this.height/8 + this.scaleer;
                item.interactive = true;
                item.on("pointerdown", () => this.addGive(this.items[i]), this);
                this.addChild(item)
            })
        }
        for(let i = 0; i<item_count; i++){
            Assets.load(this.base_url + "images/" + this.base_url + "images/" + this.items[i]+"_item.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + 3*this.height/8;

                let number = new Text(this.get[i]);
                number.y = item.y + this.scaleer/2;
                number.x = item.x;
                number.anchor.set(0.5);

                this.addChild(item);
                this.addChild(number);
                
            })
            Assets.load(this.base_url + "images/" + "minus_button.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/4000, this.scaleer/4000)
                item.anchor.set(1, 0);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + 3*this.height/8 + this.scaleer;
                item.interactive = true;
                item.on("pointerdown", () => this.removeGet(this.items[i]), this);
                this.addChild(item);
            })
            Assets.load(this.base_url + "images/" + "plus_button.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/4000, this.scaleer/4000)
                item.anchor.set(0);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + 3*this.height/8 + this.scaleer;
                item.interactive = true;
                item.on("pointerdown", () => this.addGet(this.items[i]), this);
                this.addChild(item)
            })
        }
        let keep = new Text("You will own the follwing items:")
        keep.x = this.top_x;
        keep.y = this.top_y + 10*this.height/16;
        this.addChild(keep)
        for(let i = 0; i<item_count; i++){
            Assets.load(this.base_url + "images/" + this.items[i]+"_item.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + 3*this.height/4;

                let stock = 0;
                let itemName = this.items[i];
                this.load();
                if(this.inventory != undefined){
                    if(itemName == "wood" || itemName == "clay" || itemName == "wheat" || itemName == "sheep" || itemName == "ore"){
                        stock = this.inventory[itemName] - this.give[i] + this.get[i]
                    }
                }
                let number = new Text(stock);
                number.y = item.y + this.scaleer/2;
                number.x = item.x;
                number.anchor.set(0.5);

                this.addChild(item);
                this.addChild(number);
                
            })
        }
        let sumGive = this.give.reduce((result, current) => result + current)
        let sumGet = this.get.reduce((result, current) => result + current)


        let text = "You will give "+sumGive+" and you will get "+sumGet+"."
        if(sumGet == 0 || sumGive == 0){
            text = "Items cannot be gifted!"
        }
        let status = new Text(text)
        status.x = this.top_x + this.width - this.scaleer;
        status.y = this.top_y + this.height;
        status.anchor.set(1);
        this.addChild(status)
    }



    protected override accept(){
        let xhttp = new XMLHttpRequest;
        let self = this;
        xhttp.onload = function () {
            if(this.status == 200){
                if(self.parentObject.meta != undefined){
                    self.parentObject.meta.window = undefined;
                }
                self.parentObject.reload();
                self.parentObject.removeWindow()
                self.destroy();
            }
        }
        xhttp.open("PUT", this.parentObject.url+"move/player_trade/"+this.color+"/"+this.getSelectedCountGive("wood")+"/"+this.getSelectedCountGive("clay")
                    +"/"+this.getSelectedCountGive("sheep")+"/"+this.getSelectedCountGive("wheat")+"/"+this.getSelectedCountGive("ore")
                    +"/"+this.getSelectedCountGet("wood")+"/"+this.getSelectedCountGet("clay")+"/"+this.getSelectedCountGet("sheep")
                    +"/"+this.getSelectedCountGet("wheat")+"/"+this.getSelectedCountGet("ore"), true)
        xhttp.send()
        
    }

    private addGive(item: string){
        this.load()
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            if(this.inventory != undefined){
                if(item == "wood" || item == "clay" || item == "wheat" || item == "sheep" || item == "ore"){
                    if(this.inventory[item] > this.give[index]){
                        this.give[index] += 1
                        this.drawChild()
                    }
                }
            }
        }
    }

    private addGet(item: string){
        this.load()
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            if(this.inventory != undefined){
                if(item == "wood" || item == "clay" || item == "wheat" || item == "sheep" || item == "ore"){
                    this.get[index] += 1;
                    this.drawChild()
                }
            }
        }
    }

    private removeGive(item: string){
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            if(this.give[index] > 0){
                this.give[index] -= 1
                this.drawChild()
            }
        }
    }

    private removeGet(item: string){
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            if(this.get[index] > 0){
                this.get[index] -= 1
                this.drawChild()
            }
        }
    }

    private getSelectedCountGive(item: string){
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            return this.give[index]
        }
        else{
            return 0
        }
    }

    private getSelectedCountGet(item: string){
        let index = this.items.findIndex(item_alt => item_alt == item)
        if(index != undefined){
            return this.get[index]
        }
        else{
            return 0
        }
    }
}


export class PlayerTradeAnswer extends Window{
    private trade: Trade;
    private inventory: inventory | undefined;
    private color: string;
    constructor(parentObject: Cgame, width: number, height: number, screen_width: number, screen_height: number, scaleer: number, trade: Trade, color: string, url: string, base_url: string){
        super(parentObject, width, height, screen_width, screen_height, "Player Trade", scaleer, true, url, base_url)
        this.color = color;
        this.trade = trade;
        this.trade.flip();
        this.drawChild();
    }

    protected load(){
        if(this.parentObject.hud != undefined){
            let myInventory: inventory = this.parentObject.hud.inventories.find(inv => inv.owner == this.color) as inventory
            if(myInventory){
                this.inventory = myInventory;
            }
        }
    }

    protected drawChild(){
        this.draw();
        for(let i = 0; i<this.trade.give.names().length; i++){
            let name = this.trade.give.names()[i];
            Assets.load(this.base_url + "images/" + name+"_item.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + this.height/8;

                let number = new Text(this.trade.give.get(name));
                number.y = item.y + this.scaleer/2;
                number.x = item.x;
                number.anchor.set(0.5);

                this.addChild(item);
                this.addChild(number);
                
            })
        }
        for(let i = 0; i<this.trade.get.names().length; i++){
            let name = this.trade.get.names()[i];
            Assets.load(this.base_url + "images/" + name+"_item.png").then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/2000, this.scaleer/2000)
                item.anchor.set(0.5);
                item.x = this.top_x + i*100+50;
                item.y = this.top_y + 3*this.height/8;

                let number = new Text(this.trade.get.get(name));
                number.y = item.y + this.scaleer/2;
                number.x = item.x;
                number.anchor.set(0.5);

                this.addChild(item);
                this.addChild(number);
                
            })
        }
        let stock: number[] = [];
        let affordable = true;
        this.load();
        for(let i = 0; i<this.trade.get.names().length; i++){
            let name = this.trade.get.names()[i];
            if(this.inventory != undefined){
                if(name == "wood" || name == "clay" || name == "wheat" || name == "sheep" || name == "ore"){
                    stock[i] = this.inventory[name] + this.trade.get.get(name) - this.trade.give.get(name)
                    if(stock[i] < 0){
                        affordable = false;
                        break;
                    }
                }
            }
        }
        if(affordable){
            let keep = new Text("You will own the follwing items:")
            keep.x = this.top_x;
            keep.y = this.top_y + 10*this.height/16;
            this.addChild(keep)
            for(let i = 0; i<this.trade.get.names().length; i++){
                let name = this.trade.get.names()[i];
                Assets.load(this.base_url + "images/" + name+"_item.png").then(texture => {
                    let item = Sprite.from(texture)
                    item.scale.set(this.scaleer/2000, this.scaleer/2000)
                    item.anchor.set(0.5);
                    item.x = this.top_x + i*100+50;
                    item.y = this.top_y + 3*this.height/4;

                    
                    let number = new Text(stock[i]);
                    number.y = item.y + this.scaleer/2;
                    number.x = item.x;
                    number.anchor.set(0.5);

                    this.addChild(item);
                    this.addChild(number);
                    
                })
            }
        }
        else{
            let keep = new Text("You can not accept the deal, please deny it.")
            keep.x = this.top_x;
            keep.y = this.top_y + 10*this.height/16;
            this.addChild(keep)
        }
    }
    protected override accept(){
        let xhttp = new XMLHttpRequest;
        let self = this;
        xhttp.onload = function () {
            if(this.status == 200){
                if(self.parentObject.meta != undefined){
                    self.parentObject.meta.window = undefined;
                }
                self.parentObject.reload();
                self.parentObject.removeWindow()
                self.destroy();
            }
        }
        xhttp.open("PUT", this.parentObject.url+"move/reply_to_active_trade/"+this.color+"/1", true)
        xhttp.send();
    }
    protected override deny(){
        let xhttp = new XMLHttpRequest;
        let self = this;
        xhttp.onload = function () {
            if(this.status == 200){
                if(self.parentObject.meta != undefined){
                    self.parentObject.meta.window = undefined;
                }
                self.parentObject.removeWindow()
                self.destroy();
                self.parentObject.reload();
            }
        }
        xhttp.open("PUT", this.parentObject.url+"move/reply_to_active_trade/"+this.color+"/0", true)
        xhttp.send();
    }
}