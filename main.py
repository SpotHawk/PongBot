import discord
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

client = discord.Client()

mydb = mysql.connector.connect(host=os.getenv('HOST'),user=os.getenv('DBU'),password=os.getenv('DBP'),database='PRx5iD5O8U')
mycursor=mydb.cursor()

mycursor.execute('select users.dcid from users')

ids=[]
for item in mycursor:
    ids.append(str(item).strip("('',)"))

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
        uid=str(message.author.id)
        if uid not in ids:
            sql = "INSERT INTO users (dcnev, dcid, pont, coin) VALUES (%s, %s, %s, %s)"
            val = (message.author.name, message.author.id, 0,0)
            mycursor.execute(sql, val)
            mydb.commit()
            ids.append(str(message.author.id))
            return
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