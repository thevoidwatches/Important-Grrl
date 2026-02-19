import discord
from discord.ext import commands

#connection to discord
intents = discord.Intents.default()
intents.message_content = True
#to use regular commands still, use a command_prefix
bot = commands.Bot(command_prefix='', intents=intents)

#load cogs for commands/slash commands
@bot.event
async def on_ready():
    await bot.load_extension('commands_dicebot')
    await bot.load_extension('commands_ptu')
    print('All cogs loaded.')
    try:
        await bot.tree.sync() # Sync slash commands to Discord
        print('All commands synced.')
    except Exception as e:
        print(f"An error occured while syncing commands:\n{e}")
    print('The Important Grrl is now running.'.format(bot))

#ensures that the bot doesn't respond to non-slash messages
@bot.event
async def on_message(message):
    pass

token = open('auth.txt').read()
bot.run(token, reconnect = True)
