#imports for basic bot functionality
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

#imports for basic dicebot funcitonality
import random
import math
from commands_dicebot import Dice, basicHelp, diceHelp
import re

PTU_Dice = Dice()

#imports for specific system functionality
from reference_tables_ptu import db_table, get_level, next_level, random_nature, random_type
from utilities_random_tables import weightedTable, load_files, buildTable
from utilities_text import pluralize, aAn
from settings import TRAINER_LEVEL_MULTIPLIER, UNDERLEVELED_POKEMON_ADJUSTMENT, REGION_NAME

pickup_table = load_files("databases/pickup")
biome_table = load_files("databases/biomes")
city_table = load_files("databases/cities")
area_table = load_files("databases/areas")
route_table = load_files("databases/routes")
fossil_table = buildTable("databases/fossils.csv")
metronome_table = buildTable("databases/metronome.csv")

ptuHelp = """
    `/skill` will roll a number of d6s, optionally with a bonus added on afterwards.
    `/attack` will roll a d20, minus an inputted AC.
    `/damage` will roll damage for an attack using a specified damage base.
    `/block` will calculate damage dealt, applying an inputted defense stat and optional damage reduction and type effectiveness. It can optionally also calculate remaining HP, given your current HP.
    `/scavenge`, alias `/pickup`, will roll one or more times on the Pickup table. If the Advantage option is used, it will not roll the same thing multiple times.
    `/encounter`, alias `/pokehunt` will roll one or more times in a given encounter table. Tables can be chosen from cities, routes, named areas, or biomes.
    `/fossil` will randomly identify a fossil from the fossil table.
    `/dowse` will automatically find use a dowsing rod.
    `/train` will calculate how much experience a pokemon has after one or more training sessions.
    `/metronome` will randomly select a move to use from Metronome (not yet implemented)
    `/nature` will randomly generate one of the 36 Natures.
    `/type` will randomly generate one of the 18 Types
    `/region`, alias `/version`, will report the name of the region that the bot is customized for."""

class PTU(commands.Cog):
    @commands.hybrid_command(description="Roll 1-6 d6s for a PTU skill roll, plus a bonus of 0-10.")
    @app_commands.describe(
        rank="The numerical rank of your skill, between 1 and 6.",
        bonus="The bonus to add to your roll, between 0 and 10. Defaults to 0.",
        label="The label to declare for this command.")
    async def skill(self, context, rank: int, bonus: int = 0, label: str = ""):
        report = ""
        if rank < 1 or rank > 6:
            report += "Rank must be within 1 and 6. Adjusting to within that range."
            rank = max(1, rank)
            rank = min(6, rank)
        if bonus < 0 or bonus > 10:
            report += "\nBonus must be within 0 and 10. Adjusting to within that range."
            bonus = max(0, bonus)
            bonus = min(10, bonus)
        if report:
            await context.send(report.strip())
        await PTU_Dice.dice(self, context, dice=rank, sides=6, bonus=bonus, label=label)

    @commands.hybrid_command(description="Roll 1d20 minus an inputted AC for a PTU attack roll")
    @app_commands.describe(
        ac="The Attack Check penalty applied to the roll. Is subtracted from your roll.",
        label="The label to declare for this command."
    )
    async def attack(self, context, ac: int, label: str = ""):
        await PTU_Dice.dice(self, context, bonus=(ac * -1), label=label)

    @commands.hybrid_command(description="Roll damage for an attack in PTU.")
    @app_commands.describe(
        db="The Damage Base of the attack.",
        bonus="Your Attack or Special Attack.",
        crit="True if you rolled a critical hit.",
        flat="Set as true to use the set damage for a given Damage Base, instead of rolling.",
        misc_bonus="Extra damage bonuses from abilities, items, etc. Accepts formats like '1d6+2', '1d10', or '5'.",
        label="The label to declare for this command."
    )
    async def damage(self, context, db: int, bonus: int, crit: bool = False, flat: bool = False, misc_bonus: str = "", label: str = ""):
        # Loads in the damage base information.
        report = ""
        if db < 1 or db > 24:
            report += "Damage Base must be within 1 and 24. Adjusting to within that range."
            db = max(1, db)
            db = min(24, db)

        damage_base = db_table[db]
        dice = damage_base['dice']
        sides = damage_base['sides']
        db_bonus = damage_base['bonus']
        db_flat = damage_base['set']

        if bonus < 0:
            report += "\nAttack and Special Attack cannot be negative. Adjusting to a bonus of 0."
            bonus = 0

        misc_total = 0
        misc_label = ""
        if misc_bonus:
            tokens = misc_bonus.replace(" ", "").split("+")
            valid = True
            for token in tokens:
                dice_match = re.fullmatch(r'(\d+)d(\d+)', token)
                if dice_match:
                    misc_dice = int(dice_match.group(1))
                    misc_sides = int(dice_match.group(2))
                    rolls = 0
                    for _ in range(misc_dice):
                        roll = random.randint(1, misc_sides)
                        rolls += roll
                    misc_total += rolls
                    misc_label += f"+{rolls}"
                elif token.isdigit():
                    misc_total += int(token)
                    misc_label += f"+{token}"
                else:
                    valid = False
                    break
            if not valid:
                misc_label = ""
                misc_total = 0
                report += "\nMisc bonus must be made up of 'XdY' and/or flat number terms separated by '+'. Ignoring misc bonus."

        if report:
            await context.send(report.strip())

        if crit:
            dice *= 2
            db_bonus *= 2
            db_flat *= 2

        printString = label

        if flat:
            printString += f"\nSet damage for DB {db}"
            if crit:
                printString += " as a critical hit"
            printString += f": {db_flat}"
            damage = db_flat
        else:
            printString += f"\nRolling {dice}d{sides}+{db_bonus}+{bonus}"
            if misc_label:
                printString += f"+{misc_bonus.replace(" ","")}"
            if crit:
                printString += " thanks to a critical hit!"
            damage = 0
            for i in range(dice):
                damage += random.randint(1, sides)
            printString += f"\nRolled {damage}+{db_bonus}"
            damage += db_bonus
        printString += f"+{bonus}{misc_label}"
        printString += f", for a total of **{damage + bonus + misc_total}!**"

        await context.send(printString.strip())

    @commands.hybrid_command(description="Calculate damage recieved from an attack in PTU.")
    @app_commands.describe(
        damage="The damage rolled from the attack by using the /damage command.", defense="Your Defense or Special Defense.",
        effectiveness="An effectiveness multiplier derived from typing, defaulting to 1. Input as a decimal number.",
        damage_reduction="Your Damage Reduction, if you have any. Defaults to 0",
        hp="Your current HP, to automatically calculate your remaining HP after applying the given damage",
        label="The label to declare for this command."
    )
    async def block(self, context, damage: int, defense: int, effectiveness: float = 1.0, damage_reduction: int = 0, hp: int = 0, label: str = ""):        
        if damage < 1:
            await context.send("This command should only be used for positive damage values.")
            return
        
        report = ""
        if defense < 0:
            report += "Defense cannot be a negative number. Setting defense to 0."
            defense = 0
        
        if effectiveness == 0:
            await context.send("You are immune to this damage!")
            return
        
        e_values = [0.125, 0.25, 0.5, 1, 1.5, 2, 3]
        if effectiveness not in e_values:
            report += "\nEffectiveness must be an exact value, from 1/8, 1/4, 1/2, 1, 1.5, 2, or 3. Rounding to the nearest of these values."
            effectiveness = min(e_values, key=lambda x: abs(x - effectiveness))
        
        if damage_reduction < 0:
            report += "\nDamage reduction cannot be a negative number. Setting DR to 0."
            damage_reduction = 0

        if report:
            await context.send(report.strip())

        result = max(1, damage - defense) #defense stats can't reduce below 1
        result = max(0, result - damage_reduction) #damage reduction CAN
        result = math.ceil(result * effectiveness) #always round up effectiveness

        printString = label

        match effectiveness:
            case 0.125:
                e_string = "ineffective damage"
            case 0.25:
                e_string = "barely effective damage"
            case 0.5:
                e_string = "not very effective damage"
            case 1.5:
                e_string = "super effective damage"
            case 2.0:
                e_string = "super-duper effective damage"
            case 3.0:
                e_string = "super-de-duper effective damage"
            case _:
                e_string = "damage"
        printString += f"\n{damage} {e_string}, reduced by a relevant defense of {defense}"
        if damage_reduction > 0:
            printString += f" and {damage_reduction} damage reduction"
        printString += f", becomes **{result} damage!**"

        if hp and hp > result:
            printString += f" Subtracted from your current HP of {hp}, you have {max(0, hp - result)} HP remaining."
        elif hp:
            printString += " You have been reduced to 0 HP and have fainted!"

        await context.send(printString.strip())

    @commands.hybrid_command(
        aliases=["scavenge"],
        description="Roll on PTU's Pickup Table."
    )
    @app_commands.describe(
        rolls="The number of times to roll on the scavenge table. Defaults to 1.",
        advantage="True if you cannot find the same items multiple times. Caps rolls at 10.",
        label="The label to declare for this command."
    )
    async def pickup(self, context, rolls: int = 1, advantage: bool = False, label: str = ""):
        if rolls > 10 and advantage:
            await context.send("When you have advantage, you can only roll up to 10 times at once. Setting rolls to 10.")
            rolls = 10
            
        foundItems = []
        while len(foundItems) < rolls:
            randRoll = random.randint(1, 20)
            match randRoll:
                case 1 | 2 | 3 | 4 | 5:
                    found = {"itemname": "None", "tableweight": 0, "sell price": "0"}
                    if not advantage or not (found in foundItems):
                        foundItems.append(found)
                case 6 | 7:
                    found = weightedTable(pickup_table['x_items'])
                    if not advantage or not (found in foundItems):
                        foundItems.append(found)
                case 8 | 9 | 10:
                    found = weightedTable(pickup_table['berries'])
                    if not advantage or not (found in foundItems):
                        foundItems.append(found)
                case 11 | 12 | 13:
                    found = weightedTable(pickup_table['pokeballs'])
                    if not advantage or not (found in foundItems):
                        foundItems.append(found)
                case 14 | 15 | 16:
                    found = weightedTable(pickup_table['healing_items'])
                    if not advantage or not (found in foundItems):
                        foundItems.append(found)
                case 17:
                    found = weightedTable(pickup_table['keepsakes'])
                    if not advantage or not (found in foundItems):
                        foundItems.append(found)
                case 18:
                    found = weightedTable(pickup_table['vitamins'])
                    if found['itemname'] == "Mint": 
                        found['itemname'] = f"{random_nature()} Mint"
                    if not advantage or not (found in foundItems):
                        foundItems.append(found)
                case 19:
                    found = weightedTable(pickup_table['held_items'])
                    if not advantage or not (found in foundItems):
                        foundItems.append(found)
                case 20:
                    found = weightedTable(pickup_table['tms'])
                    if not advantage or not (found in foundItems):
                        foundItems.append(found)

        printString = label

        foundDict = {}
        for item in foundItems:
            key = item['itemname']
            if key in foundDict:
                foundDict[key] = (foundDict[key][0] + 1, item)
            else:
                foundDict[key] = (1, item)

        for key in dict(sorted(foundDict.items())):
            item = foundDict[key][1]
            found = foundDict[key][0]
            if item['itemname'] != "None":
                if found > 1:
                    printString += f"\n{found} {pluralize(found,"time")}, you found {aAn(item['itemname'])}! The market will buy them for {item['sell price']} each!"
                else:
                    printString += f"\nFound {aAn(item['itemname'])}! The market will buy that for {item['sell price']}!"

        if "None" in foundDict:
            found = foundDict["None"][0]
            printString += f"{found} {pluralize(found,"time")}, you found nothing."

        if len(printString) > 2000:
            printString = "The final message was too long. Please try again, making fewer scavenge rolls at once."
        await context.send(printString.strip())

    @commands.hybrid_command(aliases=["pokehunt"], description="Roll for a random encounter, using weighted tables from `/databases/biomes` or `/databases/routes`.")
    @app_commands.choices(
        biome=[
            Choice(name="Abyssal Depths", value="depths"),
            Choice(name="Badlands", value="badlands"),
            Choice(name="Beach", value="beach"),
            Choice(name="Caves", value="caves"),
            Choice(name="City", value="city"),
            Choice(name="Crags", value="crags"),
            Choice(name="Desert", value="desert"),
            Choice(name="Forest", value="forest"),
            Choice(name="Glacier", value="glacier"),
            Choice(name="Grasslands", value="grassland"),
            Choice(name="Industrial", value="industrial"),
            Choice(name="Jungle", value="jungle"),
            Choice(name="Lake", value="lake"),
            Choice(name="Ocean", value="ocean"),
            Choice(name="Peaks", value="peaks"),
            Choice(name="Polar Sea", value="polar"),
            Choice(name="Ponds and Rivers", value="river"),
            Choice(name="Ruins", value="ruins"),
            Choice(name="The Safari Zone", value="safari"),
            Choice(name="Swamp", value="swamp"),
            Choice(name="Tundra", value="tundra"),
            Choice(name="Volcano", value="volcano"),
            Choice(name="Gift List (Off-Limits to Players)", value="gift")
        ],
        city=[
            Choice(name="Athens", value="athens"),
            Choice(name="Boread City", value="boread"),
            Choice(name="Cyclopton", value="cyclopton"),
            Choice(name="Dryad City", value="dryad"),
            Choice(name="Eidolon City", value="eidolon"),
            Choice(name="Harpyville", value="harpyville"),
            Choice(name="Hydra City", value="hydra"),
            Choice(name="Lamia Town", value="lamia"),
            Choice(name="Manticore Town", value="manticore"),
            Choice(name="Naiad Town", value="naiad"),
            Choice(name="Rhodes", value="rhodes"),
            Choice(name="Rome", value="rome"),
            Choice(name="Sparta", value="sparta"),
        ],
        area=[
            Choice(name="Mount Aetna", value="aetna"),
            Choice(name="The Aegis Peaks", value="aegis"),
            Choice(name="The Regi Mountains", value="regi"),
            Choice(name="The Spear Peaks", value="spear"),
            Choice(name="The August Swamp", value="august"),
            Choice(name="The Crimson Bog", value="crimson"),
            Choice(name="Golurk Bay", value="golurk"),
            Choice(name="Selene Lake", value="selene"),
            Choice(name="The Helios Desert", value="helios"),
            Choice(name="The Haunted Jungle", value="haunted"),
            Choice(name="The Sylvan Forest (North)", value="sylvanN"),
            Choice(name="The Sylvan Forest (South)", value="sylvanS"),
            Choice(name="Julius Isle (North)", value="juliusN"),
            Choice(name="Julius Isle (South)", value="juliusS"),
            Choice(name="The Isle of Tauros", value="tauros"),
        ]
    )
    @app_commands.describe(
        biome="A biome to search for a pokemon in. Mutually exclusive with route, city, and area.",
        city="A city to search for a pokemon in. Mutually exclusive with biome, route, and area.",
        area="An area to search for a pokemon in. Mutually exclusive with biome, city, and route.",
        route="A route to search for a pokemon in. Mutually exclusive with biome, city, and area.",
        level="Your trainer level, which determines the level of the pokemon you find.",
        rolls="The number of times to roll in the same route or biome. Defaults to 1.",
        advantage="True if you cannot find the same pokemon multiple times. Caps rolls at 10.",
        label="The label to declare for this command."
    )
    async def encounter(self, context, level: int, area: str = "", biome: str = "", city: str = "", route: int = 0, rolls: int = 1, advantage: bool = False, label: str = ""):
        checks = 0
        if area:
            checks += 1
            table = area_table[area]
        if biome:
            checks += 1
            table = biome_table[biome]
        if city:
            checks += 1
            table = city_table[city]
        if route:
            checks += 1
            route = f"r{route}"
            if not route in route_table:
                await context.send("Please select one of the region's routes.")
                return
            else:
                table = route_table[route]
        else:
            route = ""
        if checks == 0:
            await context.send("You must select a biome, city, route, or named area to search for pokemon in.")
            return
        elif checks > 1:
            await context.send("You may only select a single biome, city, route, or named area to search for pokemon in.")
            return
        
        level = max(5, int(level * TRAINER_LEVEL_MULTIPLIER))

        if rolls > 5 and advantage:
            await context.send("When you have advantage, you can only roll up to 5 times at once. Setting rolls to 5.")
            rolls = 5
        
        printString = label
        printString += f"\nRolling on the {area + biome + city + route} table..."
        
        found_list = []
        while len(found_list) < rolls:
            selection = weightedTable(table)
            if selection['pokemon'] in biome_table:
                printString += f"\n    Rolling on the {selection['pokemon']} subtable..."
                selection = weightedTable(biome_table[selection['pokemon']])
            if not advantage or not selection in found_list:
                found_list.append(selection)

        found_count = len(found_list)
        printString += "\nYou found"
        if found_count > 1:
            for i in range(len(found_list)):
                caught = found_list[i]
                if i+1 == found_count:
                    printString += " and"
                if level >= (int(caught['min_level']) - UNDERLEVELED_POKEMON_ADJUSTMENT):
                    printString += (f" {aAn(random_nature())} {caught['pokemon']}")
                else:
                    printString += (f" {aAn(random_nature())} {caught['prevolution']} (downgraded from {caught['pokemon']} due to level)")
                if i+1 != found_count:
                    printString += ","
                else:
                    printString += f"! All pokemon found are level {level}."
        else:
            caught = found_list[0]
            if level >= (int(caught['min_level']) - UNDERLEVELED_POKEMON_ADJUSTMENT):
                printString += (f" {aAn(random_nature())} {caught['pokemon']} at level {level}!")
            else:
                printString += (f" {aAn(random_nature())} {caught['prevolution']} (downgraded from {caught['pokemon']} due to level) at level {level}!")

        await context.send(printString)

    @commands.hybrid_command(description="Randomly identify a fossil in PTU, using a weighted table at `/databases.fossils.csv`.")
    @app_commands.describe(rolls="The number of times to roll on the fossil table.")
    @app_commands.describe(label="The label to declare for this command.")
    async def fossil(self, context, rolls: int = 1, advantage: bool = False, label: str = ""):
        printString = label
        
        printString += "Identified"
        for i in range(rolls):
            found = weightedTable(fossil_table)
            if i + 1 == rolls and rolls > 1:
                printString += " and"
            printString += f" {aAn(found['itemname'])}"
            if i + 1 != rolls and rolls > 1:
                printString += ","
            else:
                printString += "!"
            if rolls == 1:
                printString += f" That can be revived into {aAn(found['pokemon'])}!"

        await context.send(printString.strip())

    @commands.hybrid_command(description="Roll to dowse for shards in PTU, using standard Dowsing Rod rules.")
    @app_commands.describe(
        dice="The number of dice you roll when dowsing.",
        rolls="The number of dowsing attempts to make at once, to a max of 5",
        label="The label to declare for this command.")
    async def dowse(self, context, dice: int, rolls: int = 1, label: str = ""):
        if rolls > 5:
            rolls = 5
            await context.send("You may not make more than 5 dowsing rolls at once. Capping to 5 rolls.")
        if dice < 1:
            dice = 1
            await context.send("You may not roll less than 1d6 when dowsing. Setting dice to 1.")
        if dice > 15:
            dice = 15
            await context.send("You may not roll more than 15 dice at once when dowsing. Setting dice to 15.")

        printString = label

        for i in range(rolls):
            total = 0
            dice_rolled = 0
            explosions = 0
            red = 0
            orange = 0
            yellow = 0
            green = 0
            blue = 0
            violet = 0

            while dice_rolled < (dice + explosions):
                roll = random.randint(1, 6)
                dice_rolled += 1
                if roll >= 4:
                    total += 1
                    if roll == 6:
                        explosions += 1
                    colorRoll = random.randint(1, 6)
                    match colorRoll:
                        case 1:
                            red += 1
                        case 2:
                            orange += 1
                        case 3:
                            yellow += 1
                        case 4:
                            green += 1
                        case 5:
                            blue += 1
                        case 6:
                            violet += 1


            printString += f"\nRolled {dice}d6"
            if explosions:
                printString += f" and an extra {explosions}d6 thanks to exploding dice"
            printString += f", finding a total of **{total} shards.**"
            if red:
                printString += f"\n- {red} red {pluralize(red,"shard")}"
            if orange:
                printString += f"\n- {orange} orange {pluralize(orange,"shard")}"
            if yellow:
                printString += f"\n- {yellow} yellow {pluralize(yellow,"shard")}"
            if green:
                printString += f"\n- {green} green {pluralize(green,"shard")}"
            if blue:
                printString += f"\n- {blue} blue {pluralize(blue,"shard")}"
            if violet:
                printString += f"\n- {violet} violet {pluralize(violet,"shard")}"

        await context.send(printString.strip())
        return

    @commands.hybrid_command(description="Calculate how much experience a pokemon gains from one or more training session in PTU.")
    @app_commands.describe(
        exp="Your pokemon's starting experience value.",
        skill_rank="The rank of the skill you use to train pokemon - typically Command.",
        bonus="Any other bonuses you can add to training experience.",
        sessions="The number of training sessions to apply at once.",
        label="The label to declare for this command.")
    async def train(self, context, exp: int, skill_rank: int, bonus: int = 0, sessions: int = 1, label: str = ""):
        report = ""
        if exp < 0:
            exp = 0
            report += "A pokemon cannot have negative experience. Setting starting EXP to 0."
        match skill_rank:
            case 1 | 2:
                skill_bonus = 0
            case 3 | 4:
                skill_bonus = 5
            case 5 | 6:
                skill_bonus = 10
            case 8:
                skill_bonus = 15
            case _:
                await context.send("Your training skill rank must be a legal value (1-6, or 8).")
                return
        if bonus < 0:
            bonus = 0
            report += "\nYou cannot have a penalty to your training experience. Setting bonus to 0."
        
        if report:
            await context.send(report.strip())

        curr_xp = exp
        for i in range(sessions):
            curr_level = get_level(curr_xp)
            half_level = max(1,math.floor(curr_level / 2))
            curr_xp += half_level + skill_bonus + bonus

        curr_level = get_level(curr_xp)
        gained_xp = curr_xp - exp
        gained_levels = curr_level - get_level(exp)
        to_next_level = next_level(curr_xp)

        printString = label

        printString += f"Your pokemon gained {gained_xp} exp"
        if sessions > 1:
            printString += f" through {sessions} training sessions"
        printString += f", and now has **{curr_xp} exp.**"
        if gained_levels:
            printString += f" They gained {gained_levels} {pluralize(gained_levels, "level")}, and are now **level {curr_level}!**"
        if curr_level < 100:
            printString += f" They will reach level {curr_level + 1} after earning another {to_next_level} exp."
        
        await context.send(printString.strip())

    @commands.hybrid_command(description="Randomly select a move to use using Metronome, in PTU.")
    @app_commands.describe(label="The label to declare for this command.")
    async def metronome(self, context, label: str = ""):
        await context.send(f"Metronome is not yet implemented.")

    @commands.hybrid_command(description="Randomly generate one of the 36 natures in PTU.")
    async def nature(self, context):
        printString = f"Random nature: {random_nature()}"
        await context.send(printString)

    @commands.hybrid_command(description="Randomly generate one of the 18 types in PTU.")
    async def type(self, context):
        printString = f"Random type: {random_type()}"
        await context.send(printString)

    @commands.hybrid_command(description="Tells you the name of the region whos settings are being used.", aliases=["version"])
    async def region(self, context):
        printString = f"This iteration of the Important Grrl is generating from the {REGION_NAME} Region."
        await context.send(printString)

    @commands.hybrid_command(description="See a list of available commands for this bot.")
    async def help_important_grrl(self, context):
        printString = "The Important Grrl recognizes the following commands:"
        printString += f"\nBasic commands:{basicHelp}"
        printString += f"\nGeneric dice-rollowing commands:{diceHelp}"
        printString += f"\nPTU-specific commands:{ptuHelp}"
        await context.send(printString)

# The setup function is required to load the cog
async def setup(bot):
    await bot.add_cog(PTU(bot))