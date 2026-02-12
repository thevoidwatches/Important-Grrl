# The Important Grrl

A dice-rolling Discord bot designed for the fan-made [Pokemon Tabletop United](https://pokemontabletop.com/) ttrpg system.

To run your own copy of the Important Grrl, simply download the code, create a discord bot through the [discord developer portal](https://discord.com/developers/applications), then save the bot's token in a file called auth.txt in the same folder as the downloaded code. Opening run.bat will then boot up your own copy of the bot.

The `databases` folder contains csv files with data tables, which are randomly rolled from using the scavenge, dousing, encounter, and metronome commands. Be aware that the provided pickup, biome, city, area, and route tables are weighted to favor more common outcomes over rarer ones. In particular, note that the biome, city, area, and route tables are set for a limited subset of the pokedex, and for the creator's homebrew region. If you intend to use this bot's encounter command, it is *strongly* recommended that you run your own copy, and adjust these tables to your liking. Template files are provided within each folder, describing how to set up that folder's tables. To customize the pickup tables, do *not* add or remove tables, but you may add or remove entries from the tables, or change their tableweights and sell prices, to your liking.

Recognizes the following commands:
```
    /ping will simply respond with your ping to the bot.
    /kill will close the bot. The bot will attempt to restart every 60 seconds.
    /reset, alias /seed, will reset the bot's random number generator by choosing a new seed.
    /dice, alias /roll, allows you to roll any number of dice of any size, applying a bonus if you choose to and rolling the specified set of dice any number of times.
    /skill will roll a number of d6s, optionally with a bonus added on afterwards.
    /damage will roll damage for an attack using a specified damage base.
    /block will calculate damage dealt, applying an inputted defense stat and optional damage reduction and type effectiveness. It can optionally also calculate remaining HP, given your current HP.
    /scavenge, alias /pickup, will roll one or more times on the Pickup table. If the Advantage option is used, it will not roll the same thing multiple times.
    /encounter, alias /pokehunt will roll one or more times in a given encounter table. Tables can be chosen from cities, routes, named areas, or biomes.
    /fossil will randomly identify a fossil from the fossil table.
    /dowse will automatically find use a dowsing rod.
    /train will calculate how much experience a pokemon has after one or more training sessions.
    /metronome will randomly select a move to use from Metronome (not yet implemented)
    /nature will randomly generate a Nature.
```
