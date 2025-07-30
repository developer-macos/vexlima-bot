import discord
from discord.ext import commands
from discord import app_commands
import json


import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Load config from JSON
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_config(data):
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)

config = load_config()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔧 Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# WELCOME MESSAGE HANDLER
@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    if guild_id in config:
        channel_id = config[guild_id].get("welcome_channel")
        msg = config[guild_id].get("welcome_message", "Welcome to the server!")
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            if channel:
                await channel.send(msg.replace("{user}", member.mention))

# SETUP WELCOME
@bot.tree.command(name="setwelcome", description="Set welcome channel and message")
@app_commands.describe(channel="Where to send the welcome", message="Custom message, use {user} for the new member")
async def set_welcome(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    guild_id = str(interaction.guild.id)
    config.setdefault(guild_id, {})
    config[guild_id]["welcome_channel"] = str(channel.id)
    config[guild_id]["welcome_message"] = message
    save_config(config)
    await interaction.response.send_message(f"✅ Welcome system set to {channel.mention} with message:\n{message}", ephemeral=True)

# ANNOUNCEMENT
@bot.tree.command(name="announce", description="Send a server announcement")
@app_commands.describe(channel="Where to announce", message="Message content", mention_everyone="Mention everyone?")
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, message: str, mention_everyone: bool = False):
    content = "@everyone\n" + message if mention_everyone else message
    await channel.send(content)
    await interaction.response.send_message("📢 Announcement sent!", ephemeral=True)

# AUTO ROLE SET
@bot.tree.command(name="setautorole", description="Set an auto role for new members")
@app_commands.describe(role="Role to give to new members")
async def set_autorole(interaction: discord.Interaction, role: discord.Role):
    guild_id = str(interaction.guild.id)
    config.setdefault(guild_id, {})
    config[guild_id]["autorole"] = str(role.id)
    save_config(config)
    await interaction.response.send_message(f"🎭 Autorole set to: {role.name}", ephemeral=True)

# GIVE AUTOROLE
@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    role_id = config.get(guild_id, {}).get("autorole")
    if role_id:
        role = member.guild.get_role(int(role_id))
        if role:
            await member.add_roles(role)

# SERVER INFO
@bot.tree.command(name="serverinfo", description="Shows server info")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=guild.name, color=discord.Color.blue())
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.add_field(name="Channels", value=len(guild.channels))
    embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
    await interaction.response.send_message(embed=embed)

# MODERATION COMMANDS
@bot.tree.command(name="kick", description="Kick a member")
@app_commands.describe(user="User to kick", reason="Reason for kick")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"👢 {user} has been kicked for: {reason}")

@bot.tree.command(name="ban", description="Ban a member")
@app_commands.describe(user="User to ban", reason="Reason for ban")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {user} has been banned for: {reason}")

@bot.tree.command(name="timeout", description="Timeout a user for a number of minutes")
@app_commands.describe(user="User to timeout", minutes="How many minutes", reason="Reason")
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str = "No reason provided"):
    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await user.timeout(until=duration, reason=reason)
    await interaction.response.send_message(f"⏱️ {user.mention} has been timed out for {minutes} minutes.")

# YOUR BOT TOKEN






