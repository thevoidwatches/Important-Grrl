# City Table Guideline

Files should follow the following format, and *must* be saved as csv files.

```csv
pokemon,tableweight,min_level,prevolution
depths,1,0,n/a
Charmander,3,0,n/a
Charmeleon,2,15,Charmander
```

City tables can contin both biome tables and pokemon. Biomes *must* be labeled in the `pokemon` column using the exact name of the relevant biome table in the `../biomes` folder, without the `.csv` prefix, and the `min_level` and `prevolution` columns have no bearing on them. If a biome is rolled, the biome table will have a pokemon pulled from it.

When a pokemon is rolled, the `min_level` column is used to determine if the trainer is high enough level to catch it, based on the trainer level multiplier variable and underleveled pokemon adjustment variable found in in `../../settings.py`. If the inputted trainer level times this multiplier matches or exceeds the value in `min_level` minus the underleveled adjustment, the pokemon can be caught - otherwise, it will be downgraded into the pokemon listed in the `prevolution` column.

The `tableweight` column determines how many chances there are to draw that specific entry. In the above example, there is a 1/6 chance of drawing the depths biome and selecting a pokemon from it according to its own weights; a 3/6 (or 1/2) chance of drawing a Charmander; and a 2/6 (1/3) chance of drawing a Charmeleon and checking the inputted trainer level to see if the trainer catches a Charmeleon or a Charmander.

The creator recommends that city tables consist of 3 biomes with different weights, and 1 unique pokemon line found in that city.

**Note that when constructing your own city tables, you *must* edit lines 270-282 of the `commands_ptu.py` file in the top-level folder.** Each `Choice()` in these lines should correspond to one of the .csv files in this folder, with `name` being what players will see when using the command and `value` being the name of the file, without the `.csv` prefix.

Additionally, please note that due to limitations inherent in Discord's slash commands, you may only have a maximum of 25 cities.