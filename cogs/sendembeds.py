from discord.ext import commands
import discord, validators, re
from discord import app_commands

class Button(discord.ui.Button):
  def __init__(self, bot, label, style, mode, ems, channel):
    super().__init__(label=label, style=style)
    self.bot = bot
    self.mode = mode
    self.ems = ems
    self.channel = channel
  
  async def callback(self, interaction: discord.Interaction):
    if self.mode == 1:
      await self.channel.send(embeds=self.ems)
      await interaction.response.send_message("Embeds Sent!", ephemeral=True, delete_after=3)
    elif self.mode == 2:
      await interaction.response.send_modal(EmbedModal1(self.bot, self.ems, self.channel))
    else:
      await interaction.response.send_modal(EmbedModal2(self.bot, self.ems, self.channel))
    

class ButtonView(discord.ui.View):
  def __init__(self, bot, ems, channel):
    super().__init__()
    
    if not len(ems) == 0:
      self.add_item(Button(bot, "Send Embeds", discord.ButtonStyle.green, 1, ems, channel))
    if not len(ems) == 10:
      self.add_item(Button(bot, "Add an Embed", discord.ButtonStyle.primary, 2, ems, channel))


class NextPageView(discord.ui.View):
  def __init__(self, bot, ems, channel):
    super().__init__()
    
    self.add_item(Button(bot, "Next Page", discord.ButtonStyle.primary, 3, ems, channel))


class EmbedModal1(discord.ui.Modal):
  def __init__(self, bot, ems, channel):
    super().__init__(title="Create Embed")
    self.bot = bot
    self.ems = ems
    self.channel = channel
    
  topic = discord.ui.TextInput(label="Title", style=discord.TextStyle.short, max_length=256, required=False)
  description = discord.ui.TextInput(label="Description", placeholder="jump to next row with -br-", style=discord.TextStyle.long, max_length=2048, required=False)
  color = discord.ui.TextInput(label="Color Hex Code", placeholder="example: #5FE99A", style=discord.TextStyle.short)
  image_url = discord.ui.TextInput(label="Image Url", style=discord.TextStyle.short, required=False)
  thumbnail_url = discord.ui.TextInput(label="Thumbnail Image Url", placeholder="https://...", style=discord.TextStyle.short, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    title = str(self.topic)
    if not title:
      title = ""
    description = str(self.description)
    if not description:
      description = ""
    thumbnail_url = str(self.thumbnail_url)
    if thumbnail_url and not validators.url(thumbnail_url):
      return await interaction.response.send_message(f"Did not create the Embed. Thumbnail Url was invalid. {len(self.ems)} Embeds in List", ephemeral=True, delete_after=10, view=ButtonView(self.bot, self.ems, self.channel))   
    image_url = str(self.image_url)
    if image_url and not validators.url(image_url):
      return await interaction.response.send_message(f"Did not create the Embed. Image Url was invalid. {len(self.ems)} Embeds in List", ephemeral=True, delete_after=10, view=ButtonView(self.bot, self.ems, self.channel))
    color = str(self.color)
    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
    if not match:                      
      return await interaction.response.send_message(f"Did not create the Embed. Hex Code was invalid. {len(self.ems)} Embeds in List", ephemeral=True, delete_after=10, view=ButtonView(self.bot, self.ems, self.channel))

    
    
    description_split = description.split("-br-")
    descr = description_split[0]
    for j in range(len(description_split)-1):
      descr += "\n" + description_split[j+1]
      
    em = discord.Embed(title=title, description=descr, color=int(color[1:], 16))
    if image_url:
      em.set_image(url=image_url)
    if thumbnail_url:
     em.set_thumbnail(url=thumbnail_url)
   
    self.ems.append(em)
    await interaction.response.send_message(ephemeral=True, delete_after=5, view=NextPageView(self.bot, self.ems, self.channel))


class EmbedModal2(discord.ui.Modal):
  def __init__(self, bot, ems, channel):
    super().__init__(title="Embed Extras")
    self.bot = bot
    self.ems = ems
    self.channel = channel
    
  author = discord.ui.TextInput(label="Author Name", style=discord.TextStyle.short, max_length=256, required=False)
  author_url = discord.ui.TextInput(label="Author Url", placeholder="https://...", style=discord.TextStyle.long, max_length=2048, required=False)
  author_icon_url  = discord.ui.TextInput(label="Author Icon Url", style=discord.TextStyle.short, required=False, placeholder="https://...")
  footer_text = discord.ui.TextInput(label="Footer Text", style=discord.TextStyle.short, max_length=2048, required=False)
  footer_icon_url = discord.ui.TextInput(label="Footer Icon Url", placeholder="https://...", style=discord.TextStyle.short, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    author = str(self.author)
    author_url = str(self.author_url)
    if author_url and not validators.url(author_url):
      return await interaction.response.send_message(f"Did not edit the Embed. author_url was invalid. {len(self.ems)} Embeds in List", ephemeral=True, delete_after=10, view=NextPageView(self.bot, self.ems, self.channel))
    author_icon_url = str(self.author_icon_url)
    if author_icon_url and not validators.url(author_icon_url):
      return await interaction.response.send_message(f"Did not edit the Embed. author_icon_url was invalid. {len(self.ems)} Embeds in List", ephemeral=True, delete_after=10, view=NextPageView(self.bot, self.ems, self.channel))
    footer_text = str(self.footer_text)
    footer_icon_url = str(self.footer_icon_url)
    if footer_icon_url and not validators.url(footer_icon_url):
      return await interaction.response.send_message(f"Did not edit the Embed. footer_icon_url was invalid. {len(self.ems)} Embeds in List", ephemeral=True, delete_after=10, view=NextPageView(self.bot, self.ems, self.channel))
    
    
    if author and author_url and author_icon_url:
      self.ems[-1].set_author(name=author, url=author_url, icon_url=author_icon_url)
    elif author and author_icon_url:
      self.ems[-1].set_author(name=author, url=author_icon_url)
    elif author and author_url:
      self.ems[-1].set_author(name=author, icon_url=author_icon_url)
    elif author:
      self.ems[-1].set_author(name=author)
    if footer_text and footer_icon_url:
      self.ems[-1].set_footer(text=footer_text, icon_url=footer_icon_url)
    elif footer_text:
      self.ems[-1].set_footer(text=footer_text)
    await interaction.response.send_message(f"Embed created. {len(self.ems)} in List", ephemeral=True, delete_after=10, view=ButtonView(self.bot, self.ems, self.channel))
    

class sendembeds(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(description="Send up to 10 fully customizable Embeds")
  async def send_embeds(self, interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.send_modal(EmbedModal1(self.bot, [], channel))

  @send_embeds.error
  async def ticket_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
      await interaction.response.send_message(str(error), ephemeral=True)
    if isinstance(error, app_commands.MissingPermissions or error, app_commands.MissingAnyRole):
      await interaction.response.send_message("You don't have permissions to run this command.")
    

async def setup(bot):
  await bot.add_cog(sendembeds(bot))
