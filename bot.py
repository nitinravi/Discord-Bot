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
async def on_command_error(ctx, error):
    if isinstance(error,commands.CommandNotFound):
        await ctx.send('Invalid command.')

@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    responses = ["It is certain.", "It is decidedly so.",
                 "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
                 "Most likely.",
                 "Outlook good.",
                 "Yes.",
                 "Signs point to yes.",
                 "Reply hazy, try again.",
                 "Ask again later.",
                 "Better not tell you now.",
                 "Cannot predict now.",
                 "Concentrate and ask again.",
                 "Don't count on it.",
                 "My reply is no.",
                 "My sources say no.",
                 "Outlook not so good.",
                 "Very doubtful."]
    await ctx.send(f'Question:{question}\n Answer:{random.choice(responses)}')

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
