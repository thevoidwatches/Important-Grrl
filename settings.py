# When using the /encounter command, your inputted trainer level is multiplied by this to determine the level of the pokemon you find.
# If using the 1-50 trainer levels found in the RAW, this should be either 1 or 1.5 depending on if you want to catch pokemon half the level of your party average, or 3/4 that level.
# If using the 1-25 trainer level homebrew, this should be either 2 or 3.
TRAINER_LEVEL_MULTIPLIER = 2

# When using the /encounter command, second-stage pokemon can be found. Their minimum level to evolve to that pokemon will have this number subtracted from it prior to being compared to the level that the pokemon is being caught at, before determining if they should be downgraded or not.
# Essentially, you may catch or generate wild pokemon who have evolved early, by up to this number of levels.
UNDERLEVELED_POKEMON_ADJUSTMENT = 5

# Name this variable the same thing as your custom region.
REGION_NAME = "Olympia"