import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get
#from config import TOKEN

from boto.s3.connection import S3Connection
import html
import requests
import re
import asyncio
import random
import time
# import pymongo
# from pymongo import MongoClient

#import db

#client = commands.Bot(command_prefix=".", intents=discord.Intents.all())

client = commands.AutoShardedBot(shards=2, command_prefix = '-', intents=discord.Intents.default())

#token = 'discordBotToken' 
#mongoClusterKey0 = 'MongoDB Cluster Key'

#cluster0 = MongoClient(mongoClusterKey0)
#db = cluster0['hearhear-bot']

#TopGG_Token = 'TopGG Token'
#dbl.DBLClient(client, TopGG_Token, autopost=True) # Autopost will post your guild count every 30 minutes

@client.event
async def on_ready():
    print('Bot Activated!\n')
    print('------------------------------\n')
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
    while True:
        act = f'debates in {len(client.guilds)} servers'
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=act))
        await asyncio.sleep(1800)

@client.tree.command(name="ping",description="Checks response time between client and Hear Hear! bot.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pinged in {round(client.latency*1000)} ms.")

# @client.tree.command(name="about",description="About the Hear! Hear! bot.")
# async def about(interaction: discord.Interaction):
#     await interaction.response.send_message("WIP")

@client.tree.command(name="commands",description="Lists commands for the Hear Hear bot.")
async def commands(interaction: discord.Interaction):
    embed = discord.Embed()
    embed.title = "List of Commands for the Hear! Hear! Bot"
    embed.set_image(url="https://i.imgur.com/7Lw4CRt.gif")
    embed.description = f"""
`/ping`
Checks response time between client and Hear Hear! bot.

`/commands`
Displays list of commands.

`/coinflip`
Randomly chooses between heads and tails. Useful for vetoes.

`/getmotion`
Displays a random motion from the hellomotions motion bank.

`/time`
Times a speech with format *XmYs*, e.g. *7m*, *5m30s*, *30s*.
"""
    #embed.set_footer(text="Message <@704206757681037362> or <@696777012110688296> for technical help.",icon_url="https://i.imgur.com/RaQy5so.png")
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="getmotion",description="Displays a random motion from the hellomotions motion bank.")
async def getmotion(interaction: discord.Interaction):
    req = requests.get("https://hellomotions.com/random-motion")
    body = req.text.split("<b>")
    motion = html.unescape((body[1].split("</b"))[0])
    await interaction.response.send_message(f"{motion}")

@client.tree.command(name="coinflip",description="Chooses between heads and tails, useful for vetoes")
async def coinflip(interaction: discord.Interaction):
    coin = ["Head", "Tail"]
    await interaction.response.send_message(f"The coin shows **{random.choice(coin)}**!")

class Timer(discord.ui.View):
    def __init__(self,mins,secs):
        super().__init__()
        self.mins = mins
        self.secs = secs
        self.paused = False
        self.stopped = False
        self.time1 = int(mins)*60 + int(secs)
        self.time2 = self.time1
        self.time3 = 0
        self.buttonPause = discord.ui.Button(label="Pause ✋", style=discord.ButtonStyle.grey)
        self.buttonStop = discord.ui.Button(label="Stop Timer 🛑", style=discord.ButtonStyle.blurple)

    async def time(self, interaction):
        msg = interaction.message
        
        if interaction.response.is_done():
            await msg.edit(view=self)
        else:
            await interaction.response.edit_message(view=self)

        n = float(1)
        while self.time2 >= 0 and not self.paused and not self.stopped:
            await msg.edit(content=f"⏳ **Timer**   `{str(int(self.time2/60)).zfill(2)} : {str(self.time2%60).zfill(2)}`")
            j = self.time2%5
            if j:
                self.time2 -= j
                self.time3 += j
                await msg.edit(content=f"⏳ **Timer**   `{str(int(self.time2/60)).zfill(2)} : {str(self.time2%60).zfill(2)}`")
            await asyncio.sleep(4+float(n))
            self.time2 -= 5
            self.time3 += 5
            if self.time3 == 60:
                await interaction.channel.send(f"\n\n🟢  **1 minute done!** {interaction.user.mention}")
            if self.time2 == 60:
                await interaction.channel.send(f"\n\n🟠  **1 minute left!** {interaction.user.mention}")
            if self.time2 == 0:
                self.buttonPause.disabled = True
                self.buttonStop.disabled = True
                await msg.edit(content="Timer stopped! Use `/time` to start a new timer.",view=self)
                await interaction.channel.send(f"\n\n🔴  **Time's up!** {interaction.user.mention}")
    

    @discord.ui.button(label="Start Timer ⏱️", style=discord.ButtonStyle.green)
    async def buttonStart(self, interaction: discord.Interaction, button: discord.ui.Button):

        async def pause(interaction: discord.Interaction):
            self.buttonStop.disabled = not self.buttonStop.disabled
            self.paused = not self.paused
            if self.paused:
                self.buttonPause.label = "Resume 👍"
                if interaction.response.is_done():
                    await interaction.message.edit(content=f"⏸️   **PAUSED**   `{str(int(self.time2/60)).zfill(2)} : {str(self.time2%60).zfill(2)}`",view=self)
                else:
                    await interaction.response.edit_message(content=f"⏸️  **PAUSED**   `{str(int(self.time2/60)).zfill(2)} : {str(self.time2%60).zfill(2)}`",view=self)
            if not self.paused:
                self.buttonPause.label = "Pause ✋"
                await self.time(interaction)              
        async def stop(interaction: discord.Interaction):
            self.buttonPause.disabled = True
            self.buttonStop.disabled = True
            self.stopped = True
            await interaction.response.edit_message(content="Timer stopped! Use `/time` to start a new timer.",view=self)
        self.buttonPause.callback = pause
        self.buttonStop.callback = stop
        button.disabled = True
        self.add_item(self.buttonPause)
        self.add_item(self.buttonStop)
        await self.time(interaction)

@client.tree.command(name="time", description="Times a debate speech.")
@app_commands.describe(time="Specify time using format XmYs or Ym, where X=minutes and Y=seconds e.g. 7m15s or 7m")
async def timer(interaction: discord.Interaction, time: str):
    pattern = re.compile("^([0-9]{1,2}m[0-9]{1,2}s)|([0-9]{1,2}m)|([0-9]{1,2}s)$")
    if not re.match(pattern, time):
        await interaction.response.send_message("Invalid syntax! Please use the format `XmYs`, e.g. `7m15s`.")
        return

    time = time.split("m")
    if len(time)==2:
        mins = time[0].zfill(2)
        secs = time[1][:-1].zfill(2)
    else:
        mins = "00"
        secs = time[0][:-1].zfill(2)


    await interaction.response.send_message(f"⏳ **Timer**   `{mins} : {secs}`", view=Timer(mins,secs))

client.run(S3Connection(os.environ['TOKEN']))