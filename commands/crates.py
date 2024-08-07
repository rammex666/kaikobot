import random
from boxs import get_box
import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from main import bot
from db_utils import get_playerdb

from inventory import add_item_to_inventory


class CrateCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.slash_command(name="open_crate", description="Open a crate to get a random item")
    async def open_crate(self, interaction: Interaction):
        embed = nextcord.Embed(title="Choose a Box", description="Select the type of box you want to open.")
        options = [nextcord.SelectOption(label=box, description=f"Cost: {get_box()[box]['cost']} money") for box in
                   get_box()]
        select = nextcord.ui.Select(placeholder="Select a box", options=options)
        view = nextcord.ui.View()
        view.add_item(select)

        async def select_callback(interaction: nextcord.Interaction):
            selected_box = select.values[0]
            await self.handle_box_selection(interaction, selected_box)

        select.callback = select_callback
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def handle_box_selection(self, interaction: nextcord.Interaction, selected_box: str):
        playerdb = get_playerdb()
        player = playerdb.find_one({"_id": interaction.user.id})
        box = get_box()[selected_box]

        if player["money"] < box["cost"]:
            await interaction.response.send_message("You don't have enough money to open this box.", ephemeral=True)
            return

        playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"money": -box["cost"]}})

        item = random.choice(box["items"])
        add_item_to_inventory(interaction.user.id, **item)

        await interaction.followup.send(f"Congratulations! You obtained: {item['name']}")


def setup(bot):
    bot.add_cog(CrateCommands(bot))
