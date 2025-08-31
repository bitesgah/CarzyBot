from discord.ext import commands, tasks
import discord, json
from discord import app_commands

def load_data():
  with open("jsons/selfroles.json", "r") as f:
    return json.load(f)

def save_data(data):
  with open("jsons/selfroles.json", "w") as f:
    json.dump(data, f, indent=2)

    
class Button(discord.ui.Button):
  def __init__(self, bot, role):
    super().__init__(label=role.name, style=discord.ButtonStyle.primary)
    self.bot = bot
    self.role = role

  async def callback(self, interaction: discord.Interaction):
    role = interaction.user.get_role(self.role.id)
    if not role:
      try:
        await interaction.user.add_roles(self.role)
        await interaction.response.send_message(f"You have been given <@&{self.role.id}>", ephemeral=True, delete_after=3)
      except discord.errors.Forbidden:
        await interaction.response.send_message("Missing Permissions: role is higher than my highest role", ephemeral=True, delete_after=3)
      except discord.errors.HTTPException:
        await interaction.response.send_message("too many requests, try again later", ephemeral=True, delete_after=3)
    else:
      try:
        await interaction.user.remove_roles(self.role)
        await interaction.response.send_message(f"<@&{self.role.id}> has been removed", ephemeral=True, delete_after=3)
      except discord.errors.Forbidden:
        await interaction.response.send_message("Missing Permissions: role is higher than my highest role", ephemeral=True, delete_after=3)
      except discord.errors.HTTPException:
        await interaction.response.send_message("too many requests, try again later", ephemeral=True, delete_after=3)
      

class SelfRoleView(discord.ui.View):
  def __init__(self, bot, roles, guild_id):
    super().__init__(timeout=None)

    guild = bot.get_guild(guild_id)
    for role in roles:
      role = discord.utils.get(guild.roles, id=role)
      self.add_item(Button(bot, role))



class selfroles(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot
    self.refresh_selfroles.start()

  
  @app_commands.command(description="sends selfroles UI")
  @app_commands.checks.has_permissions(manage_roles=True)
  async def send_selfroles_buttons(self, interaction: discord.Interaction, channel: discord.TextChannel):
    selfrolesData = load_data()
    if not "selfroles" in selfrolesData.keys():
      return await interaction.response.send_message("There aren't any selfroles yet", ephemeral=True, delete_after=3)
    if not selfrolesData["selfroles"]:
      return await interaction.response.send_message("There aren't any selfroles currently", ephemeral=True, delete_after=3)
    else:
      roles = selfrolesData["selfroles"]
      msg = await channel.send(view=SelfRoleView(self.bot, roles, interaction.guild.id))
      selfrolesData["selfrolesMSG"] = {"channel" : str(channel.id), "msg" : str(msg.id)}
      await interaction.response.send_message("selfroles UI sent!", ephemeral=True)
    save_data(selfrolesData)

  
  @send_selfroles_buttons.error
  async def send_selfroles_buttons_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
      await interaction.response.send_message("you need Manage_Roles Permission to run this command", ephemeral=True, delete_after=3)



  
  @app_commands.command(description="adds new selfroles")
  @app_commands.checks.has_permissions(manage_roles=True)
  async def selfrolesadd(self, interaction: discord.Interaction, role1: discord.Role, role2: discord.Role=None, role3: discord.Role=None):
    roles = False
    selfrolesData = load_data()
    if not "selfroles" in selfrolesData:
      list = []
    else:
      list = selfrolesData["selfroles"]
    if not role1.id in list:
      list.append(role1.id)
    
    if not role2 == None:
      if not role2.id in list:
        list.append(role2.id)
        roles = True
    if not role3 == None:
      if not role3.id in list:
        list.append(role3.id) 
        roles = True

    selfrolesData["selfroles"] = list
    if roles == True:
      save_data(selfrolesData)
      return await interaction.response.send_message("roles added", ephemeral=True, delete_after=3)
    await interaction.response.send_message("role was added", ephemeral=True, delete_after=3)  
    save_data(selfrolesData)

  @selfrolesadd.error
  async def selfrolesadderror(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
      await interaction.response.send_message("you need Manage_Roles Permission to run this command", ephemeral=True, delete_after=3)


  @app_commands.command(description="remove selfroles")
  @app_commands.checks.has_permissions(manage_roles=True)
  async def selfrolesremove(self, interaction: discord.Interaction, role1: discord.Role, role2: discord.Role=None, role3: discord.Role=None):
    selfrolesData = load_data()
    roles = False
    if not "selfroles" in selfrolesData:
      await interaction.response.send_message("there aren't any selfroles yet", ephemeral=True, delete_after=3)
    else:
      list = selfrolesData["selfroles"]
      list.remove(role1.id)
      
      if not role2 == None:
        list.remove(role2.id)
        roles = True
      if not role3 == None:
        list.remove(role3.id) 
        roles = True

      selfrolesData["selfroles"] = list
    if roles == True:
      save_data(selfrolesData)
      return await interaction.response.send_message("roles removed", ephemeral=True, delete_after=3)
    await interaction.response.send_message("role removed", ephemeral=True, delete_after=3)  
    save_data(selfrolesData)

  @selfrolesremove.error
  async def selfrolesremoveerror(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
      await interaction.response.send_message("you need Manage_Roles Permission to run this command", ephemeral=True, delete_after=3)


  @tasks.loop(minutes=1)
  async def refresh_selfroles(self):
    selfrolesData = load_data()
    if "selfrolesMSG" in selfrolesData:
      channel_id = selfrolesData["selfrolesMSG"]["channel"]
      msg_id = selfrolesData["selfrolesMSG"]["msg"]
      channel = self.bot.get_channel(int(channel_id))
      try:
        msg = await channel.fetch_message(msg_id)
      except:
        return print("selfroles msg not found!")
      roles = selfrolesData["selfroles"]
      if roles:
        await msg.edit(view=SelfRoleView(self.bot, roles, 556853649415077898))
      else:
        await msg.edit(view=None, content="No Selfroles at the Moment")
      print("selfroles refreshed!")
      save_data(selfrolesData)


async def setup(bot):
  await bot.add_cog(selfroles(bot))