from nextcord import Interaction
from main import bot
from db_utils import get_equipmentdb, get_inventorydb, get_playerdb
from nextcord.ext import commands


class StartCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


@bot.slash_command(name="start", description="Start Your adventure")
async def start(interaction: Interaction):
    playerdb = get_playerdb()
    player = playerdb.find_one({"_id": interaction.user.id})
    if player is None:
        playerdb.insert_one(
            {
                "_id": interaction.user.id
                , "name": interaction.user.name
                , "money": 0
                , "level": 1
                , "xp": 0
                , "mana": 100
                , "health": 100
                , "strength": 1
                , "dexterity": 1
                , "intelligence": 1
                , "speed": 1
             }
        )
        await interaction.response.send_message("You started your adventure!", ephemeral=True)
    else:
        await interaction.response.send_message("You already started your adventure!", ephemeral=True)


def setup(bot):
    bot.add_cog(StartCommands(bot))
