from discord.ext import commands, tasks
import discord, os, json
from discord import app_commands

def load_data():
  with open("jsons/ticket.json", "r") as f:
    return json.load(f)

def save_data(data):
  with open("jsons/ticket.json", "w") as f:
    json.dump(data, f, indent=2)

# The Buttons
class Button(discord.ui.Button):
  def __init__(self, bot, label, style, action):
    super().__init__(label=label, style=style)
    self.bot = bot
    self.action = action

  async def callback(self, interaction: discord.Interaction):
    name = interaction.channel.name.split("-")
    int = name[-1]
    rol = False
    ticketData = load_data()

    if "ticketmods" in ticketData:
      for role in ticketData["ticketmods"]:  
        if interaction.user.get_role(role):
         rol = True
    if rol == False and not interaction.user == interaction.guild.owner and not (self.action == 3 or self.action == 4):
      return await interaction.response.send_message("Tickets can only be managed by Moderators", delete_after=5)
    
    # Kategorie suchen
    supportCategory = None
    i = 0
    while not supportCategory and i < len(interaction.guild.categories):
      if "support" in interaction.guild.categories[i].name.replace(" ", "").lower():
        supportCategory = interaction.guild.categories[i]
      i += 1

    # Kategorie erstellen falls nicht da
    if not supportCategory:
      supportCategory = await interaction.guild.create_category_channel("support")

     # Logs Kanal suchen
    logsChannel = None
    i = 0
    while not logsChannel and i < len(supportCategory.text_channels):
      if "ticket-logs" in supportCategory.text_channels[i].name.lower():
        logsChannel = supportCategory.text_channels[i]
      i += 1

    # Logs Kanal erstellen falls nicht vorhanden
    if not logsChannel:
      logsChannel = await supportCategory.create_text_channel(name="ticket-logs", overwrites={interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)}, topic="Support Logs")

    # Delete
    if self.action == 0: 
      messages = [message async for message in interaction.channel.history()]
      f = open(f"log-{int}", "w")
      for msg in reversed(messages):
        f.write(f"\n{msg.author.name}:\n")
        if msg.clean_content: 
          f.write(f"{msg.clean_content}\n")
        for att in msg.attachments:
          f.write(f"Attachments:\n{att.proxy_url}\n")
        for em in msg.embeds:
          f.write(f"Embeds:\nTitle: {em.title}\nDescription: {em.description}\n")
      f.close()
      f = open(f"log-{int}", "rb")
      em=discord.Embed(title="", description=f"Ticket {int} was deleted by {interaction.user.mention}", color=discord.Color.red())
      await logsChannel.send("Chat Log:", embed=em, file=discord.File(f, f"log-{int}"))
      os.remove(f"log-{int}")
      del ticketData["ticketMSG"][str(int)]
      await interaction.channel.delete()

      save_data(ticketData)
  


    # Claim
    elif self.action == 1:
      ticketData["ticketMSG"][str(int)]["claimed"] = "True"
      id = ticketData["ticketMSG"][str(int)]["msg"]
      msg = await interaction.channel.fetch_message(id)
      await msg.edit(view=TicketView(self.bot, "True", ticketData["ticketMSG"][str(int)]["closed"]))

      await interaction.response.send_message("You successfully claimed the ticket", ephemeral=True, delete_after=5)

      em=discord.Embed(title="", description=f"Ticket {int} was claimed by {interaction.user.mention}", color=discord.Color.blue())
      await logsChannel.send(embed=em)
      await interaction.channel.edit(name=f"cby-{interaction.user.name}-{int}", topic=f"{interaction.channel.topic} - claimed by {interaction.user.name}")

      save_data(ticketData)
  

    # Close
    elif self.action == 2:
      await interaction.response.send_modal(ReasonModal(self.bot, int, logsChannel))

    # Create Ticket
    elif self.action == 3:
      await interaction.response.send_modal(TicketModal(self.bot))


# Reason and Ticket Closing
class ReasonModal(discord.ui.Modal):
  def __init__(self, bot, int, logs):
    super().__init__(title="Closing")
    self.bot = bot
    self.int = int
    self.logs = logs

  reason = discord.ui.TextInput(label="Reason", style=discord.TextStyle.long, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    int = self.int
    reason = str(self.reason)
    
    ticketData = load_data()
    ticketData["ticketMSG"][str(int)]["closed"] = "True"
    id = ticketData["ticketMSG"][str(int)]["msg"]
    msg = await interaction.channel.fetch_message(id)
    await msg.edit(view=TicketView(self.bot, ticketData["ticketMSG"][str(int)]["claimed"], "True"))

    await interaction.response.send_message("You successfully closed the ticket", ephemeral=True, delete_after=5)

    rea = ""
    if reason:
      rea = f"\nReason: `{reason}`"
    em=discord.Embed(title="", description=f"Ticket {int} was closed by {interaction.user.mention}{rea}")
    await self.logs.send(embed=em)
    overwrites = interaction.channel.overwrites
    user = discord.utils.get(interaction.channel.members, id=ticketData["ticketMSG"][str(int)]["user"])
    overwrites[user] = discord.PermissionOverwrite(send_messages=False, read_messages=True)
    await interaction.channel.edit(name=f"closed-{int}", topic=f"{interaction.channel.topic} - closed by {interaction.user.name}", overwrites=overwrites)

    messages = [message async for message in interaction.channel.history()]
    f = open(f"log-{int}", "w")
    for msg in reversed(messages):
      f.write(f"\n{msg.author.name}:\n")
      if msg.clean_content: 
        f.write(f"{msg.clean_content}\n")
      for att in msg.attachments:
        f.write(f"Attachments:\n{att.proxy_url}\n")
      for em in msg.embeds:
        f.write(f"Embeds:\nTitle: {em.title}\nDescription: {em.description}\n")
    f.close()
    f = open(f"log-{int}", "rb")
    await user.send(f"Your Ticket in {interaction.guild.name} was closed.{rea}\nChat log:", file=discord.File(f, f"log-{int}"))
    em=discord.Embed(title="", description="Ticket closed")
    os.remove(f"log-{int}")
    await interaction.channel.send(embed=em)

    save_data(ticketData)



# Buttonview For Ticket Creation
class TickView(discord.ui.View):
  def __init__(self, bot):
    super().__init__()
    self.add_item(Button(bot, "open ticket", discord.ButtonStyle.primary, 3))


# Buttons Creation in Support Channel
class TicketView(discord.ui.View):
  def __init__(self, bot, claimed="False", closed="False"):
    super().__init__()
    if claimed == "False":
      self.add_item(Button(bot, "claim", discord.ButtonStyle.primary, 1))
    self.add_item(Button(bot, "delete", discord.ButtonStyle.danger, 0))
    if closed == "False":
      self.add_item(Button(bot, "close", discord.ButtonStyle.gray, 2))



# Formular to fill out, creates the Ticket
class TicketModal(discord.ui.Modal):
  def __init__(self, bot):
    super().__init__(title="Create Ticket")
    self.bot = bot

  topic = discord.ui.TextInput(label="Topic", style=discord.TextStyle.short, required=True, min_length=3, max_length=30)
  description = discord.ui.TextInput(label="Description", style=discord.TextStyle.long, min_length=10, max_length=200)

  async def on_submit(self, interaction: discord.Interaction):
    titel = str(self.topic)
    content = str(self.description)
    ticketData = load_data()
      

    if not "ticket" in ticketData:
      ticketData["ticket"] = 1
    ticketData["ticket"] += 1
    zahl = ticketData["ticket"]
    overwrites = {
      interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
      interaction.user: discord.PermissionOverwrite(read_messages=True)
    }
    if "ticketmods" in ticketData:
      for role in ticketData["ticketmods"]:
        role = discord.utils.get(interaction.guild.roles, id=role)
        overwrites[role] = discord.PermissionOverwrite(read_messages=True)

    # Kategorie suchen
    supportCategory = None
    i = 0
    while not supportCategory and i < len(interaction.guild.categories):
      if "support" in interaction.guild.categories[i].name.replace(" ", "").lower():
        supportCategory = interaction.guild.categories[i]
      i += 1

    # Kategorie erstellen falls nicht da
    if not supportCategory:
      supportCategory = await interaction.guild.create_category_channel("support")

    # Ticket Kanal erstellen
    channel = await supportCategory.create_text_channel(name=f"{interaction.user.name}-{zahl}", overwrites=overwrites, topic=titel)

    # Embed erzeugen
    em=discord.Embed(title=titel, description=content, color=discord.Color.blue())
    em.set_author(name=f"New Ticket: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

    # Buttons senden und msg speichern um die Buttons refreshen zu können
    msg = await channel.send(embed=em, view=TicketView(self.bot))
    if not "ticketMSG" in ticketData:
      ticketData["ticketMSG"] = {}
    ticketData["ticketMSG"][str(zahl)] = {"msg" : str(msg.id), "channel" : str(channel.id), "claimed" : "False", "closed" : "False", "user" : interaction.user.id}

    # Logs Kanal suchen
    logsChannel = None
    i = 0
    while not logsChannel and i < len(supportCategory.text_channels):
      if "ticket-logs" in supportCategory.text_channels[i].name.lower():
        logsChannel = supportCategory.text_channels[i]
      i += 1

    # Logs Kanal erstellen falls nicht vorhanden
    if not logsChannel:
      logsChannel = await supportCategory.create_text_channel(name="ticket-logs", overwrites={interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)}, topic="Support Logs")
    
    em=discord.Embed(title="", description=f"{interaction.user.name} opened Ticket {zahl} {channel.mention}", color=discord.Color.green())
    await logsChannel.send(embed=em)

    await interaction.response.send_message("Ticket created", ephemeral=True, delete_after=5)

    save_data(ticketData)




# The Commands
class Ticket(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.refresh_tickets.start()

  @app_commands.command(description="Creates a Support Ticket")
  @app_commands.checks.cooldown(1, 60*5, key=lambda i: (i.guild_id, i.user.id))
  async def ticket(self, interaction: discord.Interaction):
    await interaction.response.send_modal(TicketModal(self.bot))

  @app_commands.command(description="Sends Ticket Creation Button")
  @app_commands.checks.has_permissions(administrator=True)
  async def send_ticket_button(self, interaction: discord.Interaction, channel: discord.TextChannel):
    ticketData = load_data()
      
    msg = await channel.send(view=TickView(self.bot))
    ticketData["CreateTicketButton"] = {"msg" : str(msg.id), "channel" : str(msg.channel.id)}
    await interaction.response.send_message(f"Buttons sent!", ephemeral=True, delete_after=3)
    save_data(ticketData)



  @app_commands.command(description="Adds a Role to Moderators")
  @app_commands.checks.has_permissions(manage_roles=True)
  async def ticket_moderator_add(self, interaction: discord.Interaction, role: discord.Role):
    ticketData = load_data()
      
    if not "ticketmods" in ticketData:
      ticketData["ticketmods"] = []
    ticketData["ticketmods"].append(role.id)
    await interaction.response.send_message(f"I added {role.mention} to moderators", ephemeral=True, delete_after=3)
    save_data(ticketData)


  @app_commands.command(description="Adds a Role to Moderators")
  @app_commands.checks.has_permissions(manage_roles=True)
  async def ticket_moderator_remove(self, interaction: discord.Interaction, role: discord.Role):
    ticketData = load_data()
      
    if not "ticketmods" in ticketData:
      ticketData["ticketmods"] = []
    ticketData["ticketmods"].remove(role.id)
    await interaction.response.send_message(f"I removed {role.mention} from moderators", ephemeral=True, delete_after=3)
    save_data(ticketData)



  @ticket.error
  async def ticket_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)


# loop for refreshing the Buttons
  @tasks.loop(minutes=1)
  async def refresh_tickets(self):
    ticketData = load_data()
      
    if "ticketMSG" in ticketData:
      for num in ticketData["ticketMSG"]:
        channel_id = ticketData["ticketMSG"][num]["channel"]
        channel = self.bot.get_channel(int(channel_id))
        try:
          id = ticketData["ticketMSG"][num]["msg"]
          msg = await channel.fetch_message(id)
        except:
          pass
        else:
          await msg.edit(view=TicketView(self.bot, ticketData["ticketMSG"][num]["claimed"], ticketData["ticketMSG"][num]["closed"]))
    if "CreateTicketButton" in ticketData:
      channel_id = ticketData["CreateTicketButton"]["channel"]
      msg_id = ticketData["CreateTicketButton"]["msg"]
      channel = self.bot.get_channel(int(channel_id))
      try:
        msg = await channel.fetch_message(msg_id)
      except:
        pass
      else:
        await msg.edit(view=TickView(self.bot))
      print("tickets refreshed!")


async def setup(bot):
  await bot.add_cog(Ticket(bot))