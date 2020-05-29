import discord
import random
from discord.ext import commands
import os

token = os.getenv('Token')

client = commands.Bot(command_prefix=".")


@client.event
async def on_ready():
    print("Bot is ready")


@client.event
async def on_member_join(member):
    print(f"{member} has landed like a bawse")


@client.event
async def on_member_remvove(member):
    print(f"{member} has left")


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency *1000)}ms')


@client.command()
async def clear(ctx, amount=6):
    await ctx.channel.purge(limit=amount)


@client.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)

client.run(token)
