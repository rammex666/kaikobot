import random

from bson import ObjectId
from nextcord import Interaction
from nextcord.ext import commands
from db_utils import get_playerdb, get_equipmentdb, get_inventorydb
from inventory import add_item_to_inventory
from main import bot
import asyncio
import nextcord

monsterslv5 = [
    {
        "name": "Dragon", "strength": 300, "health": 2000,
        "spawn_rate": 0.01,
        "drop": {"gold": 0.1, "rock": 0.4, "wood": 0.5},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1264962701084594217/R.png?ex=669fc7d1&is=669e7651&hm=23805cd1b9c279494ecf1bba0789268c6bdfc57e05908895fbaaeb170812f2f6&"
    },
    {
        "name": "Goblin", "strength": 15, "health": 55,
        "spawn_rate": 0.55,
        "drop": {"gold": 0.1, "rock": 0.4, "wood": 0.5},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1264963147341631608/a19f4746882b1843e03103a9ec6db8d8.png?ex=669fc83c&is=669e76bc&hm=ac6b64fce567c6e5614edcd49b4610d30f309c57b33c5ac5b979941012a14efc&"
    },
    {
        "name": "Orc", "strength": 30, "health": 150,
        "spawn_rate": 0.44,
        "drop": {"gold": 0.1, "rock": 0.4, "wood": 0.5},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1265293797302992936/R.png?ex=66a0fc2d&is=669faaad&hm=dc4aa818be67fb564200ae7adb0ac4f09ea1b4c2ed957f76f6e789005b285b0f&"
    }
]

monsterslv10 = [
    {
        "name": "Dragon", "strength": 300, "health": 2000,
        "spawn_rate": 0.01,
        "drop": {"gold": 0.1, "rock": 0.4, "wood": 0.5},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1264962701084594217/R.png?ex=669fc7d1&is=669e7651&hm=23805cd1b9c279494ecf1bba0789268c6bdfc57e05908895fbaaeb170812f2f6&"
    },
    {
        "name": "Goblin", "strength": 15, "health": 55,
        "spawn_rate": 0.20,
        "drop": {"gold": 0.1, "rock": 0.4, "wood": 0.5},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1264963147341631608/a19f4746882b1843e03103a9ec6db8d8.png?ex=669fc83c&is=669e76bc&hm=ac6b64fce567c6e5614edcd49b4610d30f309c57b33c5ac5b979941012a14efc&"
    },
    {
        "name": "Orc", "strength": 30, "health": 150,
        "spawn_rate": 0.20,
        "drop": {"gold": 0.1, "rock": 0.4, "wood": 0.5},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1265293797302992936/R.png?ex=66a0fc2d&is=669faaad&hm=dc4aa818be67fb564200ae7adb0ac4f09ea1b4c2ed957f76f6e789005b285b0f&"
    },
    {
        "name": "Troll", "strength": 20, "health": 1000,
        "spawn_rate": 0.20,
        "drop": {"gold": 0.1, "rock": 0.4, "wood": 0.5},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1265607547541524500/08159388115335.5e25b68500eae.png?ex=66a22061&is=66a0cee1&hm=10eb9b066bc8d5749e3b6c56613d936ae9dc41f5f89d9c71c8db19ec56a968a6&"
    },
    {
        "name": "Leprechaun", "strength": 30, "health": 220,
        "spawn_rate": 0.20,
        "drop": {"gold": 0.1, "rock": 0.4, "wood": 0.5},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1265607898055049266/wismer-farfadet3.png?ex=66a220b4&is=66a0cf34&hm=44c46301e467858b6359801d135f8986a82db1054c5485cfb49c455d395f0614&"
    },
    {
        "name": "Dwarf", "strength": 50, "health": 190,
        "spawn_rate": 0.19,
        "drop": {"gold": 0.1, "rock": 0.4, "wood": 0.5},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1265607674846773271/Rrrr.png?ex=66a2207f&is=66a0ceff&hm=f606f90f3709bfe664c224d5641c69e6ce629805925b5d3456b097d64a3a3fe7&"
    },
]


def get_drop(monster, owner_id):
    items, probabilities = zip(*monster["drop"].items())
    drop = random.choices(items, probabilities)[0]

    if drop == "gold":
        drop = {
            "name": "gold",
            "quantity": random.randint(1, 4),
            "quality": "F",
            "level": 1,
            "xp": 0,
            "type": "object",
            "damage": 0,
            "durability": 0,
            "description": "GOOOOOLD.",
            "rarity": "uncommon",
        }
    elif drop == "wood":
        drop = {
            "name": "Wood",
            "quantity": 1,
            "quality": "F",
            "level": 1,
            "xp": 0,
            "type": "object",
            "damage": 0,
            "durability": 0,
            "description": "sell them to the shop.",
            "rarity": "common",
        }
    elif drop == "rock":
        drop = {
            "name": "Rock",
            "quantity": 1,
            "quality": "F",
            "level": 1,
            "xp": 0,
            "type": "object",
            "damage": 0,
            "durability": 0,
            "description": "sell them to the shop.",
            "rarity": "common",
        }

    add_item_to_inventory(owner_id, **drop)


def spawn_monster(monsters):
    monster_names = [monster["name"] for monster in monsters]
    spawn_rates = [monster["spawn_rate"] for monster in monsters]
    chosen_monster = random.choices(monster_names, spawn_rates)[0]
    for monster in monsters:
        if chosen_monster == "Dragon":
            print("UN DRAGON VIEN DE SPAWWWN")
        if monster["name"] == chosen_monster:
            return monster


hunting_users = set()


class HuntCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.slash_command(name="hunt", description="Hunt a random monster")
    async def hunt(self, interaction: Interaction):
        if interaction.user.id in hunting_users:
            await interaction.response.send_message(
                "You are already hunting! Please wait until your current hunt is finished.", ephemeral=True)
            return
        playerdb = get_playerdb()
        equipmentdb = get_equipmentdb()
        mana = playerdb.find_one({"_id": interaction.user.id})["mana"]
        if mana < 35:
            await interaction.response.send_message("You don't have enough mana to hunt!", ephemeral=True)
            return

        player = playerdb.find_one({"_id": interaction.user.id})
        equipment = equipmentdb.find_one({"_id": interaction.user.id})

        time_to_travel = random.randint(10, 120) / player["speed"]

        if player is None:
            await interaction.response.send_message("You need to start your adventure to hunt monsters!",
                                                    ephemeral=True)
            return
        hunting_users.add(interaction.user.id)
        embed = nextcord.Embed(
            title="Hunting",
            description=f"You have to travel {time_to_travel}s to hunt!",
            color=nextcord.Color.random()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        for i in range(round(time_to_travel)):
            await asyncio.sleep(1)
            time_to_travel -= 1
            embed.description = f"You have to travel {time_to_travel}s to hunt!"
            await interaction.edit_original_message(embed=embed)
            if time_to_travel == 0:
                break
        if player["level"] <= 5:
            monster = spawn_monster(monsterslv5)
        if player["level"] <= 10:
            monster = spawn_monster(monsterslv10)

        embed.description = "You have arrived at the monster's location!\n\nYou Founded a " + monster[
            "name"] + "!\n\n" + "Strength: " + str(monster["strength"]) + "\nHealth: " + str(monster["health"])
        embed.set_image(url=monster["image"])
        await interaction.edit_original_message(embed=embed)

        if equipment is None:
            player_hp = player['health']
            monster_hp = monster['health']
            while player_hp > 0 and monster_hp > 0:
                monster_hp -= player['strength']
                embed.description += f"\n\nYou attacked the {monster['name']}! It has {monster_hp} HP left."
                await interaction.edit_original_message(embed=embed)
                await asyncio.sleep(1.5)

                if monster_hp > 0:
                    player_hp -= monster['strength']
                    embed.description += f"\nThe {monster['name']} attacked you! You have {player_hp} HP left."
                    await interaction.edit_original_message(embed=embed)
                    await asyncio.sleep(1.5)
        else:
            player_hp = player['health']
            player_id = interaction.user.id
            player = playerdb.find_one({"_id": player_id})
            equipment = equipmentdb.find_one({"_id": player_id})
            player_damage = player['strength']
            for equipment_type in ['helmet', 'chest', 'boots', 'secondary']:
                equipment_id = equipment.get(f'{equipment_type}id')
                if equipment_id:
                    item = get_inventorydb().find_one({"_id": ObjectId(equipment_id)})
                    if item:
                        player_hp += item['durability']

            for equipment_type in ['primary', 'secondary']:
                equipment_id = equipment.get(f'{equipment_type}id')
                if equipment_id:
                    item = get_inventorydb().find_one({"_id": ObjectId(equipment_id)})
                    if item:
                        player_damage += item['damage']

            monster_hp = monster['health']
            while player_hp > 0 and monster_hp > 0:
                monster_hp -= player_damage
                embed.description += f"\n\nYou attacked the {monster['name']}! It has {monster_hp} HP left."
                await interaction.edit_original_message(embed=embed)
                await asyncio.sleep(1.5)

                if monster_hp > 0:
                    player_hp -= monster['strength']
                    embed.description += f"\nThe {monster['name']} attacked you! You have {player_hp} HP left."
                    await interaction.edit_original_message(embed=embed)
                    await asyncio.sleep(1.5)

        if player_hp > 0:
            embed.description += f"\n\nCongratulations! You defeated the {monster['name']}!"
            await interaction.edit_original_message(embed=embed)
            get_drop(monster, interaction.user.id)

            embed.description += f"\n\nYou received a drop from the {monster['name']}!"
            await interaction.edit_original_message(embed=embed)
            playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"mana": -35}})
            playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"xp": 35}})
            playerlevel = player["level"]
            playerxp = player["xp"]
            if playerxp >= playerlevel * 105.3:
                playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"mana": 100}})
                playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"level": 1, "xp": -playerlevel * 100}})
                playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"speed": 0.1*playerlevel, "dexterity": 0.1*playerlevel, "intelligence": 0.1*playerlevel}})
                playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"health": 10, "strength": 3}})

                await interaction.followup.send("You leveled up!", ephemeral=True)
            hunting_users.remove(interaction.user.id)
        else:
            embed.description += f"\n\nYou were defeated by the {monster['name']}!"
            playerdb.update_one({"_id": interaction.user.id}, {"$set": {"mana": 0}})
            await interaction.edit_original_message(embed=embed)
            hunting_users.remove(interaction.user.id)


def setup(bot):
    bot.add_cog(HuntCommands(bot))
