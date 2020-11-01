import discord
import random
import json
from discord.ext import commands
from zomato_service import top_rest
from accuweather import weatherinfo
import os
from discord.utils import get

token = os.getenv('Token')

client = commands.Bot(command_prefix=".")

@client.event
async def on_ready():
    print("Bot is ready")

@client.command()
async def weather(ctx, city):
    """Gives weather report of your city (eg: .weather coimbatore)"""
    data = weatherinfo(city)
    text = (data["Headline"]["Text"])
    date = (data["DailyForecasts"][0]["Date"])

    if (data["DailyForecasts"][0]["Day"]["HasPrecipitation"]) == True:

        dayprecep_type = (data["DailyForecasts"][0]
                          ["Day"]["PrecipitationType"])
        dayprecep_int = (data["DailyForecasts"][0]["Day"]
                         ["PrecipitationIntensity"])

        if dayprecep_int == "Heavy":
            suggestion = "Stay indoors \n Store essentials \n Make sure to turn your sprinklers off"
            emoji = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/apple/237/cloud-with-rain_1f327.png"

        elif dayprecep_int == "Moderate":
            suggestion = "Its safe to head out \n Make sure to cover/protect yourself"
            emoji = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/apple/237/umbrella_2602.png"

        elif dayprecep_int == "Light":
            suggestion = "Its a pleasant day \n Enjoy your day"
            emoji = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/lg/57/sun-behind-cloud_26c5.png"

    else:
        dayprecep_type = "NA"
        dayprecep_int = "NA"
        suggestion = "Enjoy your clear day"
        emoji = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/237/black-sun-with-rays_2600.png"

    embed = discord.Embed(
        title=f"Weather Report in {city}:",
        description=f"{text}",
        color=discord.Color.dark_gold()
    )
    embed.set_thumbnail(url=emoji)
    embed.add_field(name="Date:", value=f"{date}")
    embed.add_field(name="Day Precepitation:",
                    value=f"{dayprecep_type} \n {dayprecep_int}", inline=False)
    embed.add_field(name="Suggestion:", value=f"{suggestion}", inline=False)

    await ctx.send(embed=embed)


@client.command(aliases=["top_restaurant"])
async def food(ctx, params):
    """ For restaurant details.>>Eg: .food coimbatore,3"""
    tp = params.split(',')
    city = tp[0]
    if len(tp) > 1:
        count = tp[1]
    else:
        count = '1'
    data = top_rest(city, count)
    names = ""
    for j in range(0, int(count)):
        name = (data[j]["Name"])
        cuisines = (data[j]["Cuisines"])
        timings = (data[j]["Timings"])
        url = (data[j]["url"])
        names = names + f"{j+1}:" + "\n" + \
            f"Name : {name}" + "\n" + \
            f"Cuisines : {cuisines}" + "\n" + \
            f"Timings : {timings}" + "\n" + \
            f"url : {url}" + "\n"
        j = j+1
    embed = discord.Embed(
        title="Top restaurents near you:",
        description=f"{names}",
        color=discord.Colour.dark_gold()
    )
    await ctx.send(embed=embed)


@client.command(aliases=["8ball"])
async def _8ball(ctx, *, question):
    """Gives a random answer for a yes/no question"""
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
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
        "Very doubtful.",
    ]
    await ctx.send(f"Question:{question}\n Answer:{random.choice(responses)}")

@client.command(aliases=["creator","god"])
async def who(ctx):
    """Try it out to check who created zeal"""
    await ctx.send("Zeal discord bot was created by Nitin Ravi")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command.")


@client.event
async def on_member_join(member):
    print(f"{member} has landed like a bawse")
    for channel in member.guild.channels:
        if str(channel) == "general":
            await channel.send_message(f"""Welcome to the server {member.mention}""")


@client.event
async def on_member_remove(member):
    print(f"{member} has left")


@client.command()
async def ping(ctx):
    """Displays Zeal's Ping"""
    await ctx.send(f"Pong! {round(client.latency *1000)}ms")


@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=6):
    """Clears the last 5 messages"""
    await ctx.channel.purge(limit=amount)


@client.command()
@commands.has_permissions(manage_messages=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kicks user from server(operable with permsissions)"""
    await member.kick(reason=reason)

client.run(token)
