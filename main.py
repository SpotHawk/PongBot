import discord
from discord.ui import Button,View
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

#client = discord.Client() only with discord.py
#pycord-hoz
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

#adatbazis csatlakoztatasa
mydb = mysql.connector.connect(host=os.getenv('HOST'),user=os.getenv('DBU'),password=os.getenv('DBP'),database=os.getenv('DBN'))
mycursor=mydb.cursor()

#adatok lekerdezese,betoltese memoriaba
mycursor.execute('select users.dcnev,users.dcid,users.pont,users.coin from users')

names,ids,points,coins=[],[],[],[]
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

    #ellenorzes h a user benne van-e a db-ban,ha nincs akkor hozzaadja,es a memoriaba is betolti
    if message.content.startswith('ping'):
        uid=str(message.author.id)
        if uid not in ids:
            sql = "INSERT INTO users (dcnev, dcid, pont, coin) VALUES (%s, %s, %s, %s)"
            val = (message.author.name, message.author.id, 0,0)
            mycursor.execute(sql, val)
            mydb.commit()
            names.append(message.author.name)
            ids.append(str(message.author.id))
            points.append(0)
            coins.append(0)
            Users.append(User(names[len(names)-1],ids[len(names)-1],points[len(names)-1],coins[len(names)-1]))

        #kihiv parancs
        if 'kihiv' in message.content:
            nev = message.content[11:]

            if nev in names:
                i=names.index(nev)

                acceptb = Button(label="Accept", style=discord.ButtonStyle.green, custom_id="acceptb")
                declineb = Button(label="Decline", style=discord.ButtonStyle.red, custom_id="declineb")

                async def accept(interaction):
                    acceptb.disabled = True
                    acceptb.label = "Accepted"
                    view.remove_item(declineb)
                    await interaction.response.edit_message(view=view)
                async def decline(interaction):
                    declineb.disabled = True
                    declineb.label = "Declined"
                    view.remove_item(acceptb)
                    await interaction.response.edit_message(view=view)

                acceptb.callback=accept
                declineb.callback=decline

                view=View()
                view.add_item(acceptb)
                view.add_item(declineb)
                
                await message.channel.send(f'<@{message.author.id}> kihívott téged, <@{Users[i].dcid}>', view=view)

        #match parancs
        if 'match' in message.content:
            await message.channel.send('Eredmeny')

client.run(os.getenv('TOKEN'))