import discord
from discord import Option
from discord.ext.commands import has_permissions

import yaml
import os

# Récupérer le token du bot
with open("token.txt", "r") as token_file:
    TOKEN = token_file.read().strip()


client = discord.Bot(intents=discord.Intents.all())
FOOTER: str = "🎪 DJ4H-CPA"


@client.event
async def on_ready():
    print(f"[v] {client.user.name} online")
    await client.change_presence(activity=discord.Game("Jeu des 4 heures"))


@client.slash_command(name="configuration", description="Mise en place du bot")
@has_permissions(manage_guild=True)
async def setup(msg, canal: Option(discord.TextChannel, description="Canal de jeu", required=True),
                temps: Option(int, description="Nombre d'heure sans message pour marquer un point", required=True,
                              min_value=1, max_value=10, default=4)
                ):

    # Écrire la configuration dans un fichier
    with open(f"conf/{msg.guild_id}.yml", "w") as file:
        file.write(yaml.dump({"channel": canal.id, "duration": temps}))

    embed = discord.Embed(title="Configuration enregistrée",
                          description="La configuration suivante a été enregistrée :", color=0x33d17a)
    embed.add_field(name="🏷️ Canal de jeu", value=f"<#{canal.id}>", inline=False)
    embed.add_field(name="⏳ Durée pour marquer un point", value=f"`{temps}` heure{'s' if temps > 1 else ''}")
    embed.set_footer(text=FOOTER)

    await msg.respond(embed=embed)


@client.event
async def on_message(msg):
    # Ignorer le message des bots
    if msg.author.bot:
        return

    # Chemin vers le potentiel fichier de configuration
    conf_file_path = f"conf/{msg.guild.id}.yml"

    # Vérifier la présence d'un jeu configuré pour le serveur
    if not os.path.exists(conf_file_path):
        return

    # Vérifier que le message a été posté dans un canal de jeu
    with open(conf_file_path, "r") as conf_file:
        if msg.channel.id != yaml.safe_load(conf_file)['channel']:
            return

    # ---- Le message appartient au jeu ----


client.run(TOKEN)
