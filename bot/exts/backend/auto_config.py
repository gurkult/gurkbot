import os
import typing as t
import random

from pathlib import Path

import discord
import yaml

from discord.errors import Forbidden, NotFound
from discord.ext import commands
from discord.ext.commands.context import Context
from loguru import logger


class AutoConfig(commands.Cog):
    """A cog responsible for constructing config files"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open('bot/config/config-list.yaml') as f:
            self.config_list = yaml.safe_load(f)
            self.auto = self.config_list['Auto-config']
            self.config_list.pop('Auto-config')

    @property
    def guild_id(self) -> int:
        """ Check's if the guild exists or not, if not then raises NotFound."""

        if not self.bot.get_guild(int(os.getenv('Guild_ID'))):
            logger.info(f"Cannot find the guild with id {os.getenv('Guild_ID')}. Rasing error!")
            raise NotFound(f"Cannot find guild with ids {os.getenv('Guild_ID')}")
        return int(os.getenv('Guild_ID'))

    def required(self) -> list:
        """Returns the list of information that are required for the bot to run."""

        with open('bot/config/default-config.yaml') as f:
            required_config = yaml.safe_load(f)

        for x, y in self.config_list.items():
            for k, v in y.items():
                if v['optional'] is True:
                    try:
                        del required_config[x][k]
                    except KeyError:
                        continue

        return required_config

    def check(self) -> t.Union[bool, dict]:
        """ A check that checks if the required channels, roles etc. exist or not."""

        guild = self.bot.get_guild(self.guild_id)

        #checking to see if the server has the required roles or not
        roles = [x for x in self.required()['Roles'].keys() if not discord.utils.get(guild.roles, name=x)]

        #checking for the required channels
        channels = [x for x in self.required()['Roles'].keys(
        ) if not discord.utils.get(guild.channels, name=x)]

        if not channels and not roles:
            logger.info('The check passed, the guild has all the roles and channels.!')
            return False

        elif not roles:
            logger.info(f'The guild has the required roles.')
            return {'Channels': channels}

        elif not channels:
            logger.info(f'The guild has the required channels.')
            return {'Roles': roles}

        else:
            logger.info('The guild does not have either the roles nor the channels.')
            return {'Roles': roles, 'Channels': channels}

    def false_alarm(self) -> bool:
        """Returns true if the server is alread configured but auto config is being called. """

        return os.path.exists(f'{Path.cwd()}/bot/config/config.yaml') and not self.check()

    async def create_(self) -> None:
        """A function responsible for creating all the roles and channels, if they have not already been configured."""

        guild = self.bot.get_guild(self.guild_id)

        if not self.check():
            #if the statement passed, this means that the user already has channels and roles
            #configured, we just need to get the ids.

            logger.info('The server already has the required roles and channels. Getting the ids!')

        elif 'Roles' in self.check().keys() and 'Channels' not in self.check().keys():
            logger.info('Creating the required roles for the server.')

            try:
                for r in self.check()['Roles']:
                    await guild.create_role(name=r)

            except Forbidden:
                logger.warning('The bot does not have required permissions to create the roles!')
                return

            else:
                logger.info('Successfully created all the roles and roles')

        elif 'Channels' in self.check().keys() and 'Roles' not in self.check().keys():
            logger.info('Creating the required channels for the server.')
            try:
                for c in self.required()['Channels']:
                    await guild.create_text_channel(name=c)
            except Forbidden:
                logger.warning('The bot does not have required permissions to create the channels!')
                return

            else:
                logger.info('Successfully created all the roles and channels!')

        else:
            logger.info('Creating the required roles and the channels for the server.')

            try:
                for c in self.required()['Channels']:
                    await guild.create_text_channel(name=c)

                for r in self.check()['Roles']:
                    await guild.create_role(name=r)
            except Forbidden:
                logger.warning(
                    'The bot does not have the required permissions to create the roles and the channels!')

            else:
                logger.info('Successfully created all the roles and channels and roles!')

        channel = discord.utils.get(guild.text_channels, name=random.choice(guild.text_channels).name)
        channel_invite = await channel.create_invite()

        config = {
            'Guild_ID': self.guild_id,
            'Guild_Invite': channel_invite.url,
            'Guild_Name': self.bot.get_guild(self.guild_id).name,

            'Roles': {role.name: role.id for role in guild.roles[1:]},
            'Channels': {}
        }

        for c in guild.text_channels:
            channel = c.name.replace('-', '_').title()
            if channel in self.required()['Channels']:
                config['Channels'][channel] = c.id

        with open('bot/config/config.yaml', 'w') as f:
            yaml.dump(config, f, sort_keys=False)

    @commands.Cog.listener('on_guild_available')
    async def syncer(self, guild: discord.Guild) -> None:
        """If check returns a list then creates the items in that list.
        If the bot lacks permission then dm the owner saying that it lacks the required permissions.
        """

        if not self.auto or self.false_alarm() or guild.id != self.guild_id:
            return

        await self.create_()

    @commands.command(name='setup', hidden=True)
    async def settingup(self, ctx: Context) -> None:
        """ If the auto config is false, then the user would use this command to setup their server. """

        if self.false_alarm():
            return

        if self.auto:
            raise RuntimeError("Auto-config is set to true! Cannot use setup command.")

        await self.create_()


def setup(bot):
    bot.add_cog(AutoConfig(bot))
