# About CardRPG

This is an unfinished and very rough prototype of a web-based multiplayer action roguelike. The primary differentiating game mechanic is that the actions available to the player are represented by a deck of cards. Whenever a player uses an action, the card is played and then discarded, and the player draws a new card randomly from their deck. The player can obtain new cards by performing chain kills on enemies. By killing multiple enemies in quick succession, the player can earn more coins which they can use to purchase new cards for their deck.

This game was in development from early 2016 to about mid 2017, at which point I abandoned several key conceits of the game (browser playability, the card deck based gameplay) in favor of a heavily tweaked concept, and started over in Unity.

# Requirements

* Some form of Python 2.7. I recommend pypy for its speed, which can be found [here](https://pypy.org/download.html).
* A modern browser (most of my testing was in Chrome, though I believe it works in Firefox)
* [Node.js + npm](https://nodejs.org/en/)

# Installation

* Navigate to the project directory and run `npm install` or `yarn install`
* Run `pypy -m pip install -r requirements.txt` or `pip install -r requirements.txt`
* Run `babel.bat` (or if running a non-Windows OS, `cat babel.bat` and run the command shown there). After compilation, press ctrl-BREAK to close the compiler.
* Run `webpack.bat` (or if running a non-Windows OS, `cat webpack.bat` and run the command shown there). After compilation, press ctrl-BREAK to close webpack.

# Running the Game

* Navigate to `/server` and run `pypy cardrpg.py` or `python cardrpg.py`
* Open a web browser and navigate to `127.0.0.1:8080`
* Enjoy!

# Playing the Game
* Move with WASD
* Press 1-6 to use abilities
* Try to get chains of monster kills!
* Buy new cards with the button in the bottom-right
* Unlock new cards as you kill monsters
* Cards cost accumulated chains once unlocked, and there are a limited number per stack

# Development

* Run the `babel.bat` and `webpack.bat` scripts and leave them running while developing.
.- babel.bat takes the code from `web_src` and compiles it from ES6 to ES5, then outputs it into `web_es5`
.- webpack.bat packs the code from `web_es5` into a single file for each page and outputs it into `web`

# Folder Structure
* /server - Python code for the backend
* /web_src - JavaScript ES6 source code
* /web_es5 - files compiled from web_src into ES5 are output here
* /web_es5/css - the CSS source for the project
* /web - the serveable web folder
* /web/assets/images - image sources for the project
* /web/assets/sounds - sound sources for the project

# Known Issues

* Performance may be an issue on slower computers or with standard Python. I had a fix in the works but can't remember if it's implemented yet.
* Several gameplay concepts are incomplete, particularly as regards "thinning" your deck at the end of a dungeon
* LAN play will usually work fine -- however, playing across the Internet will likely be an issue, as the data sent is not sufficiently optimized
* I was learning as I coded, so there's a lot of stuff that is not nearly as clean as I would like :)
* The icon images are just grabbed from Google Image searches and need to be replaced stat before doing much with this
* This entire thing needs unit tests like whoa
