import discord
import random
import youtube_dl
import asyncio
import json
from discord.ext import commands
from youtube_dl import YoutubeDL
from zomato_service import top_rest
import os

token = os.getenv('Token')

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 as ipv6 addresses can cause issues
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def get_prefix(_, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix=get_prefix)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, url):
        """Plays from a url or keyword"""

        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print(
            'Player error: %s' % e) if e else None)
        embed = discord.Embed(
            title="Now playing:",
            description=f"{player.title}",
            color=discord.Colour.dark_gold()
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=['PAUSE'])
    async def pause(self, ctx):
        """Pauses the song playing"""
        ctx.voice_client.pause()
        await ctx.send("Song paused.")

    @commands.command(aliases=['RESUME', 'continue', 'CONTINUE'])
    async def resume(self, ctx):
        """Resumes a paused song"""
        ctx.voice_client.resume()
        await ctx.send("Song resumed.")

    @commands.command(aliases=["stop", "disconnect", "bye"])
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


@client.event
async def on_ready():
    print("Bot is ready")


@client.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "."

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)


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


@client.command()
async def changeprefix(ctx, prefix):
    """Changes the prefix for instructions"""
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
        print(prefixes)

    prefixes[str(ctx.guild.id)] = prefix

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f"Prefix changed to {prefix}")


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
async def clear(ctx, amount=6):
    """Clears the last 5 messages"""
    await ctx.channel.purge(limit=amount)


@client.command()
@commands.has_permissions(manage_messages=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kicks user from server(operable with permsissions)"""
    await member.kick(reason=reason)


client.add_cog(Music(client))
client.run(token)
