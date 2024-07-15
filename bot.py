import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Fonction pour load les extentions dans les fichiers spécifiés
def load_extensions(bot, directories):
    for directory in directories:
        for filename in os.listdir(directory):
            if filename.endswith('.py'):
                extension = f"{directory}.{filename[:-3]}"
                bot.load_extension(extension)

load_extensions(bot, ['commands', 'events'])

bot.run(BOT_TOKEN)