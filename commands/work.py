from nextcord import SelectOption, Interaction
from main import bot
from db_utils import get_equipmentdb, get_inventorydb, get_playerdb
from nextcord.ext import commands
from random import randint
from inventory import generate_item, get_items_by_owner
import nextcord
from bson.objectid import ObjectId


class WorkCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class ItemSelect(nextcord.ui.Select):
    def __init__(self, options, new_item):
        super().__init__(placeholder='Select your Secondary Weapon', min_values=1, max_values=1, options=options)
        self.new_item = new_item

    async def callback(self, interaction: nextcord.Interaction):
        selected_item_id = interaction.data['values'][0]
        get_inventorydb().delete_one({"_id": ObjectId(selected_item_id)})
        get_inventorydb().insert_one(self.new_item)
        await interaction.response.send_message("Item deleted and new item added.", ephemeral=True)


class ItemView(nextcord.ui.View):
    def __init__(self, items, new_item):
        super().__init__()
        options = [SelectOption(label=item['name'], value=str(item['_id'])) for item in items]
        self.add_item(ItemSelect(options, new_item))
        self.new_item = new_item


@bot.slash_command(name="work", description="Work to earn money and some xp")
async def work(interaction: Interaction):
    playerdb = get_playerdb()
    player = playerdb.find_one({"_id": interaction.user.id})
    randommoney = randint(1, 7)
    randomxp = randint(1, 10)
    if player is None:
        await interaction.response.send_message("Start your adventure first by doing /start", ephemeral=True)
    else:
        mana = player["mana"]
        if mana <= 10:
            await interaction.response.send_message("You don't have enough mana to work", ephemeral=True)
        else:
            playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"mana": -10}})
            await interaction.response.send_message(f"You worked and earned {randommoney} money and {randomxp} xp",
                                                    ephemeral=True)
            playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"money": randommoney, "xp": randomxp}})
            playerlevel = player["level"]
            playerxp = player["xp"]
            result = generate_item(interaction.user.id)
            if result["status"] == "success":
                new_item = result["item"]
                await interaction.followup.send(f"You found an item: {new_item['name']}!", ephemeral=True)
            elif result["status"] == "invfull":
                new_item = result["item"]
                same_type_items = [item for item in get_items_by_owner(interaction.user.id) if
                                   item['type'] == new_item['type']]
                await interaction.followup.send(
                    f"Your inventory is full!\nIf you want to keep the item : {new_item['name']} delete an item",
                    view=ItemView(same_type_items, new_item), ephemeral=True)
            else:
                pass
            if playerxp >= playerlevel * 105.3:
                playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"mana": 100}})
                playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"level": 1, "xp": -playerlevel * 100}})
                playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"speed": 0.1*playerlevel, "dexterity": 0.1*playerlevel, "intelligence": 0.1*playerlevel}})
                playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"health": 10, "strength": 3}})

                await interaction.followup.send("You leveled up!", ephemeral=True)


def setup(bot):
    bot.add_cog(WorkCommands(bot))
