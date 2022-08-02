import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import mysql.connector

load_dotenv()

# client = discord.Client()
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
# adatbazis csatlakoztatasa
mydb = mysql.connector.connect(host=os.getenv('HOST'), user=os.getenv('DBU'), password=os.getenv('DBP'),
                               database=os.getenv('DBN'))
mycursor = mydb.cursor()

# adatok lekerdezese,betoltese memoriaba
mycursor.execute('select users.dcnev,users.dcid,users.pont,users.coin from users')

names, ids, points, coins = [], [], [], []
for item in mycursor:
    names.append(item[0])
    ids.append(item[1])
    points.append(item[2])
    coins.append(item[3])


# userek felvetele
class User:
    def __init__(self, dcnev, dcid, pont, coin):
        self.dcnev = dcnev
        self.dcid = dcid
        self.pont = pont
        self.coin = coin


Users = []
for i in range(len(names)):
    Users.append(User(names[i], ids[i], points[i], coins[i]))


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    global dcID1, dcID2, dcAuthor1, dcAuthor2

    # ellenorzes h a user benne van-e a db-ban,ha nincs akkor hozzaadja
    if message.content.startswith('ping'):
        un = message.author.name
        uid = str(message.author.id)
        if uid not in ids:
            sql = "INSERT INTO users (dcnev, dcid, pont, coin) VALUES (%s, %s, %s, %s)"
            val = (message.author.name, message.author.id, 0, 0)
            mycursor.execute(sql, val)
            mydb.commit()
            names.append(message.author.name)
            ids.append(str(message.author.id))
            points.append(0)
            coins.append(0)
            Users.append(
            User(names[len(names) - 1], ids[len(names) - 1], points[len(names) - 1], coins[len(names) - 1]))

        # kihiv parancs
        if 'kihiv' in message.content:
            nev = message.content[11:]
            if nev in names:
                i = names.index(nev)  # idx
                # await message.channel.send(f'<@{message.author.id}> kihívott téged, <@{Users[idx].dcid}>')
                embed = discord.Embed(title="Kihívtak!", color=0x020053,
                                      description=f'<@{message.author.id}> kihívott téged, <@{Users[i].dcid}>')
                embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/sport-8/70/ping_pong-512.png")
                # await message.channel.send(embed=embed)
                userDM = await client.fetch_user(Users[i].dcid)
                dcID1 = message.author.id
                dcID2 = Users[i].dcid
                #dcAuthor1 = message.author
                await message.reply('Kihívás elküldve!')
                #print(message.author)
                await userDM.send(embed=embed)

        # Elfogad (kihívás)
    if 'elfogad' in message.content:
        userDM = await client.fetch_user(dcID1)
        embed = discord.Embed(title='Kihívás elfogadva!', color=0x025300,
                              description=f'<@{dcID2}> elfogadta a kihívást!')
        embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/sport-8/70/ping_pong-512.png")
        await userDM.send(embed=embed)
        #dcAuthor2 = message.author
        #print(dcAuthor2)
    elif 'elutasit' in message.content:
        userDM = await client.fetch_user(dcID1)
        embed = discord.Embed(title='Kihívás elutasítva!', color=0x530200,
                              description=f'<@{dcID2}> nem fogadta el a kihívást!')
        embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/sport-8/70/ping_pong-512.png")
        await userDM.send(embed=embed)

        # match parancs
        if 'match' in message.content:
            await message.channel.send('Eredmeny')

client.run(os.getenv('TOKEN'))
