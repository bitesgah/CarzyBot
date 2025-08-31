from discord.ext import commands, tasks
import discord, requests, json

def load_data():
  with open("jsons/notify.json", "r") as f:
    return json.load(f)

def save_data(data):
  with open("jsons/notify.json", "w") as f:
    json.dump(data, f, indent=2)

def checkuser(user):
  with open("jsons/env.json", "r") as f:
    env = json.load(f)
  TwitchSecret = env["TwitchSecret"]
  TwitchClientID = env["TwitchClientID"]
  body = {
      'client_id': TwitchClientID,
      'client_secret': TwitchSecret,
      "grant_type": 'client_credentials'
  }
  r = requests.post('https://id.twitch.tv/oauth2/token', body)
  keys = r.json()
  
  headers = {
      'Client-ID': TwitchClientID,
      'Authorization': 'Bearer ' + keys['access_token']
  }
  
  stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + user, headers=headers)
  stream_data = stream.json()
  
  if len(stream_data['data']) == 1:
    return True
  else:
    return False


class twitchnot(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot
    self.check.start()    

  
  @tasks.loop(seconds=60)
  async def check(self):
    notificationData = load_data()
    if not "twitchnotify" in notificationData:
      return
    for name in notificationData["twitchnotify"]:
      if isinstance(notificationData["twitchnotify"][name], dict):
        print(f"Now Checking For {name}")

        if checkuser(name):
          if notificationData["twitchnotify"][name]["live"] == "false":
            channel = self.bot.get_channel(int(notificationData["notifyingchannel"]))
            if "twitchnotrole" in notificationData:
              mention = f"<@&{notificationData['twitchnotrole']}>"
            else:
              mention = "@everyone"
            await channel.send(f"{mention} {name} ist live auf Twitch!\n https://twitch.tv/{name}")
            notificationData["twitchnotify"][name]["live"] = "true"
            await self.bot.change_presence(activity=discord.Streaming(name='CF Live on Twitch!', url='https://www.twitch.tv/carzyfire'))
        else:
          if notificationData["twitchnotify"][name]["live"] == "true":
            notificationData["twitchnotify"][name]["live"] = "false"
            await self.bot.change_presence(activity=discord.Streaming(name='Brawl Stars', url='https://www.twitch.tv/carzyfire'))

    save_data(notificationData)
          

async def setup(bot):
  await bot.add_cog(twitchnot(bot))