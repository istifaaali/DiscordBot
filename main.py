import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.utils import get
import praw, requests,re
import random
import time
from music import player
import music
import os
import youtube_dl as ytdl
import subprocess

bot = commands.Bot(command_prefix=".")

def Memefunc():
    r = praw.Reddit(client_id = "",client_secret = "",username = "",password = "",user_agent = "testmemebot")
    subreddit = r.subreddit("dankmemes")
    posts = subreddit.hot(limit = random.randint(1,20))
    for post in posts:
        url = (post.url)
        file_name = url.split("/")
        if len(file_name) == 0:
            file_name = re.findall("/(.*?)", url)
        file_name = file_name[-1]
        if "." not in file_name:
            file_name += ".jpg"
    r = requests.get(url)
    with open(file_name,"wb") as f:
        f.write(r.content)
    return url

@bot.command()
async def meme(ctx):
    await ctx.send("Loading...")
    await ctx.send(Memefunc())

@bot.command()
async def say(ctx, *, message):
    """Repeats any message"""
    message = str(message)
    await ctx.send(message)

@bot.command()
@has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)
@clear.error
async def clear_error(ctx, error):
    await ctx.send(f"Sorry {ctx.author.mention}, you do not have permissions to do that!")

@bot.command(aliases = ["8ball", "eightball"])
async def _8ball(ctx, *, question):
    response = []
    await ctx.send(random.choice(response))

#Music
queue = []

async def audio_playing(ctx):
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        raise commands.CommandError("Not currently playing any audio.")

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'song.mp3',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl_ = ytdl.YoutubeDL(ytdl_format_options)
loop_on = False

@bot.command()
async def loop(ctx):
    global song
    """Loops the current playing song"""
    global queue
    global loop_on
    client = ctx.guild.voice_client

    if loop_on == False:
        loop_on = True
        song = queue[0]
        queue = []
        await ctx.send("Looped!")
    elif loop_on:
        loop_on = False
        queue = []
        queue.append(song)
        await ctx.send("Loop Disabled!")
        #ytdl_.download(song.url)
        #queue = []
        #source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("song.mp3"))
        #client.play(source, after= loopf)

@bot.command(aliases=["p"])
async def play(ctx, *,url):
    global queue
    global loop_on
    channel = ctx.message.author.voice.channel
    voice = ctx.author.voice
    try:
        await channel.connect()
    except:
        pass
    client = ctx.guild.voice_client
    """try:
        song_there = os.path.isfile("song.mp3")
        if song_there:
            os.remove("song.mp3")
            print("REMOVED SONG FILE")
        elif not song_there:
            print("No Song file, continuing....")
    except PermissionError:
        pass"""

    request_by = ctx.author
    def after_playing(err):
        if loop_on:
            bruh = None
            def loopf(err):
                if loop_on:
                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("song.mp3"))
                    client.play(source, after = loopf)
                if not loop_on:
                    after_playing(bruh)
            loopf(bruh)
        elif loop_on == False:
            print("----------------------------------------------------")
            print("SONG DONE!")
            print("DELETING PREVIOUS SONG FILE!")
            try:
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                    print("REMOVED SONG FILE")
            except:
                print("FAILED TO REMOVE SONG FILE")

            if len(queue) >= 1:
                print(f"LENGTH OF QUEUE IS: {len(queue)}")
                queue.pop(0)
                print("REMOVED THE FIRST SONG IN QUEUE")
                print(f"LENGTH OF QUEUE IS NOW: {len(queue)}")
                print("DOWNLOADING NEXT SONG IN QUEUE")
                info_ = ytdl_.extract_info(queue[0].url, download=True)
                print("FINISHED DOWNLOADING")
                print("NOW PLAYING NEXT SONG IN QUEUE")
                newsource = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("song.mp3"))
                client.play(newsource, after= after_playing)
                print("SONG HAS NOW STARTED")
            print("=======================================================")
    try:
        if loop_on:
            await ctx.send("Unable to play song because loop is on")
            raise PermissionError

        queue.append(player(url,request_by))
        last_song = queue[-1]


        if len(queue) == 1:
            await ctx.send("Searching...")
            print("DOWNLOADING SONG FILE #1")
            info = ytdl_.extract_info(url, download=True)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("song.mp3"))
            client.play(source, after = after_playing)
            await ctx.send(embed=queue[0].get_embed())
        elif len(queue) > 1:
            print("ADDING TO QUEUE")
            await ctx.send("Song added to queue")
            await ctx.send(embed=last_song.get_embed())
    except PermissionError:
        pass
@play.error
async def play_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Please enter a valid URL!")
    else:
        print(error)

@bot.command(aliases=["cq"])
@has_permissions(administrator=True)
async def clearqueue(ctx):
    global queue
    if len(queue) == 0:
        await ctx.send("Queue is empty")
    elif len(queue) > 0:
        try:
            song = queue[0]
            queue = []
            queue.append(song)
            await ctx.send("Queue Cleared")
        except:
            await ctx.send("Unable to clear queue")
@clearqueue.error
async def cq_error(ctx,error):
    await ctx.send(f"Sorry {ctx.author.mention}, you do not have permission to use that command!")


@bot.command()
async def showqueue(ctx):
    if loop_on:
        await ctx.send("Currently in Loop!")
    else:
        if len(queue) == 0:
            await ctx.send("No songs in queue!")
        elif len(queue) > 0:
            num_queue = len(queue)
            await ctx.send("Songs in Queue:")
            for num in range(num_queue):
                await ctx.send(f"{num+1}. *{queue[num].title}*")

@bot.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()
@join.error
async def join_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        client = ctx.guild.voice_client
        channel = ctx.message.author.voice.channel
        await client.move_to(channel)

@bot.command(aliases=["stop"])
async def leave(ctx):
    global loop_on
    global queue
    client = ctx.guild.voice_client
    loop_on = False
    queue = []
    await client.disconnect()
@leave.error
async def leave_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send("The bot is not in any channel")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} ({bot.user.id})')
    print('------')

bot.run('')
