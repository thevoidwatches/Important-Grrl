# City Table Guideline

Files should follow the following format, and *must* be saved as csv files.

```csv
pokemon,tableweight,min_level,prevolution
Charmander,3,0,n/a
Charmeleon,2,15,Charmander
```

Biome tables may only contain pokemon.

When a pokemon is rolled, the `min_level` column is used to determine if the trainer is high enough level to catch it, based on the trainer level multiplier variable and underleveled pokemon adjustment variable found in in `../../settings.py`. If the inputted trainer level times this multiplier matches or exceeds the value in `min_level` minus the underleveled adjustment, the pokemon can be caught - otherwise, it will be downgraded into the pokemon listed in the `prevolution` column.

The `tableweight` column determines how many chances there are to draw that specific entry. In the above example, there is a 1/6 chance of drawing the depths biome and selecting a pokemon from it according to its own weights; a 3/6 (or 1/2) chance of drawing a Charmander; and a 2/6 (1/3) chance of drawing a Charmeleon and checking the inputted trainer level to see if the trainer catches a Charmeleon or a Charmander.

The number of pokemon available in a biome is your own personal preference, but the creator recommends between 20 and 30, with weights varying between 1 and 4.

**Note that when constructing your own biome tables, you *must* edit lines 252-274 of the `commands_ptu.py` file in the top-level folder.** Each `Choice()` in these lines should correspond to one of the .csv files in this folder, with `name` being what players will see when using the command and `value` being the name of the file, without the `.csv` prefix.

Additionally, please note that due to limitations inherent in Discord's slash commands, you may only have a maximum of 25 biomes.

The example biomes in this folder are constructed such that every non-legendary pokemon is available in the habitats listed in their PTU pokedex entry. First evolutions are given higher weights than second evolutions, and final evolutions are given a weight of 0. Each pokemon line has the same total weight as every other line in that biome.