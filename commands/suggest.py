from nextcord import Interaction
from main import bot
from nextcord.ext import commands
import nextcord
from nextcord.ui.text_input import TextInput


class SuggestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class CommandeModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Suggestion")

        self.type = TextInput(
            label="Mob ou Item",
            min_length=2,
            max_length=50,
            required=True,
        )
        self.add_item(self.type)

        self.name = TextInput(
            label="Nom",
            min_length=2,
            max_length=50,
            required=True,
        )
        self.add_item(self.name)

        self.drop = TextInput(
            label="Drop Si Mob",
            min_length=2,
            max_length=50,
            required=False,
        )
        self.add_item(self.drop)

        self.damage = TextInput(
            label="damage / dura / rareté / qualité si item",
            min_length=2,
            max_length=50,
            required=False,
        )
        self.add_item(self.damage)

        self.description = TextInput(
            label="Description",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Donnez un lore a l'item ou au mob...",
            required=True,
            max_length=1800,
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        guild = nextcord.utils.get(bot.guilds, id=1071553086784536717)
        channel = guild.get_channel(1265351800655970394)
        await channel.send(
            f"Nom: {self.name.value}\nType: {self.type.value}\nDrop: {self.drop.value}\ndamage / dura / rareté / qualité si item: {self.damage.value}\nDescription: {self.description.value}")


@bot.slash_command(name="suggest", description="make a suggest")
async def suggest(interaction: Interaction):
    view = CommandeModal()
    await interaction.response.send_modal(view)


def setup(bot):
    bot.add_cog(SuggestCommands(bot))
