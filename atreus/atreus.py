import discord

from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Threshold for detecting raids
RAID_MEMBER_THRESHOLD = 10
RAID_TIME_THRESHOLD = 60  # Time in seconds

members_joined = []

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    global members_joined
    members_joined.append(member.joined_at)

    # Check for raids
    if len(members_joined) >= RAID_MEMBER_THRESHOLD:
        time_difference = (members_joined[-1] - members_joined[0]).total_seconds()
        if time_difference <= RAID_TIME_THRESHOLD:
            await lockdown_mode(member.guild, enable=True)
            members_joined = []
        else:
            members_joined.pop(0)

async def lockdown_mode(guild, enable=True):
    member_role = discord.utils.get(guild.roles, name="Member")

    for channel in guild.text_channels:
        if enable:
            await channel.set_permissions(member_role, send_messages=False)
        else:
            await channel.set_permissions(member_role, send_messages=True)

    lockdown_msg = "🔒 Server lockdown enabled! Members can't send messages." if enable else "🔓 Server lockdown disabled! Members can send messages."
    await guild.system_channel.send(lockdown_msg)

@bot.command()
@commands.has_permissions(administrator=True)
async def lockdown(ctx):
    await lockdown_mode(ctx.guild, enable=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    await lockdown_mode(ctx.guild, enable=False)

bot.run('YOUR_BOT_TOKEN')