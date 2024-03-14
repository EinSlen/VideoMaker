import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX')

import discord
from discord.ext import commands
from download import VideoEditor

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name='editvideo')
async def edit_video(ctx, title, youtube_url, start_time, end_time):
    try:
        # Use your VideoEditor class here
        video_editor = VideoEditor(title, youtube_url, start_time, end_time)
        video_editor.main()

        result_message = f"La vidéo a été éditée avec succès !"
    except Exception as e:
        result_message = f"Erreur lors de l'édition de la vidéo : {e}"

    await ctx.send(result_message)

bot.run(TOKEN)
