import discord
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

client = discord.Client()

mydb = mysql.connector.connect(host=os.getenv('HOST'), user=os.getenv('DBU'), password=os.getenv('DBP'),
                               database=os.getenv('DBN'))
mycursor = mydb.cursor()

mycursor.execute('select users.dcid from users')


class Users:
    def __init__(self, dcnev, dcid, pont, coin):
        self.dcnev = dcnev
        self.dcid = dcid
        self.pont = pont
        self.coin = coin


ids = []
for item in mycursor:
    ids.append(str(item).strip("('',)"))
print(ids)


adatokDCNEV, adatokDCID, adatokPONT, adatokCOIN = [], [], [], []
mycursor.execute('SELECT users.dcnev FROM users')
for item in mycursor:
    adatokDCNEV.append(str(item).strip("('',)"))
mycursor.execute('SELECT users.dcid FROM users')
for item in mycursor:
    adatokDCID.append(str(item).strip("('',)"))
mycursor.execute('SELECT users.pont FROM users')
for item in mycursor:
    adatokPONT.append(str(item).strip("('',)"))
mycursor.execute('SELECT users.coin FROM users')
for item in mycursor:
    adatokCOIN.append(str(item).strip("('',)"))

adatok = Users(adatokDCNEV, adatokDCID, adatokPONT, adatokCOIN)
print(adatok.dcnev)
print(adatok.dcid)
print(adatok.pont)
print(adatok.coin)
print(adatok.dcnev[1])
print(type(adatok))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('ping'):
        uid = str(message.author.id)
        if uid not in ids:
            sql = "INSERT INTO users (dcnev, dcid, pont, coin) VALUES (%s, %s, %s, %s)"
            val = (message.author.name, message.author.id, 0, 0)
            mycursor.execute(sql, val)
            mydb.commit()
            ids.append(str(message.author.id))

        if 'kihiv' in message.content:
            nev = message.content[11:]
            if nev in adatok.dcnev:
                await message.channel.send(f'<@{message.author.id}> kihívott téged, <@{adatok.dcid[1]}>')
client.run(os.getenv('TOKEN'))
