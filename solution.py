import discord
from discord.ext import commands
from asyncio import sleep
from youtube_dl import YoutubeDL
from youtube_api.youtube_api import YoutubeDataApi


YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'False'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


class MusicPlayer(commands.Cog):
    def __init__(self, bot, *a, **k):
        self.bot = bot
        self.vc = ''
        self.videos = 0
        self.i = 0
        self.exit = False
        self.repeat = False

    @commands.command(name='help_bot')
    async def help_bot(self, ctx, *args, **kwargs):
        await ctx.send('''  Commands:
                "m! play" to play playlist
                "m! pause" to pause music
                "m! unpause" to unpause music
                "m! repeat" to repeat song
                "m! skip" to play next song
                "m! stop" to stop music and disconnect bot from voice chanel
                "m! song x" to play music on index x''')

    @commands.command(name='repeat')
    async def repeat(self, ctx, *a, **k):
        self.repeat = True

    @commands.command(name='play')
    async def play(self, ctx, music, *a, **k):
        try:
            if not self.vc:
                print('Successful')
                voice_channel = ctx.message.author.voice.channel
                self.vc = await voice_channel.connect()
        except:
            pass

        if self.vc.is_playing():
            self.vc.stop()
        self.exit = False

        n, a = self.a(music)

        r = 'https://www.youtube.com/watch?v=' + n[self.i] + '&list=' + a + '&index=' + str(self.i)
        print(r)
        while True:
            try:
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(r, download=False)
                URL = info['formats'][0]['url']

                self.vc.play(discord.FFmpegPCMAudio(executable="ffm/ffmpeg.exe", source=URL, **FFMPEG_OPTIONS))

                while self.vc.is_playing():
                    await sleep(1)
            except BaseException:
                pass
            if self.exit:
                await ctx.voice_client.disconnect()
                break
            if not self.repeat:
                self.i += 1
                self.i %= self.videos
                if self.i == 0:
                    self.i += 1
            r = 'https://www.youtube.com/watch?v=' + n[self.i] + '&list=' + a + '&index=' + str(self.i)

    @commands.command(name='track')
    async def track(self, ctx, music, *a, **k):
        try:
            if self.vc == '':
                print('Successful')
                voice_channel = ctx.message.author.voice.channel
                self.vc = await voice_channel.connect()
        except BaseException:
            pass

        if self.vc.is_playing():
            self.vc.stop()
        self.exit = False
        try:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(music, download=False)
            URL = info['formats'][0]['url']

            self.vc.play(discord.FFmpegPCMAudio(executable="ffm/ffmpeg.exe", source=URL, **FFMPEG_OPTIONS))

            while self.vc.is_playing():
                await sleep(1)
            if self.exit:
                await ctx.voice_client.disconnect()
            while self.repeat:
                self.vc.play(discord.FFmpegPCMAudio(executable="ffm/ffmpeg.exe", source=URL, **FFMPEG_OPTIONS))
                while self.vc.is_playing():
                    await sleep(1)
                if self.exit:
                    await ctx.voice_client.disconnect()
        except BaseException as e:
            await ctx.send('Ошибка воспроизведения трека')
            print(e)

    @commands.command(name='stop')
    async def stop(self, ctx, *a, **k):
        self.exit = True
        self.vc.stop()

    @commands.command(name='skip')
    async def skip(self, *a, **k):
        self.repeat = False
        self.vc.stop()

    @commands.command(name='pause')
    async def pause(self, ctx, *a, **k):
        if self.vc.is_playing():
            self.vc.pause()

    @commands.command(name='unpause')
    async def unpause(self, ctx, *a, **k):
        if not self.vc.is_playing():
            self.vc.resume()

    @commands.command(name='song')
    async def song(self, ctx, number, *a, **k):
        number = int(number)
        self.i = number - 2
        self.vc.stop()

    def a(self, ctx):
        n = YoutubeDataApi('AIzaSyC-ohP6SdDFybh6wR4RWe-X1VKTg5VJNls')
        a = ctx.split('=')[1]
        x = n.get_videos_from_playlist_id(a)
        self.videos = len(x)
        m = []
        for i in range(len(x)):
            m.append(x[i]['video_id'])
        print(m)
        return m, a


bot = commands.Bot(command_prefix='g! ')
bot.add_cog(MusicPlayer(bot))
TOKEN = ""
bot.run(TOKEN)
