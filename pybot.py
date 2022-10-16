import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get
from config import TOKEN

import asyncio
import randomco
import time
import pymongo
from pymongo import MongoClient

import dbl

client = commands.AutoShardedBot(shard_count=2, command_prefix = '-', intents = intents)

#token = 'discordBotToken' 
#mongoClusterKey0 = 'MongoDB Cluster Key'

#cluster0 = MongoClient(mongoClusterKey0)
#db = cluster0['hearhear-bot']

l = {}      #timer trigger library
t = {}      #reminder storage library

#TopGG_Token = 'TopGG Token'
#dbl.DBLClient(client, TopGG_Token, autopost=True) # Autopost will post your guild count every 30 minutes

@client.event
async def on_ready():
    print('Bot Activated!\n')
    print(f'Logged in as {client.user.name}\n')
    print('------------------------------\n')
    act = f'debates in {len(client.guilds)} servers [.help]'
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

    # while True:
    #     await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=act))
    #     await asyncio.sleep(1800)

@bot.tree.command(name="t")
@app_commands.describe(time="How many minutes?")
async def t(interaction: discord.Interaction, time):
    await interaction.response.send_message(f"{interaction.user.name} set the timer for {time} minutes!")

client.run(TOKEN)