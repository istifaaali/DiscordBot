import youtube_dl as ytdl
import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.utils import get

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

ytdl = ytdl.YoutubeDL(ytdl_format_options)




class player:
    def __init__(self, url, request_by):
        video = self._get_info(url)
        video_format = video["formats"][0]
        self.url = url
        self.title = video["title"]
        self.author = video["uploader"]
        self.thumbnail = video["thumbnail"]
        self.video_url = video["webpage_url"]
        self.request_by = request_by

        #self.info = ytdl.extract_info(self.url, download=True)
        #self.source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("song.mp3"))

    def _get_info(self, video_url):
        with ytdl as ydl:
            info = ydl.extract_info(video_url, download=True)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]['webpage_url'])  # get info for first video
            else:
                video = info
            return video

    def get_embed(self):
        embed = discord.Embed(title=self.title, description=self.author, url=self.video_url)
        embed.set_footer(
            text=f"Requested by {self.request_by.name}",
            icon_url=self.request_by.avatar_url)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed

















    """def after_playing(self):
        song_there = os.path.isfile("song.mp3")
        if song_there:
            os.remove("song.mp3")
            print("Removed song file")

        if len(self.queue) == 1:
            self.queue = []
            print(f"REMOVED FIRST QUEUE:{self.queue}")
        elif len(self.queue) > 1:
            self.queue.pop(0)
            self.queue[0].play()
        else:
            print("Queue Done")

    def play(self, queue):
        #self.client.play(self.source, after = lambda e: self.after_playing())
        pass"""
