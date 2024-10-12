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

        lastMessage = data.get("lastMessageID")
        logChannelID = data.get('logChannelID')
        gameChannelID = data.get('gameChannelID')

        gameChannel = self.bot.get_channel(gameChannelID)

        if lastMessage:
            try:
                last_message = await gameChannel.fetch_message(lastMessage)
                if last_message.author.id == message.author.id:
                    return
            except discord.NotFound:
                data['lastMessageID'] = None
                data["lastMessageTime"] = None
            except discord.HTTPException:
                return

        if message.channel.id != gameChannelID:
            return

        data['lastMessageID'] = message.id
        data["lastMessageTime"] = datetime.datetime.now(datetime.timezone.utc)

        with open(conf_file_path, "w") as file:
            yaml.dump(data, file)

def setup(bot):
    bot.add_cog(OnMessageEvent(bot))