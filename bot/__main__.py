import discord
from bot.bot import Bot
from bot.constants import TOKEN, PREFIX


from discord import AllowedMentions

intents = discord.Intents.all()
intents.dm_typing = False
intents.dm_reactions = False
intents.invites = False
intents.webhooks = False
intents.integrations = False


bot = Bot(
    command_prefix=PREFIX,
    case_insensitive=False,
    allowed_mentions=AllowedMentions(everyone=False),
    activity=discord.Game(name=f"Commands: {PREFIX}help"),
    intents=intents,
)

bot.load_extensions()
bot.run(TOKEN)
