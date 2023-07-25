import discord
import os
import datetime, pyowm
from discord.ext import commands
from discord import utils
from discord.utils import get
import youtube_dl
import conf



client = commands.Bot(command_prefix='.')
client.remove_command('help')

class Kuznetsova(discord.Client):
    @client.command()
    async def play(ctx, url: str):
        song_there = os.path.isfile('song.mp3')
        try:
            if song_there:
                os.remove('song.mp3')
                print('[log] Старый файл удален')
        except PermissionError:
            print('[log] Не удалось удалить файл')
        await ctx.send('Пожалуйста, ожидайте...')

        voice = get(client.voice_clients)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],

        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print('[log] Загружаю музыку...')
            ydl.download([url])
            for file in os.listdir('./'):
                if file.endswith('.mp3'):
                    name = file
                    print(f'[log] переименовываю файл: {file}')
                    os.rename(file, 'song.mp3')
            voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: print(f'[log]{name} музыка закончила свое проигрывание'))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07
            song_name = name.rsplit('-', 2)
            await ctx.send(f'Сейчас Проигрывает музыка: {song_name[0]}')


    @client.command( pass_context = True )
    @client.event

    async def hello(ctx):
        author = ctx.message.author

        await ctx.send(f'{author.mention} 50$')

    async def on_ready(ctx):
        print('Logged on as {0}!'.format(ctx.user))

    async def on_raw_reaction_add(ctx, payload):
        if payload.message_id == conf.POST_ID:
            channel = ctx.get_channel(payload.channel_id)  # получаем объект канала
            message = await channel.fetch_message(payload.message_id)  # получаем объект сообщения
            member = utils.get(message.guild.members,
                               id=payload.user_id)  # получаем объект пользователя который поставил реакцию

            try:
                emoji = str(payload.emoji)  # эмоджик который выбрал юзер
                role = utils.get(message.guild.roles, id=conf.ROLES[emoji])  # объект выбранной роли (если есть)

                if (len([i for i in member.roles if i.id not in conf.EXCROLES]) <= conf.MAX_ROLES_PER_USER):
                    await member.add_roles(role)
                    print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member, role))
                else:
                    await message.remove_reaction(payload.emoji, member)
                    print('[ERROR] Too many roles for user {0.display_name}'.format(member))

            except KeyError as e:
                print('[ERROR] KeyError, no role found for ' + emoji)
            except Exception as e:
                print(repr(e))

    async def on_raw_reaction_remove(self, payload):
        channel = self.get_channel(payload.channel_id)  # получаем объект канала
        message = await channel.fetch_message(payload.message_id)  # получаем объект сообщения
        member = utils.get(message.guild.members,
                           id=payload.user_id)  # получаем объект пользователя который поставил реакцию

        try:
            emoji = str(payload.emoji)  # эмоджик который выбрал юзер
            role = utils.get(message.guild.roles, id=conf.ROLES[emoji])  # объект выбранной роли (если есть)

            await member.remove_roles(role)
            print('[SUCCESS] Role {1.name} has been remove for user {0.display_name}'.format(member, role))

        except KeyError as e:
            print('[ERROR] KeyError, no role found for ' + emoji)
        except Exception as e:
            print(repr(e))

    @client.command()
    async def join(ctx):
        global voice
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild = ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
            await ctx.send(f'Бот присоединился к каналу: {channel}')

    @client.command()
    async def leave(ctx):
        global voice
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.disconnect()
        else:
            voice = await channel.connect()
            await ctx.send(f'Бот отключился: {channel}')



# RUN
client_ = Kuznetsova()
client_.run(conf.TOKEN)
