import random
from nextcord import Interaction
from nextcord.ext import commands
from db_utils import get_playerdb, get_equipmentdb, get_inventorydb
from main import bot
import asyncio
import nextcord

monsters = [
    {
        "name": "Dragon", "strength": 300, "health": 2000,
        "spawn_rate": 0.01,
        "drop": {"gold": 0.5, "rock": 0.3, "wood": 0.2},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1264962701084594217/R.png?ex=669fc7d1&is=669e7651&hm=23805cd1b9c279494ecf1bba0789268c6bdfc57e05908895fbaaeb170812f2f6&"
    },
    {
        "name": "Goblin", "strength": 15, "health": 55,
        "spawn_rate": 0.99,
        "drop": {"gold": 0.7, "rock": 0.1, "wood": 0.2},
        "image": "https://cdn.discordapp.com/attachments/1081964131948695614/1264963147341631608/a19f4746882b1843e03103a9ec6db8d8.png?ex=669fc83c&is=669e76bc&hm=ac6b64fce567c6e5614edcd49b4610d30f309c57b33c5ac5b979941012a14efc&"
    },
]


def get_drop(monster):
    items, probabilities = zip(*monster["drop"].items())
    drop = random.choices(items, probabilities)[0]

    if drop == "gold":
        drop = {
            "name": "gold",
            "quantity": random.randint(1, 100),
            "rairity": "common",
            "type": "drop"
        }
    else:
        drop = {
            "name": drop,
            "quantity": random.randint(1, 100),
            "rairity": "common",
            "type": "drop"
        }

    return drop


def spawn_monster(monsters):
    monster_names = [monster["name"] for monster in monsters]
    spawn_rates = [monster["spawn_rate"] for monster in monsters]
    chosen_monster = random.choices(monster_names, spawn_rates)[0]
    for monster in monsters:
        if monster["name"] == chosen_monster:
            return monster


class HuntCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.slash_command(name="hunt", description="Hunt a random monster")
    async def hunt(self, interaction: Interaction):
        playerdb = get_playerdb()
        equipmentdb = get_equipmentdb()
        mana = playerdb.find_one({"_id": interaction.user.id})["mana"]
        if mana < 35:
            await interaction.response.send_message("You don't have enough mana to hunt!", ephemeral=True)
            return

        player = playerdb.find_one({"_id": interaction.user.id})
        equipment = equipmentdb.find_one({"_id": interaction.user.id})

        time_to_travel = random.randint(10, 120)

        if player is None:
            await interaction.response.send_message("You need to start your adventure to hunt monsters!",
                                                    ephemeral=True)
            return

        embed = nextcord.Embed(
            title="Hunting",
            description=f"You have to travel {time_to_travel}s to hunt!",
            color=nextcord.Color.random()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        for i in range(time_to_travel):
            await asyncio.sleep(1)
            time_to_travel -= 1
            embed.description = f"You have to travel {time_to_travel}s to hunt!"
            await interaction.edit_original_message(embed=embed)
            if time_to_travel == 0:
                break

        monster = spawn_monster(monsters)

        embed.description = "You have arrived at the monster's location!\n\nYou Founded a " + monster[
            "name"] + "!\n\n" + "Strength: " + str(monster["strength"]) + "\nHealth: " + str(monster["health"])
        embed.set_image(url=monster["image"])
        await interaction.edit_original_message(embed=embed)

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

        if player_hp > 0:
            embed.description += f"\n\nCongratulations! You defeated the {monster['name']}!"
            await interaction.edit_original_message(embed=embed)
            drop = get_drop(monster)

            inventorydb = get_inventorydb()

            inventory = inventorydb.find_one({"_id": interaction.user.id})

            if inventory is None:
                inventorydb.insert_one({"_id": interaction.user.id, "items": {drop['name']: drop}})
            else:
                if drop['name'] in inventory["items"]:
                    inventory["items"][drop['name']]['quantity'] += drop['quantity']
                else:
                    inventory["items"][drop['name']] = drop

                inventorydb.update_one({"_id": interaction.user.id}, {"$set": {"items": inventory["items"]}})

            embed.description += f"\n\nYou received a {drop['name']} from the {monster['name']}!"
            await interaction.edit_original_message(embed=embed)
            playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"mana": -35}})
            playerdb.update_one({"_id": interaction.user.id}, {"$inc": {"xp": 35}})
        else:
            embed.description += f"\n\nYou were defeated by the {monster['name']}!"
            playerdb.update_one({"_id": interaction.user.id}, {"mana": 0})
            await interaction.edit_original_message(embed=embed)


def setup(bot):
    bot.add_cog(HuntCommands(bot))
