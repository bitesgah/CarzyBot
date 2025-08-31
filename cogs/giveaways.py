from discord.ext import commands, tasks
import discord, random, datetime, json
from discord import app_commands
from typing import Literal


class Giveaway(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.check_finish.start()

  @app_commands.command(name="giveaway", description="Erstellt Giveaway")
  @commands.has_permissions(kick_members=True)
  async def giveaway(self, interaction: discord.Interaction, channel: discord.TextChannel,
                     skala: Literal["Sekunden", "Minuten", "Stunden", "Tage", "Wochen"],
                     dauer: int, preis: str, beschreibung: str=None):
    # Sekunden Differenz ausrechnen und Wort festhalten
    if skala == "Sekunden":
      if dauer < 10:
        return await interaction.response.send_message("Minimum 10 Sekunden <:grr:1234518266131779624>", ephemeral=True)
      einheit = "Sekunde"
      zeit = dauer
    elif skala == "Minuten":
      zeit = dauer * 60
      einheit = "Minute"
    elif skala == "Stunden":
      zeit = dauer * 3600
      einheit = "Stunde"
    elif skala == "Tage":
      zeit = dauer * 86400
      einheit = "Tag"
    else:
      zeit = dauer * 604800
      einheit = "Woche"

    # Wort hübsch machen
    if dauer > 1:
      if einheit == "Tag":
        einheit == "Tage"
      else:
        einheit += "n"

    await interaction.response.send_message(
      f"Das Giveaway wird in {channel.mention} stattfinden und {dauer} {einheit} dauern!"
    )

    with open("jsons/giveaways.json", "r") as f:
      giveaways = json.load(f)

    if beschreibung:
      description = f"**{beschreibung}**\n\nReagiere mit {giveaways['reaction']} um teilzunehmen"
    else:
      description = f"Reagiere mit {giveaways['reaction']} um teilzunehmen"

    enddate = datetime.datetime.now() + datetime.timedelta(seconds=zeit + 10)
    
    description += f"\n\n**Veranstalter:** {interaction.user.mention}"
    description += f"\n**Ende:** <t:{int(enddate.timestamp())}:R>, <t:{int(enddate.timestamp())}:f>"

    enddate = enddate - datetime.timedelta(seconds=10)

    embed = discord.Embed(
      title=preis,
      description=description,
      color=int(giveaways["emcolor"], 16))
    msg = await channel.send(embed=embed)

    await msg.add_reaction(giveaways["reaction"])

    giveaways[str(msg.id)] = {
      "prize" : preis,
      "channel":
      str(channel.id),
      "end": [
        enddate.year, enddate.month, enddate.day, enddate.hour, enddate.minute,
        enddate.second
      ]
    }

    with open("jsons/giveaways.json", "w") as f:
      json.dump(giveaways, f, indent=2)

  @app_commands.command(description="Zieht neuen Gewinner")
  @commands.has_permissions(kick_members=True)
  async def reroll(self, interaction: discord.Interaction, channel: discord.TextChannel, msgid: str):
    try:
      msg = await channel.fetch_message(msgid)
    except:
      await interaction.response.send_message("Ungültige Message Id.", ephemeral=True, delete_after=5)
      return

    users = [user async for user in msg.reactions[0].users()]
    users.pop(users.index(self.bot.user))
    if not users:
      embedDict["description"] += f"\n\n**Kein Gewinner**"
      await msg.edit(embed=discord.Embed.from_dict(embedDict))
      await msg.reply(f"Keine Teilnehmer, kein Gewinner.")
      await msg.reply(f"Kein neuer Gewinner ziehbar.")
    else:
      winner = random.choice(users)
      embedDict = msg.embeds[0].to_dict()
      embedDict["description"] += f"\n\n**Reroll Gewinner:** {winner.mention}"
      await msg.edit(embed=discord.Embed.from_dict(embedDict))
      await msg.reply(
        f"Feurige Glückwünsche, der neue Gewinner ist: {winner.mention}!"
      )
    await interaction.response.send_message("Reroll erfolgreich", ephemeral=True, delete_after=2)


  @tasks.loop(seconds=10)
  async def check_finish(self):
    with open("jsons/giveaways.json", "r") as f:
      giveaways = json.load(f)

    gsToDelete = []
    for msg_id in giveaways:
      if not type(giveaways[msg_id]) == dict:
        continue
      channel_id = giveaways[msg_id]["channel"]
      channel = self.bot.get_channel(int(channel_id))
      try:
        msg: discord.Message = await channel.fetch_message(int(msg_id))
      except:
        gsToDelete.append(msg_id)
      else:
        end = giveaways[msg_id]["end"]
        enddate = datetime.datetime(end[0], end[1], end[2], end[3], end[4], end[5])
        print("Now: " + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        if datetime.datetime.now() > enddate:
          users = [user async for user in msg.reactions[0].users()]
          users.pop(users.index(self.bot.user))
          gsToDelete.append(msg_id)
          if not users:
            embedDict = msg.embeds[0].to_dict()
            embedDict["description"] += f"\n\n**Kein Gewinner**"
            await msg.edit(embed=discord.Embed.from_dict(embedDict))
            await msg.reply(f"Keine Teilnehmer, kein Gewinner.")
          else:
            winner = random.choice(users)
            congrats_msg = giveaways["congrats"].format(winner=winner.mention, prize=giveaways[msg_id]["prize"])
            embedDict = msg.embeds[0].to_dict()
            embedDict["description"] += f"\n\n**Gewinner:** {winner.mention}"
            await msg.edit(embed=discord.Embed.from_dict(embedDict))
            await msg.reply(congrats_msg)

    for id in gsToDelete:
      if str(id) in giveaways:
        del giveaways[str(id)]

    with open("jsons/giveaways.json", "w") as f:
        json.dump(giveaways, f, indent=2)


async def setup(bot):
  await bot.add_cog(Giveaway(bot))
