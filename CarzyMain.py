import os, discord, asyncio, json, re
from discord.ext import commands

class MyDiscordBot(commands.Bot):
  
  def __init__(self, intents):
    super().__init__(command_prefix=["§","?"], intents=intents, activity=discord.Streaming(name='Brawl Stars', url='https://www.twitch.tv/carzyfire'))
    

  async def on_ready(self):
    print("Bot rasiert alles")
    for f in os.listdir('./cogs'):
      if f.endswith('.py'):
        await bot.load_extension(f'cogs.{f[:-3]}')
    await self.tree.sync()
    while True:
      try:
        channel = bot.get_channel(1178247117328887849)
        currentCount = int(channel.name.split(" ")[-1])
        if not channel.guild.member_count == currentCount:
          await channel.edit(name=f"🔥 Member: {channel.guild.member_count}")
      except:
        pass
      
      await asyncio.sleep(120)


  async def on_member_join(self, member):
    if member.guild.id == 556853649415077898:
      user = await bot.fetch_user(member.id)
      channel = await bot.fetch_channel(1242888611154890876)
      em=discord.Embed(title=":fire: Willkommen auf dem feurigen Server :fire:", description="Akzeptiere -> <#816022577831084093>\nNimm ->  <#816357529771573258>\n\nViel Spaß :heart_on_fire:", color=member.guild.me.top_role.color)
      em.set_footer(text=f"{member.guild.member_count}. Mitglied", icon_url=user.display_avatar.url)
      ytrole = member.guild.get_role(1146734579345006694)
      twitchrole = member.guild.get_role(1146734498155855953)
      community = member.guild.get_role(814554571090296863)
      tournament = member.guild.get_role(1200149079427137547)
      giveawayRole = member.guild.get_role(1242161820467466342)
      await member.add_roles(ytrole, twitchrole, community, tournament, giveawayRole)
      await channel.send(f"{user.mention}", embed=em)
    

  async def on_message(self, message: discord.Message):
    if message.author.bot:
      return
    
    member = message.guild.get_member(message.author)
    if not member:
      member = message.author

    # canPostLink = False
    # if isinstance(member, discord.Member):
    #   if member.top_role >= message.guild.get_role(571456336970252361):
    #     canPostLink = True

    # if not canPostLink:
    #   # Überprüfen ob Nachricht Link enthält
    #   pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    #   # Suche nach dem Muster im Text
    #   if re.search(pattern, message.content):
    #     await message.delete()
    #     await message.channel.send(f"Du darfst hier keine Links teilen {member.mention}! <:grr:1234518266131779624>", delete_after=5)
    #     return
      
    # Improvement Channel
    if message.channel.id == 1242081417823780985:
      await message.add_reaction("✅")
      await message.add_reaction("❌")
  

async def sendmsgtochannel(id, message, datei):
  channel = bot.get_channel(id)
  if datei == None:
    await channel.send(message)
  else:
    await channel.send(message, file=discord.File(datei))
  
      
intents = discord.Intents.all()
bot = MyDiscordBot(intents=intents)
with open("jsons/env.json", "r") as f:
  env = json.load(f)
bot.run(env['TOKEN'])

