import discord
import random
import json
from discord.ext import commands
import os

token = os.getenv('Token')

def get_prefix(client,message):
    with open('prefixes.json','r') as f:
        prefixes=json.load(f)
    
    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix=get_prefix)

@client.event
async def on_ready():
    print("Bot is ready")

@client.event
async def on_guild_join(guild):
    with open('prefixes.json','r') as f:
        prefixes=json.load(f)

    prefixes[str(guild.id)] = '.'

    with open('prefixes.json','w') as f:
        json.dump(prefixes,f,indent=4)

@client.event
async def on_guild_remove(guild):
    with open ('prefixes.json','r') as f:
        prefixes=json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json','w') as f:
        json.dump(prefixes,f,indent=4)

@client.command()
async def changeprefix(ctx, prefix):
    with open('prefixes.json','r') as f:
        prefixes=json.load(f)
        print(prefixes)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json','w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f'Prefix changed to {prefix}')

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
@commands.has_permissions(manage_messages=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)



client.run(token)
