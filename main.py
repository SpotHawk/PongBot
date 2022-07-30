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
        else:
            return

client.run(os.getenv('TOKEN'))