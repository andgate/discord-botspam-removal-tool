import discord
from discord.errors import ConnectionClosed, GatewayNotFound, HTTPException, LoginFailure

TOKEN = 'DISCORD_TOKEN'
GUILD_ID = 123
BOT_CHANNEL_ID_LIST = [ 1234 ]
BOT_ID = 1234

def is_not_bot_channel(c):
    channel_id = c.id
    return not any(map(lambda id: id == channel_id, BOT_CHANNEL_ID_LIST))

def is_bot_spam(m):
    return m.author.id == BOT_ID

class BotSpamRemovalClient(discord.Client):
    def __init__(self):
        super().__init__()

    async def use_token(self, token):
        self.token = token
        try:
            await self.login(self.token)
            await self.connect()
        except LoginFailure:
            raise
        except HTTPException:
            raise
        except GatewayNotFound:
            raise
        except ConnectionClosed:
            raise

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        # Get the guild
        guild = self.get_guild(GUILD_ID)
        print(
            f'{self.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

        # Get the list on non-bot channels
        channels = filter(is_not_bot_channel, guild.text_channels)      
        print(f'{self.user} is purging to the following channels:')
        for channel in channels:
            print(f'{channel.name}(id: {channel.id})')

        input('press enter to purge...')

        # Purge each channel
        for channel in channels:
            deleted = await channel.purge(limit=None, check=is_bot_spam)
            print(f'deleted {len(deleted)} bot spam message(s) from channel {channel.name})')
