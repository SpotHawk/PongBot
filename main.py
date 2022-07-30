import discord
import os
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()

class KihivClass:
    def __init__(self, authorName, authorId, kihivNev, kihivId):
        self.authorName = authorName
        self.authorId = authorId
        self.kihivNev = kihivNev
        self.kihivId = kihivId

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('ping'):
        if 'kihiv' in message.content:
            user1 = message.author.id
            #kihivtomb = [user1, message.author.name, str(232185184739524608), 'SpotHawk']
            kihivott = KihivClass(message.author.id, message.author.name, 'SpotHawk', str(232185184739524608))
            if kihivott.kihivNev in message.content:
                await message.channel.send(f"<@{kihivott.kihivId}>")
            print(message.author.display_name)
        else:
            await message.channel.send('Hello!')

client.run(os.getenv('TOKEN'))