import { Application, IApplicationOptions} from 'pixi.js'
import { Map } from './map';
import { Hud } from './hud';
import { Meta } from './meta';
import { Window } from './window';

export class Cgame extends Application {
    public color: string;
    public url: string;
    public map: Map | undefined;
    public hud: Hud | undefined;
    public meta: Meta | undefined;
    public window: Window | undefined;
    constructor(metadata: object, color: string, url: string){
        super(metadata as IApplicationOptions)
        this.color = color;
        this.url = url;

        this.map = undefined;
        this.hud = undefined;
        this.meta = undefined;
        this.window = undefined;
    }

    public reload(){
        if(this.map != undefined){
            this.map.loadMap()
        }
        if(this.hud != undefined){
            this.hud.loadHud()
        }
        if(this.meta != undefined){
            this.meta.loadMeta()
        }
    }

    public setMap(map: Map){
        this.map = map;
    }
    public setHud(hud: Hud){
        this.hud = hud;
    }
    public setMeta(meta: Meta){
        this.meta = meta;
    }
    public setWindow(window: Window){
        this.window = window;
    }
    public removeWindow(){
        this.window = undefined;
    }
}