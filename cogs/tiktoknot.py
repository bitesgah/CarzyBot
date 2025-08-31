from discord.ext import commands, tasks
import requests, json

def load_data():
    with open("jsons/notify.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("jsons/notify.json", "w") as f:
        json.dump(data, f, indent=2)

def nextApiKey():
    data = load_data()
    if data["currentAPIKey"] == "currentAPIKey1":
        data["currentAPIKey"] = "currentAPIKey2"
    else:
        data["currentAPIKey"] = "currentAPIKey1"
    save_data(data)

def getNewestTiktok():
    data = load_data()
    url = "https://tiktok-scraper7.p.rapidapi.com/user/posts"
    querystring = {"user_id": "7002312330097001478", "count": "1", "cursor": "0"}
    headers = {
        "x-rapidapi-key": data[data["currentAPIKey"]],
        "x-rapidapi-host": "tiktok-scraper7.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        response_data = response.json()
        if "data" in response_data and "videos" in response_data["data"] and len(response_data["data"]["videos"]) > 0:
            newest_vid_id = response_data["data"]["videos"][0]["video_id"]
            author_unique_id = response_data["data"]["videos"][0]["author"]["unique_id"]
            newest_url = f"https://www.tiktok.com/@{author_unique_id}/video/{newest_vid_id}"
            return newest_url
    return None

class ttnot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.check.start()

    @tasks.loop(minutes=30)
    async def check(self):
        notificationData = load_data()
        if "ttnotify" not in notificationData:
            return

        print(f"Checking TikTok")
        latestvideourl = getNewestTiktok()
        if latestvideourl is None:
            print("Failed to fetch the latest TikTok video.")
            return

        if str(notificationData["ttnotify"]["latestvideourl"]) != latestvideourl:
            notificationData["ttnotify"]["latestvideourl"] = latestvideourl
            discord_channel_id = notificationData['notifyingchannel']
            discord_channel = self.bot.get_channel(int(discord_channel_id))

            if "ttnotrole" in notificationData:
                mention = f"<@&{notificationData['ttnotrole']}>"
            else:
                mention = "@everyone"
            
            await discord_channel.send(
                f"{mention} Gönnt euch das neueste TikTok[!]({latestvideourl})"
            )

            save_data(notificationData)

async def setup(bot):
    await bot.add_cog(ttnot(bot))
