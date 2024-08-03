from nextcord.ext import tasks, commands
from db_utils import get_playerdb
import nextcord
import os
from main import bot


class OnReadyEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.give_mana.start()

    @tasks.loop(minutes=10.0)
    async def give_mana(self):
        playerdb = get_playerdb()
        players = playerdb.find({})
        for player in players:
            if player["mana"] < 500:
                playerdb.update_one({"_id": player["_id"]}, {"$inc": {"mana": 10}})

    @commands.Cog.listener()
    async def on_ready(self):
        print("Kaiko v1.0 is ready!")
        print("By .rammex")
        await bot.change_presence(activity=nextcord.Game("Kaiko v1.0"))
        for folder in ['commands', 'events']:
            for filename in os.listdir(folder):
                if filename.endswith('.py'):
                    print(f"Loaded {filename}")

    @give_mana.before_loop
    async def before_give_mana(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(OnReadyEvent(bot))
