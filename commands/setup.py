import discord
from discord.ext import commands
from discord import Option
import os
import yaml
import datetime

FOOTER = "🎪 DJ4H-CPA"

class SetupCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="setup", description="Sets up the bot on your server.")
    @commands.has_permissions(manage_guild=True)
    async def setup(self, ctx: discord.ApplicationContext,
                    canal: Option(discord.TextChannel, description="Canal du jeu", required=True),
                    temps: Option(int, description="Nombre d'heures sans message pour marquer un point", required=True, min_value=1, max_value=10, default=4),
                    historique: Option(discord.TextChannel, description="Canal pour l'envoi de l'historique des messages", required=False, default=None)):
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
                              description=f"La configuration suivante a été enregistrée pour **`{config['serverName']}`** :", color=0x33d17a,
                              timestamp=datetime.datetime.now(datetime.timezone.utc)
                            )
        embed.add_field(name=":label: Canal de jeu", value=f"<#{canal.id}>", inline=False)
        embed.add_field(name=":hourglass_flowing_sand: Durée pour marquer un point", value=f"`{temps}` heure{'s' if temps > 1 else ''}")
        if historique:
            embed.add_field(name=":newspaper: Canal de l'historique des messages", value=f"<#{historique.id}>", inline=False)
        embed.set_footer(text=FOOTER)

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(SetupCommand(bot))