import nextcord
from nextcord import Interaction
from main import bot
from db_utils import get_equipmentdb, get_inventorydb, get_playerdb
from nextcord.ext import commands


class StatsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


@bot.slash_command(name="stats", description="Look at your stats")
async def start(interaction: Interaction, member: nextcord.Member = None, byid: str = None):
    playerdb = get_playerdb()
    if member is None:
        if byid is None:
            player = playerdb.find_one({"_id": interaction.user.id})
            if player is None:
                await interaction.response.send_message("Start your adventure first!", ephemeral=True)
            else:
                embed = nextcord.Embed(
                    title=" ",
                    description=f"Money: {player['money']}\nLevel: {player['level']}\nXP: {player['xp']}/{player['level']*105.3}\nMana : {player['mana']} / 500\nHealth : {player['health']}\nStrength : {player['strength']}\nDexterity : {player['dexterity']}\nIntelligence : {player['intelligence']}\nSpeed : {player['speed']}",
                    color=nextcord.Color.random()
                )
                embed.set_footer(text="Kaiko v1.0")
                embed.set_author(name=f"{interaction.user.name}'s stats", icon_url=interaction.user.avatar.url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else :
            player = playerdb.find_one({"_id": int(byid)})
            if player is None:
                await interaction.response.send_message("This user hasn't started their adventure yet!", ephemeral=True)
            else:
                member = await bot.fetch_user(int(byid))
                embed = nextcord.Embed(
                    title=" ",
                    description=f"Money: {player['money']}\nLevel: {player['level']}\nXP: {player['xp']}/{player['level']*105.3}\nMana : {player['mana']} / 500\nHealth : {player['health']}\nStrength : {player['strength']}\nDexterity : {player['dexterity']}\nIntelligence : {player['intelligence']}\nSpeed : {player['speed']}",
                    color=nextcord.Color.random()
                )
                embed.set_footer(text="Kaiko v1.0")
                embed.set_author(name=f"{member.name}'s stats", icon_url=member.avatar.url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        player = playerdb.find_one({"_id": member.id})
        if player is None:
            await interaction.response.send_message("This user hasn't started their adventure yet!", ephemeral=True)
        else:
            embed = nextcord.Embed(
                title=" ",
                description=f"Money: {player['money']}\nLevel: {player['level']}\nXP: {player['xp']}/{player['level']*105.3}\nMana : {player['mana']} / 500\nHealth : {player['health']}\nStrength : {player['strength']}\nDexterity : {player['dexterity']}\nIntelligence : {player['intelligence']}\nSpeed : {player['speed']}",
                color=nextcord.Color.random()
            )
            embed.set_footer(text="Kaiko v1.0")
            embed.set_author(name=f"{member.name}'s stats", icon_url=member.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)



def setup(bot):
    bot.add_cog(StatsCommands(bot))
