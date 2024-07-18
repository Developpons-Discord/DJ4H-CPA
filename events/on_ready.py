import discord
from discord.ext import commands, tasks
import yaml
import os
import datetime

FOOTER = "🎪 DJ4H-CPA"


class OnReadyEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verifyTime.start()

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            conf_file_path = f"conf/{guild.id}.yml"

            if not os.path.exists(conf_file_path):
                continue

            with open(conf_file_path, "r") as conf_file:
                data = yaml.safe_load(conf_file)

            gameChannelID = data['gameChannelID']
            lastMessageID = data.get("lastMessageID", None)

            gameChannel = self.bot.get_channel(gameChannelID)
            new_last_message_id = None

            if lastMessageID is not None:
                async for message in gameChannel.history(limit=100):
                    if not message.author.bot:
                        if lastMessageID is None or message.id != lastMessageID:
                            new_last_message_id = message.id
                            new_last_message_time = message.created_at
                            break

            if new_last_message_id:
                data['lastMessageID'] = new_last_message_id
                data['lastMessageTime'] = new_last_message_time
                with open(conf_file_path, "w") as conf_file:
                    yaml.safe_dump(data, conf_file)

        print(f"{self.bot.user} is ready and online!")

    @tasks.loop(seconds=10)
    async def verifyTime(self):
        for guild in self.bot.guilds:
            conf_file_path = f"conf/{guild.id}.yml"
            if not os.path.exists(conf_file_path):
                continue

            with open(conf_file_path, "r") as conf_file:
                data = yaml.safe_load(conf_file)

            lastMessageID = data.get('lastMessageID')
            lastMessageTime = data.get('lastMessageTime')
            gameChannelID = data.get('gameChannelID')
            gameTime = data.get('gameTime')
            winners = data.get('winners', {})
            logChannelID = data.get('logChannelID')

            if not lastMessageID or not lastMessageTime or not gameChannelID:
                continue

            gameChannel = self.bot.get_channel(gameChannelID)

            actualTime = datetime.datetime.now(datetime.timezone.utc)
            elapsedTime = actualTime - lastMessageTime
            minutes_passed = elapsedTime.total_seconds() // 3600

            if minutes_passed >= gameTime:
                message = await gameChannel.fetch_message(lastMessageID)
                if message.author.id in winners:
                    winners[message.author.id] += 1
                else:
                    winners[message.author.id] = 1

                data["winners"] = winners
                data["lastMessageID"] = None
                data["lastMessageTime"] = None

                with open(conf_file_path, "w") as file:
                    yaml.dump(data, file)

                winMessageID = data.get('winMessageID')
                winMessageEmbed = discord.Embed(
                    title=":trophy: Tableau de points :trophy:",
                    color=discord.Colour.gold(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )

                for user_id, score in winners.items():
                    user = await self.bot.fetch_user(user_id)
                    winMessageEmbed.add_field(
                        name=f":ticket: **{user.name}**",
                        value=f"**Points :** {score} :medal:",
                        inline=False
                    )

                winMessageEmbed.set_footer(
                    text=FOOTER
                )

                if winMessageID:
                    winMessage = await gameChannel.fetch_message(winMessageID)
                    await winMessage.edit(embed=winMessageEmbed)
                else:
                    winMessage = await gameChannel.send(embed=winMessageEmbed)
                    data["winMessageID"] = winMessage.id

                await winMessage.pin()

                with open(conf_file_path, "w") as file:
                    yaml.dump(data, file)

                congrats_message = f"Félicitations <@{message.author.id}>! Tu as gagné un point :trophy:!"
                await gameChannel.send(congrats_message)

                if logChannelID:
                    logEmbed = discord.Embed(
                        title=":trophy: Nouveau gagnant !",
                        description="Un nouveau membre a gagné un point !",
                        color=discord.Color.gold(),
                        timestamp=datetime.datetime.now(datetime.timezone.utc)
                    )

                    logEmbed.add_field(
                        name=":bust_in_silhouette: Auteur",
                        value=f"<@{message.author.id}>",
                        inline=False
                    )

                    logEmbed.add_field(
                        name=":speech_balloon: Contenu",
                        value=f"https://discord.com/channels/{gameChannel.guild.id}/{gameChannelID}/{lastMessageID}",
                        inline=False
                    )

                    logEmbed.add_field(
                        name=":clock3: Heure du gain",
                        value=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%d/%m/%Y %H:%M:%S')}",
                        inline=False
                    )

                    logEmbed.set_footer(text=FOOTER)
                    logEmbed.set_thumbnail(url=f"{message.author.avatar.url}")

                    logChannel = self.bot.get_channel(logChannelID)
                    await logChannel.send(embed=logEmbed)


def setup(bot):
    bot.add_cog(OnReadyEvent(bot))
