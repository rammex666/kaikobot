from nextcord import Interaction
from main import bot
from db_utils import get_equipmentdb, get_inventorydb, get_playerdb
from nextcord.ext import commands
import nextcord
from bson.objectid import ObjectId


class EquipmentCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class HelmetSelect(nextcord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder='Select your Helmet', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        helmet_id = self.values[0]
        helmet = get_helmet_name_by_id(helmet_id)
        if helmet is not None and isinstance(helmet, dict):
            helmet_name = helmet['name']
            await interaction.response.send_message(f'You selected {helmet_name}')
            equipmentdb = get_equipmentdb()
            equipmentdb.update_one({"_id": interaction.user.id}, {"$set": {"helmetid": helmet_id}}, upsert=True)
            equipmentdb.update_one({"_id": interaction.user.id}, {"$set": {"helmetname": helmet_name}}, upsert=True)
        else:
            await interaction.response.send_message('Helmet not found in the inventory.')


def get_helmet_name_by_id(helmet_id):
    inventorydb = get_inventorydb()
    helmet = inventorydb.find_one({"_id": ObjectId(helmet_id)})
    return helmet




class ChestSelect(nextcord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder='Select your ChestPlate', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        chest_id = self.values[0]
        chest = get_chest_name_by_id(chest_id)
        if chest is not None and isinstance(chest, dict):
            chest_name = chest['name']
            await interaction.response.send_message(f'You selected {chest_name}')
            equipmentdb = get_equipmentdb()
            equipmentdb.update_one({"_id": interaction.user.id}, {"$set": {"chestid": chest_id}}, upsert=True)
            equipmentdb.update_one({"_id": interaction.user.id}, {"$set": {"chestname": chest_name}}, upsert=True)
        else:
            await interaction.response.send_message('chest not found in the inventory.')


def get_chest_name_by_id(helmet_id):
    inventorydb = get_inventorydb()
    chest = inventorydb.find_one({"_id": ObjectId(helmet_id)})
    return chest




class BootsSelect(nextcord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder='Select your Boots', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        boots_id = self.values[0]
        boots = get_boots_name_by_id(boots_id)
        if boots is not None and isinstance(boots, dict):
            boots_name = boots['name']
            await interaction.response.send_message(f'You selected {boots_name}')
            equipmentdb = get_equipmentdb()
            equipmentdb.update_one({"_id": interaction.user.id}, {"$set": {"bootsid": boots_id}}, upsert=True)
            equipmentdb.update_one({"_id": interaction.user.id}, {"$set": {"bootsname": boots_name}}, upsert=True)
        else:
            await interaction.response.send_message('Boots not found in the inventory.')


def get_boots_name_by_id(boots_id):
    inventorydb = get_inventorydb()
    boots = inventorydb.find_one({"_id": ObjectId(boots_id)})
    return boots




class PrimarySelect(nextcord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder='Select your Primary Weapon', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        primary_id = self.values[0]
        primary = get_primary_name_by_id(primary_id)
        if primary is not None and isinstance(primary, dict):
            primary_name = primary['name']
            await interaction.response.send_message(f'You selected {primary_name}')
            equipmentdb = get_equipmentdb()
            equipmentdb.update_one({"_id": interaction.user.id}, {"$set": {"primaryid": primary_id}}, upsert=True)
            equipmentdb.update_one({"_id": interaction.user.id}, {"$set": {"primaryname": primary_name}}, upsert=True)
        else:
            await interaction.response.send_message('Primary weapon not found in the inventory.')


class SecondarySelect(nextcord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder='Select your Secondary Weapon', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        secondary_id = self.values[0]
        secondary = get_secondary_name_by_id(secondary_id)
        if secondary is not None and isinstance(secondary, dict):
            secondary_name = secondary['name']
            await interaction.response.send_message(f'You selected {secondary_name}')
            equipmentdb = get_equipmentdb()
            equipmentdb.update_one({"_id": interaction.user.id}, {"$set": {"secondaryid": secondary_id}}, upsert=True)
            equipmentdb.update_one({"_id": interaction.user.id}, {"$set": {"secondaryname": secondary_name}},
                                   upsert=True)
        else:
            await interaction.response.send_message('Secondary weapon not found in the inventory.')


def get_secondary_name_by_id(secondary_id):
    inventorydb = get_inventorydb()
    secondary = inventorydb.find_one({"_id": ObjectId(secondary_id)})
    return secondary




def get_primary_name_by_id(primary_id):
    inventorydb = get_inventorydb()
    primary = inventorydb.find_one({"_id": ObjectId(primary_id)})
    return primary


def get_items_by_type(owner_id):
    inventorydb = get_inventorydb()
    items = inventorydb.find({"owner_id": owner_id})

    helmets = []
    chests = []
    boots = []
    primaries = []
    secondaries = []

    for item in items:
        if item['type'] == 'helmet':
            helmets.append(item)
        elif item['type'] == 'chestplate':
            chests.append(item)
        elif item['type'] == 'boots':
            boots.append(item)
        elif item['type'] == 'primary':
            primaries.append(item)
        elif item['type'] == 'secondary':
            secondaries.append(item)

    return helmets, chests, boots, primaries, secondaries


class SupportView(nextcord.ui.View):
    def __init__(self, user_id):
        super().__init__()
        helmets, chests, boots, primaries, secondaries = get_items_by_type(user_id)

        helmet_options = self.create_options(helmets, 'helmet')
        chest_options = self.create_options(chests, 'chest')
        boots_options = self.create_options(boots, 'boots')
        primary_options = self.create_options(primaries, 'primary')
        secondary_options = self.create_options(secondaries, 'secondary')

        self.add_item(HelmetSelect(helmet_options))
        self.add_item(ChestSelect(chest_options))
        self.add_item(BootsSelect(boots_options))
        self.add_item(PrimarySelect(primary_options))
        self.add_item(SecondarySelect(secondary_options))

    @staticmethod
    def create_options(items, item_type):
        if not items:
            return [nextcord.SelectOption(label=f'No {item_type}s found', value='none')]
        elif len(items) > 25:
            items = items[:25]
        return [nextcord.SelectOption(label=item['name'], value=str(item['_id'])) for item in items]


@bot.slash_command(name="equipment", description="Setup your equipment")
async def equip(interaction: Interaction):
    playerdb = get_playerdb()
    player = playerdb.find_one({"_id": interaction.user.id})
    equipmentdb = get_equipmentdb()
    equipment = equipmentdb.find_one({"_id": interaction.user.id})
    if player is None:
        await interaction.response.send_message("Start your adventure first!", ephemeral=True)
    else:
        if equipment is None:
            embed = nextcord.Embed(
                title=" ",
                description=f"Helmet:\nArmor:\nBoots:\nPrimary:\nSecondary: ",
                color=nextcord.Color.random()
            )
            embed.set_footer(text="Kaiko v1.0")
            embed.set_author(name=f"{interaction.user.name}'s equipment", icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                                                    view=SupportView(interaction.user.id))
        else:
            embed = nextcord.Embed(
                title=" ",
                description=f"Helmet: {equipment.get('helmetname', 'Not equipped')}\nArmor: {equipment.get('armorname', 'Not equipped')}\nBoots: {equipment.get('bootsname', 'Not equipped')}\nPrimary: {equipment.get('primaryname', 'Not equipped')}\nSecondary: {equipment.get('secondaryname', 'Not equipped')}",
                color=nextcord.Color.random()
            )
            embed.set_footer(text="Kaiko v1.0")
            embed.set_author(name=f"{interaction.user.name}'s equipment", icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                                                    view=SupportView(interaction.user.id))


def setup(bot):
    bot.add_cog(EquipmentCommands(bot))
