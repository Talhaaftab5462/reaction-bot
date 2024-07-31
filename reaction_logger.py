import discord
from discord.ext import commands
import logging
from datetime import datetime, timezone, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
intents.guilds = True
intents.members = True  # Ensure this is enabled if you want to log reactions from members

bot = commands.Bot(command_prefix="!", intents=intents)

# Fetch channel IDs from environment variables
LOG_CHANNELS = {
    int(os.getenv('GUILD_ID_1')): int(os.getenv('LOG_CHANNEL_ID_1')),
    int(os.getenv('GUILD_ID_2')): int(os.getenv('LOG_CHANNEL_ID_2'))
}

# Timezone offset for GMT +5:00
LOCAL_TIMEZONE_OFFSET = timedelta(hours=5)

def get_local_time():
    return datetime.now(timezone.utc) + LOCAL_TIMEZONE_OFFSET

def get_unix_timestamp():
    return int(get_local_time().timestamp())

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    try:
        guild_id = reaction.message.guild.id
        log_channel_id = LOG_CHANNELS.get(guild_id)
        
        if log_channel_id is None:
            logging.error(f"Log channel not found for guild: {guild_id}")
            return
        
        log_channel = bot.get_channel(log_channel_id)
        if log_channel is None:
            logging.error(f"Log channel not found: {log_channel_id}")
            return
        
        embed = discord.Embed(title="Reaction Added", color=discord.Color.green(), timestamp=get_local_time())
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Channel", value=reaction.message.channel.mention, inline=True)
        embed.add_field(name="Message", value=f"[Jump to message]({reaction.message.jump_url})", inline=True)
        embed.add_field(name="Reaction", value=str(reaction.emoji), inline=True)
        embed.add_field(name="Time", value=f"<t:{get_unix_timestamp()}:f>", inline=False)  # Full date and time
        await log_channel.send(embed=embed)
        logging.info(f"Logged reaction add by {user} in {reaction.message.channel}")
    except Exception as e:
        logging.error(f"Error in on_reaction_add: {e}")

@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    try:
        guild_id = reaction.message.guild.id
        log_channel_id = LOG_CHANNELS.get(guild_id)
        
        if log_channel_id is None:
            logging.error(f"Log channel not found for guild: {guild_id}")
            return
        
        log_channel = bot.get_channel(log_channel_id)
        if log_channel is None:
            logging.error(f"Log channel not found: {log_channel_id}")
            return

        embed = discord.Embed(title="Reaction Removed", color=discord.Color.red(), timestamp=get_local_time())
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Channel", value=reaction.message.channel.mention, inline=True)
        embed.add_field(name="Message", value=f"[Jump to message]({reaction.message.jump_url})", inline=True)
        embed.add_field(name="Reaction", value=str(reaction.emoji), inline=True)
        embed.add_field(name="Time", value=f"<t:{get_unix_timestamp()}:f>", inline=False)  # Full date and time
        await log_channel.send(embed=embed)
        logging.info(f"Logged reaction remove by {user} in {reaction.message.channel}")
    except Exception as e:
        logging.error(f"Error in on_reaction_remove: {e}")

bot.run(os.getenv('BOT_TOKEN'))
