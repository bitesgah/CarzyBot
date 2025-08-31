from discord.ext import commands
import discord
from discord import app_commands

format = "%a, %d %b %Y, %H:%M"

class Utility(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot
    

  @app_commands.checks.has_permissions(manage_messages=True)
  @app_commands.command(description="deletes given amount of msgs")
  async def purge(self, interaction: discord.Interaction, amount: int):
    await interaction.response.defer()
    channel = interaction.channel
    user = interaction.user
    await interaction.channel.purge(limit=amount)
    await channel.send(f'{amount} messages have been purged by {user.mention}.', delete_after=5)

  @purge.error
  async def purge_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.channel.send("You don't have the necessary permissions to use this command.")
    else:
        raise error

  @app_commands.checks.has_permissions(manage_channels=True)
  @app_commands.command(description="deletes interaction channel")
  async def nuke(self, interaction: discord.Interaction):
    await interaction.channel.delete()

  @nuke.error
  async def nuke_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
      await interaction.response.send_message("You don't have the necessary permissions to use this command.", ephemeral=True)
    else:
      await interaction.response.send_message(f"Unknown error: {error}.", ephemeral=True)


  @app_commands.checks.has_permissions(manage_channels=True)
  @app_commands.command(description="clones then deletes interaction channel")
  async def respawn(self, interaction: discord.Interaction):
    await interaction.channel.clone()
    await interaction.channel.delete()

  @respawn.error
  async def respawn_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
      await interaction.response.send_message("You don't have the necessary permissions to use this command.", ephemeral=True)
    else:
      await interaction.response.send_message(f"Unknown error: {error}.", ephemeral=True)


  @app_commands.checks.has_permissions(manage_roles=True)
  @app_commands.command(description="adds role to whole server")
  async def add_guild_role(self, interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer()
    for member in interaction.guild.members:
      await member.add_roles(role)
    await interaction.channel.send("Success!", delete_after=5)

 

  @app_commands.command(description="shows Server stats")
  async def serverinfo(self, interaction: discord.Interaction):
    em = discord.Embed(color=interaction.guild.me.top_role.color)
    em.set_thumbnail(url=interaction.guild.icon.url)
    em.add_field(
    name=f"**{interaction.guild.name}** Information: ",
    value=
    f":white_small_square: Owner: **{interaction.guild.owner.display_name}** \n:white_small_square: Created at: **{interaction.guild.created_at.strftime(format)}** \n:white_small_square: Members: **{interaction.guild.member_count}** \n:white_small_square: Boosts: **{interaction.guild.premium_subscription_count}**  \n:white_small_square: Max Upload: **{int(interaction.guild.filesize_limit/1048576)}mb ** \n:white_small_square: Custom Url: **{interaction.guild.vanity_url}** \n:white_small_square: ID: **{interaction.guild.id}**"
  )
    if interaction.guild.banner:
      em.set_image(url=interaction.guild.banner.url)
    await interaction.response.send_message(embed=em)
   

async def setup(bot):
  await bot.add_cog(Utility(bot))