from nextcord import SelectOption, Interaction
from bson.objectid import ObjectId
from inventory import get_items_by_owner
from main import bot
from db_utils import get_inventorydb, get_playerdb, get_shopdb, get_equipmentdb
from nextcord.ext import commands
import nextcord

ALLOWED_IDS = [926163972397355049]


class ShopCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.item_prices = {
            "Common Helmet": 10,
            "Common Sword": 10,
            "Common Shield": 10,
            "Common Chestplate": 10,
            "Common Boots": 10,
            "Uncommon Helmet": 20,
            "Uncommon Sword": 20,
            "Uncommon Shield": 20,
            "Uncommon Chestplate": 20,
            "Uncommon Boots": 20,
            "gold": 10,
            "Rock": 5,
            "Wood": 5,
        }

    def get_item_price(self, item_name):
        return self.item_prices.get(item_name, 0)

    @bot.slash_command(name="set_shop", description="Set the shop items")
    async def set_shop(self, interaction: nextcord.Interaction, name: str, price: int, quality: str, rarity: str,
                       type: str, damage: int, durability: int, description: str, quantity: int, level: int, xp: int):
        if interaction.user.id not in ALLOWED_IDS:
            await interaction.response.send_message("You are not allowed to execute this command.", ephemeral=True)
            return
        get_shopdb().insert_one({
            "name": name,
            "price": price,
            "quality": quality,
            "rarity": rarity,
            "type": type,
            "damage": damage,
            "durability": durability,
            "description": description,
            "quantity": quantity,
            "level": level,
            "xp": xp,
            "nombre_de_vente": 0
        })
        await interaction.response.send_message("Shop item set successfully.", ephemeral=True)


def add_item_to_inventory(owner_id, **new_item):
    inventorydb = get_inventorydb()
    new_item["_id"] = ObjectId()
    new_item["owner_id"] = owner_id
    inventorydb.insert_one(new_item)


class BuyItemSelect(nextcord.ui.Select):
    def __init__(self, items, shop_commands):
        options = [SelectOption(label=item['name'], value=str(item['_id'])) for item in items]
        super().__init__(placeholder='Select an item to buy', min_values=1, max_values=1, options=options)
        self.items = items
        self.shop_commands = shop_commands

    async def callback(self, interaction: nextcord.Interaction):
        selected_item_id = self.values[0]
        selected_item = next((item for item in self.items if str(item['_id']) == selected_item_id), None)
        if selected_item:
            player = get_playerdb().find_one({"_id": interaction.user.id})
            if player['money'] < selected_item['price']:
                await interaction.response.send_message("You don't have enough money to buy this item.", ephemeral=True)
            else:
                get_playerdb().update_one({"_id": interaction.user.id}, {"$inc": {"money": -selected_item['price']}})
                add_item_to_inventory(interaction.user.id, **selected_item)
                get_shopdb().update_one({"_id": ObjectId(selected_item_id)}, {"$inc": {"nombre_de_vente": 1}})
                await interaction.response.send_message(
                    f"You bought {selected_item['name']} for {selected_item['price']} money.",
                    ephemeral=True)


class SellSelect(nextcord.ui.Select):
    def __init__(self, items, shop_commands):
        if not items:
            raise ValueError("No items to sell.")
        if len(items) > 25:
            items = items[:25]
        options = [SelectOption(label=item['name'], value=str(item['_id'])) for item in items]
        super().__init__(placeholder='Select an item to sell', min_values=1, max_values=1, options=options)
        self.items = items
        self.shop_commands = shop_commands

    async def callback(self, interaction: nextcord.Interaction):
        selected_item_id = self.values[0]
        selected_item = next((item for item in self.items if str(item['_id']) == selected_item_id), None)
        self.view.stop()
        if selected_item:
            player_equipment = get_equipmentdb().find_one({"_id": interaction.user.id})
            if player_equipment and any(equipment_id == selected_item_id for equipment_id in player_equipment.values()):
                for equipment_type, equipment_id in player_equipment.items():
                    if equipment_id == selected_item_id:
                        get_equipmentdb().update_one({"_id": interaction.user.id}, {"$unset": {equipment_type: ""}})
                        await interaction.response.send_message(f"You sold {selected_item['name']} for {item_price} money.", ephemeral=True)
            get_inventorydb().delete_one({"_id": ObjectId(selected_item_id)})
            item_price = self.shop_commands.get_item_price(selected_item['name'])
            get_playerdb().update_one({"_id": interaction.user.id}, {"$inc": {"money": item_price}})
            await interaction.response.send_message(f"You sold {selected_item['name']} for {item_price} money.",
                                                     ephemeral=True)

class PaginationButton(nextcord.ui.Button):
    def __init__(self, label, items, page_number, shop_commands):
        super().__init__(style=nextcord.ButtonStyle.secondary, label=label)
        self.items = items
        self.page_number = page_number
        self.shop_commands = shop_commands

    async def callback(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Your inventory")
        for item in self.items[self.page_number * 10:(self.page_number + 1) * 10]:
            item_price = self.shop_commands.get_item_price(item['name'])
            embed.add_field(name=f"{item['name']} - Price: {item_price}",
                            value=f"Quantity: {item['quantity']}\nQuality: {item['quality']}\nLevel: {item['level']}\nXP: {item['xp']}",
                            inline=True)
        await interaction.response.edit_message(embed=embed,
                                                view=SellView(self.items, self.page_number, self.shop_commands))


class SellView(nextcord.ui.View):
    def __init__(self, items, page_number, shop_commands):
        super().__init__()
        self.add_item(SellSelect(items[page_number * 10:(page_number + 1) * 10], shop_commands))
        if page_number > 0:
            self.add_item(PaginationButton("Previous", items, page_number - 1, shop_commands))
        if len(items) > (page_number + 1) * 10:
            self.add_item(PaginationButton("Next", items, page_number + 1, shop_commands))


class ShopSelect(nextcord.ui.Select):
    def __init__(self, shop_commands):
        options = [
            SelectOption(label="Buy", value="buy"),
            SelectOption(label="Sell", value="sell")
        ]
        super().__init__(placeholder='Select an action', min_values=1, max_values=1, options=options)
        self.shop_commands = shop_commands

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        if value == "buy":
            items = list(get_shopdb().find({}))
            embed = nextcord.Embed(title="Shop items")
            for item in items:
                embed.add_field(name=f"{item['name']} - Price: {item['price']}", value=f"{item['description']}"
                                                                                       f"\n__Damage__ : **{item['damage']}**"
                                                                                       f"\n__Durability__ : **{item['durability']}**"
                                                                                       f"\n__Level__ : **{item['level']}**"
                                                                                       f"\n__Rarity__ : **{item['rarity']}**"
                                                                                       f"\n__Quality__ : **{item['quality']}**"
                                                                                       f"\n__Quantity__ : **{item['quantity']}**"
                                                                                       f"\nBuy this item", inline=True)
            view = nextcord.ui.View()
            view.add_item(BuyItemSelect(items, self.shop_commands))
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        elif value == "sell":
            items = get_items_by_owner(interaction.user.id)
            await interaction.response.edit_message(view=SellView(items, 0, self.shop_commands))


class ShopView(nextcord.ui.View):
    def __init__(self, shop_commands):
        super().__init__()
        self.add_item(ShopSelect(shop_commands))


@bot.slash_command(name="shop", description="Buy or sell items")
async def shop(interaction: Interaction):
    shop_commands = ShopCommands(bot)
    await interaction.response.send_message("Welcome to the shop!", view=ShopView(shop_commands), ephemeral=True)


def setup(bot):
    bot.add_cog(ShopCommands(bot))
