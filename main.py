import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


def load_cogs(bot):
    for folder in ['commands', 'events']:
        for filename in os.listdir(folder):
            if filename.endswith('.py'):
                bot.load_extension(f'{folder}.{filename[:-3]}')


load_cogs(bot)
bot.run(BOT_TOKEN)
