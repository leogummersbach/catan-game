# Catan Game

## About

First of all, I do not own the rights of the original Catan Board Game. Please visit their [official web page](https://www.catan.com/).
This is an example of a cient-server architecture for playing the catan board game.

## Run

To run, simply run the scripts `StartCGameApi.bat` and `StartCGameLocal.bat`. Then, type `http://localhost:1234/?color=yellow` in your browser to play as color yellow.

## Frontend

The frontend works with `pixi.js` and can be found in `cgame/game`. It reads data from an API, which is the backend. 
Then, the data gets displayed nice. The upper-left corner tells you what to do. To start the frontend locally, simply run the script `StartCGameLocal.bat`.
Then, hit the displayed link and specify the color you want to play with in the url (for example, if you want to play with color yellow, type `http://localhost:1234/?color=yellow`). 
All graphics are created by myself.

## Backend

The backend works with Fast-API and a strong object-oriented implementation of the boardgame.
It can be found in `cgame_backend` and can be run with via the script `StartCGameApi.bat`.
The backend currently runs exactly one game with ID `0`. You can edit the players and if they are bots or not in the `main.py` file at the very end. 
Note than bots do not work completely, they just skip and deny everythink at the time. Sometimes, you need to act for them manually by accessing their game via their URL.
You can have an insight on the API's data by accessing the following URLs:
* `http://localhost:8000/cgameapi/games/0/meta`
* `http://localhost:8000/cgameapi/games/0/hud`
* `http://localhost:8000/cgameapi/games/0/map`


