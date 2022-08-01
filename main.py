import discord
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

client = discord.Client()

#adatbazis csatlakoztatasa
mydb = mysql.connector.connect(host=os.getenv('HOST'),user=os.getenv('DBU'),password=os.getenv('DBP'),database=os.getenv('DBN'))
mycursor=mydb.cursor()

#adatok lekerdezese,betoltese memoriaba
mycursor.execute('select users.dcnev,users.dcid,users.pont,users.coin from users')

names,ids,points,coins,dpname=[],[],[],[],[]
for item in mycursor:
    names.append(item[0])
    ids.append(item[1])
    points.append(item[2])
    coins.append(item[3])

#userek felvetele
class User:
    def __init__(self, dcnev, dcid, pont, coin):
        self.dcnev = dcnev
        self.dcid = dcid
        self.pont = pont
        self.coin = coin

Users=[]
for i in range(len(names)):
    Users.append(User(names[i],ids[i],points[i],coins[i]))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #ellenorzes h a user benne van-e a db-ban,ha nincs akkor hozzaadja
    if message.content.startswith('ping'):
        un=message.author.name
        uid=str(message.author.id)
        if uid and un not in ids or names:
            sql = "INSERT INTO users (dcnev, dcid, pont, coin) VALUES (%s, %s, %s, %s)"
            val = (message.author.name, message.author.id, 0,0)
            mycursor.execute(sql, val)
            mydb.commit()
            names.append(message.author.name)
            ids.append(str(message.author.id))
            points.append(0)
            coins.append(0)

        #kihiv parancs
        if 'kihiv' in message.content:
            nev = message.content[11:]
            if nev in names:
                i=names.index(nev)
                await message.channel.send(f'<@{message.author.id}> kihívott téged, <@{Users[i].dcid}>')

        #match parancs
        if 'match' in message.content:
            await message.channel.send('Eredmeny')


client.run(os.getenv('TOKEN'))