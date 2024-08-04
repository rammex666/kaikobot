import random
from mobs import *
from bson import ObjectId
from nextcord import Interaction
from nextcord.ext import commands
from db_utils import get_playerdb, get_equipmentdb, get_inventorydb
from inventory import add_item_to_inventory
from main import bot
import asyncio
import nextcord


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
            monster = spawn_monster(getlv5monster())
        elif player["level"] <= 10:
            monster = spawn_monster(getlv10monster())
        elif player["level"] <= 20:
            monster = spawn_monster(getlv20monster())
        else:
            monster = spawn_monster(getlv20monster())
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
            monstername = monster['name']
            monsterxp = {
                "Dwarf": 50,
                "Leprechaun": 50,
                "Troll": 40,
                "Daemon": 70,
                "Elf": 70,
                "Dragon": 2000,
                "Orc": 35,
                "Goblin": 35,
            }
            embed.description += f"\n\nCongratulations! You defeated the {monster['name']}!"
            await interaction.edit_original_message(embed=embed)
            get_drop(monster, interaction.user.id)

            embed.description += f"\n\nYou received a drop from the {monster['name']}!"
            await interaction.edit_original_message(embed=embed)
            playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"mana": -35}})
            playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"xp": monsterxp.get(monstername, 0)}})
            playerlevel = player["level"]
            playerxp = player["xp"]

            if playerxp >= playerlevel * 105.3:
                playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"mana": 100}})
                playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"level": 1, "xp": -playerlevel * 100}})
                playerdb.update_one({"_id": interaction.user.id}, {
                    "$inc": {"speed": 0.1 * playerlevel, "dexterity": 0.1 * playerlevel,
                             "intelligence": 0.1 * playerlevel}})
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
