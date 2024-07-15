import discord
from discord import Option
from discord.ext import tasks
from discord.ext.commands import has_permissions

from dotenv import load_dotenv
import datetime
import os
import yaml

load_dotenv()

BOT_TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = discord.Bot(command_prefix='!', intents=intents)
FOOTER = "🎪 DJ4H-CPA"

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    # verifyTime.start()


@bot.event
async def on_message(message):
    # Ignorer le message du bot
    if message.author.bot:
        return

    # Chemin vers le potentiel fichier de configuration
    conf_file_path = f"conf/{message.guild.id}.yml"

    # Vérifier la présence d'un jeu configuré pour le serveur
    if not os.path.exists(conf_file_path):
        return

    # Vérifier que le message a été posté dans un canal de jeu
    with open(conf_file_path, "r") as conf_file:
        data = yaml.safe_load(conf_file)

    logChannelID = data['logChannelID']
    gameChannelID = data['gameChannelID']

    if message.channel.id != gameChannelID:
        return

    # Création de l'embed qui contient les logs du message
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

    #logEmbed.set_author(name="Nom du Bot",
    #                    icon_url="URL_DE_L_ICONE_DU_BOT")

    # Obtention et sauvegarde de l'id et du temps d'envoi du message pour la vérification plus tard
    data['lastMessageID'] = message.id
    data["lastMessageTime"] = datetime.datetime.now(datetime.UTC)

    with open(conf_file_path, "w") as file:
        yaml.dump(data, file)

    logChannel = bot.get_channel(logChannelID)

    await logChannel.send(embed=logEmbed)

@bot.slash_command(name="setup", description="Sets up the bot on your server.")
@has_permissions(manage_guild=True)
async def setup(ctx: discord.ApplicationContext,
                canal: Option(discord.TextChannel, description="Canal du jeu", required=True),
                temps: Option(int, description="Nombre d'heures sans message pour marquer un point", required=True, min_value=1, max_value=10, default=4),
                historique: Option(discord.TextChannel, description="Canal pour l'envoi de l'historique des messages", required=False, default=None),
                ):
    guildID = ctx.guild_id
    guildName = ctx.guild.name

    config = {
        "serverName": guildName,
        "serverID": guildID,
        "gameChannelID": canal.id,
        "gameTime": temps,
        "logChannelID": historique.id if historique else None,
        "lastMessageID": None,
        "lastMessageTime": None,
        "winners": {},
        "winMessageID": None
    }

    os.makedirs(f"conf", exist_ok=True)
    with open(f"conf/{guildID}.yml", "w") as file:
        yaml.dump(config, file)

    embed = discord.Embed(title="Configuration enregistrée",
                          description=f"La configuration suivante a été enregistrée pour **`{config['serverName']}`** :", color=0x33d17a)
    embed.add_field(name=":label: Canal de jeu", value=f"<#{canal.id}>", inline=False)
    embed.add_field(name=":hourglass_flowing_sand: Durée pour marquer un point", value=f"`{temps}` heure{'s' if temps > 1 else ''}")
    if historique:
        embed.add_field(name=":newspaper: Canal de l'historique des messages", value=f"<#{historique.id}>", inline=False)
    embed.set_footer(text=FOOTER)

    await ctx.respond(embed=embed)

"""
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
"""

bot.run(BOT_TOKEN)