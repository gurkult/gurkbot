import discord
from bot import constants
from bot.bot import Bot
from bot.constants import TOKEN


from discord import AllowedMentions


intents = discord.Intents.all()
intents.dm_typing = False
intents.dm_reactions = False
intents.invites = False
intents.webhooks = False
intents.integrations = False


bot = Bot(
    command_prefix=constants.PREFIX,
    case_insensitive=False,
    allowed_mentions=AllowedMentions(everyone=False),
    activity=discord.Game(name=f"Commands: {constants.PREFIX}help"),
    intents=intents,
)

bot.load_extensions()
bot.run(TOKEN)
