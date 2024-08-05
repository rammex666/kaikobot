from nextcord import Interaction, ButtonStyle
from nextcord.ext import commands
import nextcord
import asyncio
from db_utils import get_playerdb, get_equipmentdb, get_inventorydb
from bson.objectid import ObjectId
from main import bot


class DuelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.slash_command(name="duel", description="Challenge another player to a duel")
    async def duel(self, interaction: Interaction, opponent: nextcord.Member):
        playerdb = get_playerdb()
        equipmentdb = get_equipmentdb()

        player = playerdb.find_one({"_id": interaction.user.id})
        opponent_player = playerdb.find_one({"_id": opponent.id})

        if player is None or opponent_player is None:
            await interaction.response.send_message("Both players must start their adventure first!", ephemeral=True)
            return

        if player["mana"] < 50 or opponent_player["mana"] < 50:
            await interaction.response.send_message("Both players need at least 50 mana to duel!", ephemeral=True)
            return

        await interaction.response.send_message(
            f"{interaction.user.mention} has challenged {opponent.mention} to a duel!")

        view = DuelRequestView(interaction.user, opponent)
        await interaction.followup.send(f"{opponent.mention}, do you accept the duel?", view=view)


class DuelRequestView(nextcord.ui.View):
    def __init__(self, challenger, opponent):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.opponent = opponent

    @nextcord.ui.button(label="Accept", style=ButtonStyle.green)
    async def accept(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != self.opponent:
            await interaction.response.send_message("You are not the challenged player!", ephemeral=True)
            return

        await interaction.response.send_message("Duel accepted!")
        await self.start_duel(interaction)

    @nextcord.ui.button(label="Decline", style=ButtonStyle.red)
    async def decline(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != self.opponent:
            await interaction.response.send_message("You are not the challenged player!", ephemeral=True)
            return

        await interaction.response.send_message("Duel declined!")
        self.stop()

    async def start_duel(self, interaction):
        playerdb = get_playerdb()
        equipmentdb = get_equipmentdb()

        player = playerdb.find_one({"_id": self.challenger.id})
        opponent = playerdb.find_one({"_id": self.opponent.id})

        player_hp = player['health']
        opponent_hp = opponent['health']

        player_damage = player['strength']
        opponent_damage = opponent['strength']

        player_equipment = equipmentdb.find_one({"_id": player["_id"]})
        opponent_equipment = equipmentdb.find_one({"_id": opponent["_id"]})

        if player_equipment:
            player_damage += self.calculate_equipment_damage(player_equipment)
            player_hp += self.calculate_equipment_durability(player_equipment)

        if opponent_equipment:
            opponent_damage += self.calculate_equipment_damage(opponent_equipment)
            opponent_hp += self.calculate_equipment_durability(opponent_equipment)

        turn = 0
        while player_hp > 0 and opponent_hp > 0:
            if turn % 2 == 0:
                opponent_hp -= player_damage
                await interaction.followup.send(
                    f"{self.challenger.mention} attacked {self.opponent.mention}! {self.opponent.mention} has {opponent_hp} HP left.")
            else:
                player_hp -= opponent_damage
                await interaction.followup.send(
                    f"{self.opponent.mention} attacked {self.challenger.mention}! {self.challenger.mention} has {player_hp} HP left.")

            await asyncio.sleep(1.5)
            turn += 1

        if player_hp > 0:
            await interaction.followup.send(f"{self.challenger.mention} won the duel !")
            playerdb.update_one({"_id": player["_id"]}, {"$inc": {"mana": -50}})
            playerdb.update_one({"_id": opponent["_id"]}, {"$inc": {"mana": -50}})
        else:
            await interaction.followup.send(f"{self.opponent.mention} won the duel !")
            playerdb.update_one({"_id": player["_id"]}, {"$inc": {"mana": -50}})
            playerdb.update_one({"_id": opponent["_id"]}, {"$inc": {"mana": -50}})

    def calculate_equipment_damage(self, equipment):
        damage = 0
        for equipment_type in ['primary', 'secondary']:
            equipment_id = equipment.get(f'{equipment_type}id')
            if equipment_id:
                item = get_inventorydb().find_one({"_id": ObjectId(equipment_id)})
                if item:
                    damage += item['damage']
        return damage

    def calculate_equipment_durability(self, equipment):
        durability = 0
        for equipment_type in ['helmet', 'chest', 'boots', 'secondary']:
            equipment_id = equipment.get(f'{equipment_type}id')
            if equipment_id:
                item = get_inventorydb().find_one({"_id": ObjectId(equipment_id)})
                if item:
                    durability += item['durability']
        return durability


def setup(bot):
    bot.add_cog(DuelCommands(bot))
