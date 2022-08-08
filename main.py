import discord
from discord.ui import Button, View
import os
from dotenv import load_dotenv
import datetime
import mysql.connector
import time

load_dotenv()
# client = discord.Client() only with discord.py
# pycord-hoz
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
client = discord.Client(intents=intents)

# adatbazis csatlakoztatasa
mydb = mysql.connector.connect(host=os.getenv('HOST'), user=os.getenv('DBU'), password=os.getenv('DBP'), database=os.getenv('DBN'))
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
    global dcID1, dcID2, tID, channel
    guild = message.guild

    if message.author == client.user:
        return

    # ellenorzes h a user benne van-e a db-ban,ha nincs akkor hozzaadja,es a memoriaba is betolti
    if message.content.startswith('ping'):
        uid = message.author.id
        if uid not in ids:
            sql = "INSERT INTO users (dcnev, dcid, pont, coin) VALUES (%s, %s, %s, %s)"
            val = (message.author.name, message.author.id, 0, 0)
            mycursor.execute(sql, val)
            mydb.commit()
            names.append(message.author.name)

            ids.append(message.author.id)
            points.append(0)
            coins.append(0)
            Users.append(User(names[len(names) - 1], ids[len(names) - 1], points[len(names) - 1], coins[len(names) - 1]))

        # kihiv parancs
        if 'kihiv' in message.content:
            nev = message.content[11:]
            if nev in names:
                i = names.index(nev)  # memoriaban levo userek szama (idx - Zolinak ;) )
                embed = discord.Embed(title="Kihívtak!", color=0x020053, description=f'<@{message.author.id}> kihívott téged, <@{Users[i].dcid}>')
                dcID2 = Users[i].dcid
                embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/sport-8/70/ping_pong-512.png")
                
                acceptb = Button(label="Accept", style=discord.ButtonStyle.green, custom_id="acceptb")
                declineb = Button(label="Decline", style=discord.ButtonStyle.red, custom_id="declineb")

                async def accept(interaction):
                    acceptb.disabled = True
                    acceptb.label = "Accepted"
                    view.remove_item(declineb)

                    # Thread létrehozása
                    channel = client.get_channel(1004010609509150771)  # channel id here
                    message = await channel.send(f'<@{dcID1}> VS <@{dcID2}>') # Thread start message
                    await message.create_thread(name="Ping-Pong", auto_archive_duration=60) # Thread létrehozása
                    tid = message.thread.id # Thread ID

                    await interaction.response.edit_message(view=view)
                    userDM = await client.fetch_user(dcID1) # user konvertálás (címzett)
                    authorNev = await client.fetch_user(dcID2) # user konvertálás (author)
                    embed = discord.Embed(title='Kihívás elfogadva!', color=0x025300,
                                          description=f'<@{dcID2}> elfogadta a kihívást!')
                    embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/sport-8/70/ping_pong-512.png")

                    guild_id = guild.id # server ID lekérdezés
                    server = client.get_guild(guild_id)
                    role_id = 1004009190215405619  # Kihívott rang ID
                    role = discord.utils.get(server.roles, id=role_id) # server role lekérdezés
                    member = await guild.fetch_member(dcID2) # member konvertálás
                    await member.add_roles(role) # role kiosztása
                    await userDM.send(embed=embed)
                    
                async def decline(interaction):
                    declineb.disabled = True
                    declineb.label = "Declined"
                    view.remove_item(acceptb)
                    await interaction.response.edit_message(view=view)
                    userDM = await client.fetch_user(dcID1)
                    
                    authorNev = await client.fetch_user(dcID2) # user konvertálás (author)
                    embed = discord.Embed(title='Kihívás elutasítva!', color=0x530200, description=f'<@{dcID2}> nem fogadta el a kihívást!')
                    embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/sport-8/70/ping_pong-512.png")
                    server = client.get_guild(guild_id)
                    role_id = 1004010127520706590  # Kihívó ID
                    role2 = discord.utils.get(server.roles, id=role_id)
                    await message.author.remove_roles(role2) # leveszi a kihívó role-t
                    await userDM.send(embed=embed)

                acceptb.callback = accept
                declineb.callback = decline

                view = View()
                view.add_item(acceptb)
                view.add_item(declineb)

                # await message.channel.send(embed=embed)
                userDM = await client.fetch_user(Users[i].dcid)
                dcID1 = message.author.id

                guild_id = guild.id
                role_id = 1004010127520706590  # Kihívó ID
                role = guild.get_role(role_id)
                await message.author.add_roles(role) # A kihívó ID hozzáadása
                if not discord.utils.get(message.author.roles, id=role_id): # Ha nincs az authornak ilyen role-ja
                    await message.author.add_roles(role)
                await message.reply('Kihívás elküldve!')
                await userDM.send(embed=embed, view=view)

    if type(message.channel) == discord.threads.Thread: # Ha a message a pongbot channel-ben van
        if message.content.startswith('ping'):
            if 'datum' in message.content:
                dbmidtmp1 = str(datetime.date.today()).split('-')
                dbmidtmp2 = f"{str(dbmidtmp1[0])[2:]}{dbmidtmp1[1]}{dbmidtmp1[2]}"
                #datumT = str(message.content).split()
                mycursor.execute('select count(id) from matches where id like "' + dbmidtmp2 + '%"')

                for item in mycursor:
                    i = item

                j = i[0]
                j += 1
                dbmid = f"{dbmidtmp2}{j}"

                # https://decomaan.github.io/google-calendar-link-generator/
                # https://www.google.com/calendar/render?action=TEMPLATE&text=Ping+Pong&details=Hell%C3%B3&location=%C5%B0r&dates=20220808T201100Z%2F20220823T201100Z

                #calendarTitle = 'Ping-Pong'
                #startDate = datumT[2]
                #endDate = datumT[3]
                #location = datumT[4]
                await message.channel.send(dbmid)
                print(message.channel.id, message.thread)

                if 'rogzit' in message.content:
                    thread = client.get_channel(message.channel.id)
                    await message.channel.send('Sikeres rögzítés!, a thread 10 másodpercen belül tőrlődik.')
                    time.sleep(10)
                    await thread.delete()

client.run(os.getenv('TOKEN'))