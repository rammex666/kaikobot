from nextcord import Interaction
from main import bot
from db_utils import get_equipmentdb, get_inventorydb, get_playerdb
from nextcord.ext import commands
from inventory import get_items_by_owner
import nextcord


class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


@bot.slash_command(name="inventory", description="Look at your inventory")
async def inventory(interaction: Interaction):
    playerdb = get_playerdb()
    player = playerdb.find_one({"_id": interaction.user.id})
    if player is None:
        await interaction.response.send_message("You have to start your adventure first", ephemeral=True)
    else:
        items = get_items_by_owner(interaction.user.id)
        if not items:
            await interaction.response.send_message("You don't have any items in your inventory", ephemeral=True)
        else:
            description = ""
            for item in items:
                description += f"Item: {item['name']}\nQuantity: {item['quantity']}\nQuality: {item['quality']}\nLevel: {item['level']}\nXP: {item['xp']}\n\n"
            embed = nextcord.Embed(
                title=" ",
                description=description,
                color=nextcord.Color.random()
            )
            embed.set_footer(text="Kaiko v1.0")
            embed.set_author(name=f"{interaction.user.name}'s inventory", icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(InventoryCommands(bot))
