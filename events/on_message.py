import discord
from discord.ext import commands
import datetime
import os
import yaml

FOOTER = "🎪 DJ4H-CPA"

class OnMessageEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        conf_file_path = f"conf/{message.guild.id}.yml"

        if not os.path.exists(conf_file_path):
            return

        with open(conf_file_path, "r") as conf_file:
            data = yaml.safe_load(conf_file)

        logChannelID = data['logChannelID']
        gameChannelID = data['gameChannelID']

        if message.channel.id != gameChannelID:
            return

        logEmbed = discord.Embed(
            title=":mailbox_with_mail: Nouveau message !",
            description="Un nouveau message a été posté !",
            color=discord.Color.dark_red(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        logEmbed.add_field(
            name=":bust_in_silhouette: Auteur",
            value=f"{message.author.name}",
            inline=False
        )

        logEmbed.add_field(
            name=":speech_balloon: Contenu",
            value=f"{message.content}",
            inline=False
        )

        logEmbed.add_field(
            name=":clock3: Heure",
            value=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%d/%m/%Y %H:%M:%S')}",
            inline=False
        )

        logEmbed.set_footer(text=FOOTER)
        logEmbed.set_thumbnail(url=f"{message.author.avatar.url}")

        data['lastMessageID'] = message.id
        data["lastMessageTime"] = datetime.datetime.now(datetime.timezone.utc)

        with open(conf_file_path, "w") as file:
            yaml.dump(data, file)

        logChannel = self.bot.get_channel(logChannelID)
        await logChannel.send(embed=logEmbed)

def setup(bot):
    bot.add_cog(OnMessageEvent(bot))