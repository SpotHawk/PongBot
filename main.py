import discord
import os
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!ping'):
        await message.channel.send('Hello!')

    if message.content.startswith('ping kihiv '):
        await message.channel.send('Kit akarsz kihívni?')

client.run(os.getenv('TOKEN'))