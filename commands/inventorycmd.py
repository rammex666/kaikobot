from nextcord import Interaction
from main import bot
from db_utils import get_equipmentdb, get_inventorydb, get_playerdb
from nextcord.ext import commands
from inventory import get_items_by_owner
import nextcord
from nextcord.ui import View, button
from nextcord import ButtonStyle, Interaction

class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class PaginationView(View):
    def __init__(self, embeds):
        super().__init__()
        self.embeds = embeds
        self.current_page = 0

    @button(label="Précédent", style=ButtonStyle.primary)
    async def previous_button(self, button, interaction: Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page])

    @button(label="Suivant", style=ButtonStyle.primary)
    async def next_button(self, button, interaction: Interaction):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page])

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
            embeds = []
            items_per_page = 10
            for i in range(0, len(items), items_per_page):
                embed = nextcord.Embed(
                    title=" ",
                    color=nextcord.Color.random()
                )
                for item in items[i:i+items_per_page]:
                    embed.add_field(name=f"Item: {item['name']}", value=f"Quantity: {item['quantity']}\nQuality: {item['quality']}\nLevel: {item['level']}\nXP: {item['xp']}", inline=True)
                embed.set_footer(text=f"Kaiko v1.0 | Page {i//items_per_page + 1} de {len(items)//items_per_page + 1}")
                embed.set_author(name=f"{interaction.user.name}'s inventory", icon_url=interaction.user.avatar.url)
                embeds.append(embed)
            view = PaginationView(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(InventoryCommands(bot))
