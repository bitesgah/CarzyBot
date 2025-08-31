from discord.ext import commands, tasks
import requests, re, json

def load_data():
  with open("jsons/notify.json", "r") as f:
    return json.load(f)

def save_data(data):
  with open("jsons/notify.json", "w") as f:
    json.dump(data, f, indent=2)


class ytnot(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.check.start()


  @tasks.loop(seconds=60)
  async def check(self):
    notificationData = load_data()
    if not "ytnotify" in notificationData:
      return
    for youtube_channel in notificationData["ytnotify"]:
      ytchannel = notificationData["ytnotify"][youtube_channel]['channel_name']
      print(f"Now Checking For {ytchannel}")
      channel = f"https://www.youtube.com/channel/{youtube_channel}"

      html = requests.get(channel + "/videos").text

      try:
        latestvideourl = "https://www.youtube.com/watch?v=" + re.search(
          '(?<="videoId":").*?(?=")', html).group()
      except:
        continue

      if not str(notificationData["ytnotify"][youtube_channel]
                 ["latestvideourl"]) == latestvideourl:
        notificationData["ytnotify"][str(
          youtube_channel)]['latestvideourl'] = latestvideourl
        discord_channel_id = notificationData['notifyingchannel']
        discord_channel = self.bot.get_channel(int(discord_channel_id))

        if "ytnotrole" in notificationData:
          mention = f"<@&{notificationData['ytnotrole']}>"
        else:
          mention = "@everyone"
        await discord_channel.send(
          f"{mention} Checkt das neueste Video ab[!]({latestvideourl})"
        )

    save_data(notificationData)


async def setup(bot):
  await bot.add_cog(ytnot(bot))