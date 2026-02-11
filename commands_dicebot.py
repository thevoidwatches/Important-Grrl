#imports for basic bot functionality
from discord import app_commands
from discord.ext import commands

#imports for basic dicebot funcitonality
import random
import math
import re
from utilities_text import pluralize, aAn

random.seed()

basicHelp = """
    `/ping` will simply respond with your ping to the bot.
    `/kill` will close the bot. The bot will attempt to restart every 60 seconds."""

#Utility cogs that can be the same across multiple bots
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def ping(self, context):
        await context.send(f'Pong!\nLatency: {round(self.bot.latency * 1000)}ms')

    @commands.command(alias="close")
    async def kill(self, context):
      await context.send("`Closing the Important Grrl. The grrl will attempt to restart in one minute.`")
      quit()

diceHelp = """
    `/reset`, alias `/seed`, will reset the bot's random number generator by choosing a new seed.
    `/dice`, alias `/roll`, allows you to roll any number of dice of any size, applying a bonus if you choose to and rolling the specified set of dice any number of times."""

class Dice(commands.Cog):
    @commands.hybrid_command(aliases=["seed"])
    async def reset(self, context):
      random.seed()
      await context.send("I've reset my random number generator.")

    @commands.hybrid_command(aliases=["roll"], description="Roll a specified number of dice. Rolls 1d20 by default.")
    @app_commands.describe(dice="The number of dice in a single roll - the X in 'roll XdY+Z A times'")
    @app_commands.describe(sides="The number of sides on each die in a single roll - the Y in 'roll XdY+Z A times'")
    @app_commands.describe(bonus="The bonus to add to a single roll - the Z in 'roll XdY+Z A times'")
    @app_commands.describe(rolls="The number of separate rolls to make - the A in 'roll XdY+Z A times'")
    @app_commands.describe(rolls="Any roll of this number of above will add to the number of dice being rolled")
    @app_commands.describe(label="The label to declare for this command.")
    async def dice(self, context, dice: int = 1, sides: int = 20, bonus: int = 0, rolls: int = 1, explode: int = 0, label: str = ""):
        # sets values to a minimum to avoid negative inputs where it doesn't make sense
        dice = max(1, dice)
        sides = max(2, sides)
        rolls = max(1, rolls)
        if explode == 1:
            explode = 0
            await context.send("Exploding dice cannot be set to explode on rolls of 1 and up. Turning exploding dice off.")

        # sets whether or not to add a plus sign when appending the bonus
        if bonus > 0:
            bonusPrint = f"+{bonus}"
        elif bonus == 0:
            bonusPrint = ""
        else:
            bonusPrint = str(bonus)

        printString = label

        printString = f"\nRolling {dice}d{sides}{bonusPrint}"
        if rolls > 1:
            printString += f", {rolls} times"
        if explode > 0:
            printString += ", with exploding dice"
            if explode < sides:
                printString += f" on rolls of {explode} and up"

        # rolls once per roll
        for i in range(rolls):

            # sets up indents if there are multiple distinct rolls being made
            indent = ""
            if rolls > 1:
                printString += f"\nRoll {i+1} of {rolls}..."
                indent = "    "

            # rolls dice and reports their results
            if (dice + explode) > 1:
                total = 0
                rolled = 0
                exploded = 0
                while rolled < dice + exploded:
                    result = random.randint(1, sides)
                    total += result
                    rolled += 1

                    # sets up a highlight for each max roll
                    maxRoll = ""
                    if result == sides:
                        maxRoll = "**"
                    printString += f"\n{indent}Rolled {maxRoll}{result}{maxRoll} on a d{sides}!"

                    # explosion code:
                    if explode > 0 and result >= explode:
                        exploded += 1
                        printString += " You get to roll an extra die!"
                printString += f"\n{indent}The final total is **{total+bonus}!**"
                if exploded > 0:
                    printString += f" Your dice exploded {exploded} {pluralize(exploded,"time")}!"
                elif explode > 0:
                    printString += " Your dice did not explode."
            else:
                result = random.randint(1, sides)
                # sets up a highlight for a max roll
                maxRoll = ""
                if result == sides:
                    maxRoll = "**"
                if bonus:
                    printString += f"\n{indent}Rolled {maxRoll}{result}{maxRoll}{bonusPrint}, for a total of **{result+bonus}!**"
                else:
                    printString += f"\n{indent}Rolled **{result}!**"
            
        # If the string is too long for a single Discord message, ask the player to roll fewer dice.
        if len(printString) > 2000:
            printLines = printString.splitlines()
            printString = ""
            linesSkipped = 0
            for line in printLines:
                if line.startswith("Rolled ") or line.startswith("    Rolled "):
                    linesSkipped += 1
                else:
                    if linesSkipped:
                        printString += f"\nTrimming {pluralize(linesSkipped), "line"} to conserve message length..."
                        linesSkipped = 0
                    printString += f"\n{line}"
        if len(printString) > 2000:
            printString = "The final message was too long, even after trimming. Please try again, rolling fewer dice at once."
        await context.send(printString.strip())

# The setup function is required to load the cog
async def setup(bot):
    await bot.add_cog(Utility(bot))
    await bot.add_cog(Dice(bot))