import datetime
from dotenv import load_dotenv
import os
import discord
from discord.ext import tasks


def saveData():
    pass

load_dotenv()

BOT_TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = discord.Bot(command_prefix='!', intents=intents)

lastMessageID = None
lastMessageTime = None
channelID = 1155485801560412180
logChannelID = 1261661067403329568
guildID = 1057945976305897542

jsonData = {
    "winners": {

    },

    "winMessageID": None
}


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    verifyTime.start()


@bot.event
async def on_message(message):
    if message.author.id != bot.user.id and message.channel.id == channelID:
        global lastMessageID
        global lastMessageTime
        global logChannelID

        embed = discord.Embed(
            title="New message!",
            color=discord.Colour.blurple()
        )
        embed.add_field(name="+ Author", value=f"{message.author.name}", inline=False)
        embed.add_field(name="+ Content", value=f"{message.content}", inline=False)
        embed.add_field(name="+ Time", value=f"{message.created_at.strftime('%d/%m/%Y %H:%M:%S')}", inline=False)

        lastMessageID = message.id
        lastMessageTime = datetime.datetime.now(datetime.UTC)

        logChannel = bot.get_channel(logChannelID)

        await logChannel.send(embed=embed)


@tasks.loop(seconds=1)
async def verifyTime():
    global lastMessageID
    if lastMessageID != None:

        gameChannel = bot.get_channel(channelID)
        message = await gameChannel.fetch_message(lastMessageID)

        actualTime = datetime.datetime.now(datetime.UTC)
        elaspedTime = actualTime - lastMessageTime

        days_passed = elaspedTime.days
        seconds_passed = elaspedTime.seconds
        hours_passed = seconds_passed // 3600
        minutes_passed = (seconds_passed % 3600) // 60

        if seconds_passed >= 10:
            if message.author.id in jsonData["winners"]:
                jsonData["winners"][message.author.id] += 1
            else:
                jsonData["winners"][message.author.id] = 0
                jsonData["winners"][message.author.id] += 1

            userPoints = jsonData["winners"][message.author.id]
            if jsonData["winMessageID"] != None:
                winMessage = await gameChannel.fetch_message(jsonData["winMessageID"])
                winners = jsonData["winners"]
                winMessageEmbed = discord.Embed(
                    title=":trophy: Winners Points :trophy:",
                    color=discord.Colour.gold()
                )

                for user_id, score in winners.items():
                    user = await bot.fetch_user(user_id)
                    winMessageEmbed.add_field(
                        name=f":ticket: **{user.name}**",
                        value=f"**Points :** {score} :medal:",
                        inline=False
                    )

                winMessageEmbed.set_footer(
                    text=f"Date : {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                )

                await winMessage.edit(embed=winMessageEmbed)
            else:
                winners = jsonData["winners"]
                winMessageEmbed = discord.Embed(
                    title=":trophy: Winners Points :trophy:",
                    color=discord.Colour.gold()
                )

                for user_id, score in winners.items():
                    user = await bot.fetch_user(user_id)
                    winMessageEmbed.add_field(
                        name=f":ticket: **{user.name}**",
                        value=f"**Points :** {score} :medal:",
                        inline=False
                    )

                winMessageEmbed.set_footer(
                    text=f"Date : {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                )

                winMessage = await gameChannel.send(embed=winMessageEmbed)

                jsonData["winMessageID"] = winMessage.id

            lastMessageID = None


bot.run(BOT_TOKEN)