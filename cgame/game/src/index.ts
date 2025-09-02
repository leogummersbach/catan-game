import { Cgame } from './cgame'
import { Map } from './map';
import { Hud } from './hud';
import { Meta } from './meta';



const params = new URLSearchParams(window.location.search)

let color = "undefined"
if(params.has("color")){
    color = params.get("color") as string
}

let url = "http://localhost:8000/cgameapi/games/0/"
let base_url = "http://localhost:8000/cgameapi/"
//let url = "http://dyndns.leoseite.de/cgameapi/"
let items = ["wood", "clay", "sheep", "wheat", "ore"];


const app = new Cgame({
    view: document.getElementById("pixi-canvas") as HTMLCanvasElement,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
    backgroundColor: 0x6495ed,
    width: 1920,
    height: 1080,
    resizeTo: window
}, color, url);


const map: Map = new Map(app, app.screen.width, 0.8*app.screen.height, 80, url, base_url, color);
const hud: Hud = new Hud(app, app.screen.width, 0.2*app.screen.height, 0.8*app.screen.height, color, 100, url, base_url);
const meta: Meta = new Meta(app, app.screen.width*0.1, app.screen.height, 100, url, base_url, items, color);

app.setMap(map);
app.setHud(hud);
app.setMeta(meta);


app.stage.addChild(map)
app.stage.addChild(meta)
app.stage.addChild(hud)


