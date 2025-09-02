import { Container, FederatedWheelEvent, FederatedPointerEvent, Sprite, Text, Assets} from "pixi.js";
import { Cgame } from "./cgame";
//import data from "../dynamic/data.json";

export class map_object{
    public x: number;
    public y: number;
    public where: number;
    public type: string;
    public number: number | undefined;
    public owner: string;
    public trading: string | undefined;
    constructor(x: number, y: number, where: number, type: string, number: number, owner: string){
        this.x = x;
        this.y = y;
        this.where = where;
        this.type = type;
        this.number = number;
        this.owner = owner;
    }
}

export class Map extends Container {
    public parentObject: Cgame;
    private scaleer: number;
    private screenWidth: number;
    private screenHeight: number;
    private x_shift: number;
    private y_shift: number;
    private x_shift_start: number;
    private y_shift_start: number;
    private dragging: boolean;
    private draggable: boolean;
    private map: map_object[];
    private url: string;
    private base_url: string;
    private color: string;
    constructor(parentObject: Cgame, screenWidth: number, screenHeight: number, scaleer: number, url: string, base_url: string, color: string) {
        super();
        this.parentObject = parentObject;
        this.scaleer = scaleer
        this.x_shift = 0
        this.y_shift = 0
        this.x_shift_start = 0
        this.y_shift_start = 0
        this.dragging = false
        this.draggable = true;
        this.url = url;
        this.base_url = base_url;
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        this.color = color;
        this.map = [new map_object(0, 0, 0, "desert", 0, "nobody")];
        this.drawMap()
        setTimeout(() => {this.drawMap()}, 500);
        
        this.interactive = true;


        this.on("wheel", this.onScoll, this);
        this.on("mousedown", this.onClick, this)
        this.on("mousemove", this.onMove, this)
        this.on("mouseup", this.onRelease, this)

        let self = this;
        self.loadMap();
        
        setInterval(function() {
            self.loadMap();
        }, 100);
        
    }

    private onScoll(e: FederatedWheelEvent): void {
        let scrollDelta = e.deltaY * 0.1
        this.scaleer -= scrollDelta
        this.drawMap()
    }
    private onClick(e: FederatedPointerEvent): void {
        if(this.draggable){
            this.dragging = true
            this.draggable = false
            this.x_shift_start = (e.x - this.screenWidth/2) - this.x_shift
            this.y_shift_start = (e.y - this.screenHeight/2) - this.y_shift
            //this.onMove(e)
        }
    }
    private onMove(e: FederatedPointerEvent): void {
        if(this.dragging && e.buttons == 1){
            this.x_shift = e.x - this.screenWidth/2
            this.y_shift = e.y - this.screenHeight/2
            this.x_shift -= this.x_shift_start
            this.y_shift -= this.y_shift_start
            
            this.drawMap()
        }
        
    }
    private onRelease(e: FederatedPointerEvent): void {
        this.onMove(e)
        this.dragging = false
        this.x_shift_start = this.x_shift
        this.y_shift_start = this.y_shift
        setTimeout(() => {this.draggable = true}, 100);
    }

    public loadMap(): any {
        const xhttp = new XMLHttpRequest();
        let self = this;
        xhttp.onload = function() {
            self.map = JSON.parse(this.responseText).map;
            self.drawMap();
            }
        xhttp.open("GET", this.url+"map", true);
        xhttp.send();
    }
    public drawMap(): void{
        this.clear()
        let mapItems = this.map
        //let angles = [30,90,150,210,270,330]
        for(let i = 0; i < mapItems.length; i++){
            let itemData = mapItems[i]
            let suffix = ".png"
            let owner = itemData.owner;
            if(this.classifyItem(itemData.type) == 1 || this.classifyItem(itemData.type) == 2){
                if(owner != "shadow"){
                    suffix = "_" + owner + suffix;
                }
            }
            else if(this.classifyItem(itemData.type) == 3){
                suffix = "_" + itemData.trading + suffix;
            }
            Assets.load(this.base_url + "images/" +itemData.type+suffix).then(texture => {
                let item = Sprite.from(texture)
                item.scale.set(this.scaleer/200, this.scaleer/200)

                item.anchor.set(0.5);
                item.x = this.screenWidth / 2 + (Math.sqrt(3)*this.scaleer)*itemData.x;
                item.y = this.screenHeight / 2 + 1.5*this.scaleer*itemData.y;
                if(Math.abs(itemData.y % 2) == 1){
                    item.x = item.x + 0.5*(Math.sqrt(3)*this.scaleer)
                }
                item.x += this.x_shift;
                item.y += this.y_shift;

                if(this.classifyItem(itemData.type) == 1){
                    if(itemData.where == 0){
                        item.y -= this.scaleer
                    }
                    if(itemData.where == 1){
                        item.y += this.scaleer
                    }
                    item.interactive = true;
                    if(owner == "shadow"){
                        if(itemData.type == "settlement"){
                            item.on("pointerdown", () => {this.buildSettlementStep2(itemData.x, itemData.y, itemData.where)}, this)
                        }
                        else if(itemData.type == "city"){
                            item.on("pointerdown", () => {this.buildCityStep2(itemData.x, itemData.y, itemData.where)}, this)
                        }
                    }
                    else{
                        item.on("pointerdown", () => {this.cornerClick(itemData.owner)}, this)
                    }
                    this.addChild(item)
                }
                else if(this.classifyItem(itemData.type) == 2){
                    if(itemData.where == 0){
                        item.y -= 3*this.scaleer/4
                        item.x += (Math.sqrt(3)*this.scaleer)/4
                        item.angle = -70
                    }
                    if(itemData.where == 1){
                        item.y -= 3*this.scaleer/4
                        item.x -= (Math.sqrt(3)*this.scaleer)/4
                        item.angle = 70
                    }
                    if(itemData.where == 2){
                        item.x -= (Math.sqrt(3)*this.scaleer)/2
                    }
                    if(owner == "shadow"){
                        item.interactive = true;
                        item.on("pointerdown", () => {this.buildStreetStep2(itemData.x, itemData.y, itemData.where)}, this)
                    }
                    this.addChild(item)
                }
                else if(this.classifyItem(itemData.type) == 3){
                    item.angle = -150 - itemData.where * 60
                    if(itemData.where == 0){
                        item.x += (Math.sqrt(3)*this.scaleer)/8
                        item.y -= (Math.sqrt(3)*this.scaleer)/4
                    }
                    if(itemData.where == 1){
                        item.x -= (Math.sqrt(3)*this.scaleer)/8
                        item.y -= (Math.sqrt(3)*this.scaleer)/4
                    }
                    if(itemData.where == 2){
                        item.x -= this.scaleer/2
                    }
                    if(itemData.where == 3){
                        item.x -= (Math.sqrt(3)*this.scaleer)/8
                        item.y += (Math.sqrt(3)*this.scaleer)/4
                    }
                    if(itemData.where == 4){
                        item.x += (Math.sqrt(3)*this.scaleer)/8
                        item.y += (Math.sqrt(3)*this.scaleer)/4
                    }
                    if(itemData.where == 5){
                        item.x += this.scaleer/2
                    }
                    this.addChild(item)
                }
                else{
                    //item.angle = angles[Math.floor(Math.random() * angles.length)];
                    if(itemData.type == "robber"){
                        item.angle = 0
                        item.scale.set(this.scaleer/1000, this.scaleer/1000)
                    }
                    else{
                        item.angle = 90
                        if(this.parentObject.meta?.getStatus() == 5){
                            item.interactive = true;
                            item.on("pointerdown", () => {this.moveRobber(itemData.x, itemData.y)}, this)
                        }
                    }
                    let number = new Text(itemData.number)
                    number.x = item.x
                    number.y = item.y
                    number.anchor.set(0.5);
                    number.scale.set(this.scaleer/100, this.scaleer/100)
                    if(itemData.type == "wood" || itemData.type == "wheat" || itemData.type == "clay"){
                        number.style.fill = "white"
                    }
                    this.addChild(item)
                    this.addChild(number)
                }
            })
            
        }
    }
    private classifyItem(name: string): number{
        if(name == "settlement" || name == "city"){
            return 1
        }
        if(name == "street"){
            return 2
        }
        if(name == "harbor"){
            return 3
        }
        return 0
    }
    private clear(): void{
        while(this.children[0]) { 
            this.removeChild(this.children[0]);
        }
    }

    private buildStreetStep2(x: number, y: number, where: number): any {
        const xhttp = new XMLHttpRequest();
        xhttp.open("PUT", this.url+"move/street_build/"+this.color+"/"+x+"/"+y+"/"+where, true);
        let self = this;
        xhttp.onload = function() {
            if(self.parentObject.meta?.getStatus as any == 4){
                self.parentObject.hud?.buildStreetStep1();
            }
            self.loadMap();
            self.parentObject.meta?.loadMeta()
        }
        xhttp.send();
    }
    private buildSettlementStep2(x: number, y: number, where: number): any {
        const xhttp = new XMLHttpRequest();
        xhttp.open("PUT", this.url+"move/settlement_build/"+this.color+"/"+x+"/"+y+"/"+where, true);
        let self = this;
        xhttp.onload = function() {
            if(self.parentObject.meta?.getStatus as any == 4){
                self.parentObject.hud?.buildSettlementStep1();
            }
            self.loadMap();
            self.parentObject.meta?.loadMeta()
        }
        xhttp.send();
    }
    private buildCityStep2(x: number, y: number, where: number): any {
        const xhttp = new XMLHttpRequest();
        xhttp.open("PUT", this.url+"move/city_build/"+this.color+"/"+x+"/"+y+"/"+where, true);
        let self = this;
        xhttp.onload = function() {
            if(self.parentObject.meta?.getStatus as any == 4){
                self.parentObject.hud?.buildCityStep1();
            }
            self.loadMap();
            self.parentObject.meta?.loadMeta()
        }
        xhttp.send();
    }
    private moveRobber(x: number, y: number): any {
        const xhttp = new XMLHttpRequest();
        xhttp.open("PUT", this.url+"move/move_robber/"+this.color+"/"+x+"/"+y, true);
        let self = this;
        xhttp.onload = function() {
            self.loadMap();
            self.parentObject.meta?.loadMeta();
        }
        xhttp.send();
    }
    private rob(player: string): any {
        const xhttp = new XMLHttpRequest();
        xhttp.open("PUT", this.url+"move/rob_player/"+this.color+"/"+player, true);
        let self = this;
        xhttp.onload = function() {
            self.loadMap();
            self.parentObject.hud?.loadHud();
            self.parentObject.meta?.loadMeta();
        }
        xhttp.send();
    }
    private makeDeal(player: string): any{
        const xhttp = new XMLHttpRequest();
        xhttp.open("PUT", this.url+"move/fulfill_trade/"+this.color+"/"+player, true);
        let self = this;
        xhttp.onload = function() {
            self.loadMap();
            self.parentObject.hud?.loadHud();
            self.parentObject.meta?.loadMeta();
        }
        xhttp.send();
    }
    private cancelDeal(): any{
        const xhttp = new XMLHttpRequest();
        xhttp.open("PUT", this.url+"move/cancel_trade/"+this.color, true);
        let self = this;
        xhttp.onload = function() {
            self.loadMap();
            self.parentObject.hud?.loadHud();
            self.parentObject.meta?.loadMeta();
        }
        xhttp.send();
    }
    private foreignCornerClick(owner: string): any {
        if(this.parentObject.meta?.getStatus() == 7){
            // rob owner
            this.rob(owner)
        }
        if(this.parentObject.meta?.getStatus() == 8){
            // make deal
            this.makeDeal(owner)
        }
    }
    private ownCornerClick(): any {
        if(this.parentObject.meta?.getStatus() == 8){
            // cancel deal
            this.cancelDeal()
        }
    }
    private cornerClick(owner: string): any {
        if(owner != this.color){
            this.foreignCornerClick(owner)
        }
        else{
            this.ownCornerClick()
        }
    }
}