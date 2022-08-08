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
    global dcID1, dcID2, tID, channel, bo3
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

        # result parancs
        if 'result' in message.content:
            #match id generalasa datum,es az aznapi meccsek alapjan (idopont parancshoz)
            #dbmidtmp1=str(datetime.date.today()).split('-')
            #dbmidtmp2=f"{str(dbmidtmp1[0])[2:]}{dbmidtmp1[1]}{dbmidtmp1[2]}"
            #mycursor.execute('select count(id) from matches where id like "'+dbmidtmp2+'%"')
            #for item in mycursor:
            #    i=item
            #j=i[0]
            #j+=1
            #dbmid=f"{dbmidtmp2}{j}"

            #feltoltes a db-be
            #sql = "INSERT INTO matches (id,player_1,player_2, gyoztes, vesztes, eredmeny) VALUES (%s, %s, %s, %s, %s, %s)"
            #val = (dbmid, Users[0].dcid, Users[1].dcid,0,0,"11-9")
            #mycursor.execute(sql, val)
            #mydb.commit()

            msg=str(message.content).split(' ')
            mid = msg[2]
            score= str(msg[3]).split('-')
            p1s=score[0]
            p2s=score[1]

            #meccs ell. h letezik-e
            mycursor.execute('select id from matches')
            for item in mycursor:
                i = item
            if mid not in i:
                await message.channel.send("Nincs ilyen match ID!")
            else:
                mycursor.execute('select eredmeny from matches where id='+mid)
                for item in mycursor:
                    vaneres=item[0]
                if vaneres=='':
                    mycursor.execute('select player_1,player_2 from matches where id='+mid)
                    for item in mycursor:
                        players=item
                    if int(players[0]) == message.author.id or int(players[1]) == message.author.id:
                        for item in Users:
                            if item.dcid==int(players[0]):
                                player_1=item.dcnev
                            if item.dcid==int(players[1]):
                                player_2=item.dcnev

                        matchEmbed = discord.Embed(title=f"Match rögzítés\tID: {mid}", description="Lejátszott meccs eredményének bevitele", color=0xfc0398)
                        matchEmbed.add_field(name="Player 1", value=f"```{p1s}```", inline=True)
                        matchEmbed.add_field(name="Player 2", value=f"```{p2s}```", inline=True)
                        matchEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1002233930264608858/1004043886999638076/scoreboard.png")
                        bo3b = Button(label="BO3", style=discord.ButtonStyle.grey, custom_id="bo3")
                        p1 = Button(label=f"{player_1}", custom_id="play1")
                        p2 = Button(label=f"{player_2}", custom_id="play2")
                        sendb = Button(label="Send", style=discord.ButtonStyle.primary, custom_id="send")

                        view = View()
                        view.add_item(bo3b)
                        view.add_item(p1)
                        view.add_item(p2)
                        view.add_item(sendb)

                        async def bo3s(interaction):
                            if bo3b.style == discord.ButtonStyle.grey:
                                bo3b.style = discord.ButtonStyle.green
                            else:
                                bo3b.style = discord.ButtonStyle.grey
                            await interaction.response.edit_message(view=view)

                        async def winnerselect1(interaction):
                            if p1.style == discord.ButtonStyle.grey:
                                p1.style = discord.ButtonStyle.green
                                p1.emoji = "🥇"
                                p2.style = discord.ButtonStyle.blurple
                                p2.emoji = "🥈"
                            elif p1.style == discord.ButtonStyle.blurple:
                                p1.style = discord.ButtonStyle.green
                                p1.emoji = "🥇"
                                p2.style = discord.ButtonStyle.blurple
                                p2.emoji = "🥈"
                            await interaction.response.edit_message(view=view)

                        async def winnerselect2(interaction):
                            if p2.style == discord.ButtonStyle.grey:
                                p2.style = discord.ButtonStyle.green
                                p2.emoji = "🥇"
                                p1.style = discord.ButtonStyle.blurple
                                p1.emoji = "🥈"
                            elif p2.style == discord.ButtonStyle.blurple:
                                p2.style = discord.ButtonStyle.green
                                p2.emoji = "🥇"
                                p1.style = discord.ButtonStyle.blurple
                                p1.emoji = "🥈"
                            await interaction.response.edit_message(view=view)

                        async def submit(interaction):
                            bo3b.disabled = True
                            p1.disabled = True
                            p2.disabled = True

                            if bo3b.style == discord.ButtonStyle.green:
                                bo3 = True
                            else:
                                bo3 = False

                            if p1.style == discord.ButtonStyle.green:
                                sql = "UPDATE matches set gyoztes=%s,vesztes=%s,eredmeny=%s,bo3=%s where id=%s"
                                val = (players[0], players[1], msg[3], bo3, mid)
                                mycursor.execute(sql, val)
                                mydb.commit()
                            elif p2.style == discord.ButtonStyle.green:
                                sql = "UPDATE matches set gyoztes=%s,vesztes=%s,eredmeny=%s,bo3=%s where id=%s"
                                val = (players[1], players[0], msg[3], bo3, mid)
                                mycursor.execute(sql, val)
                                mydb.commit()
                            await interaction.response.edit_message(view=view)

                        bo3b.callback = bo3s
                        p1.callback = winnerselect1
                        p2.callback = winnerselect2
                        sendb.callback = submit

                        await message.channel.send(embed=matchEmbed, view=view)
                    else:
                        await message.reply("Nincs jogosultságod, mivel ez nem a te meccsed volt!")
                else:
                    await message.reply("Ehhez a meccshez már megadták az eredményt, ha módosítani szeretnél akkor az 'edit' parancsot használdd!")

        # edit parancs
        if 'edit' in message.content:
            # beirt parancs szetbontasa
            msg = str(message.content).split(' ')
            mid = msg[2]
            score = str(msg[3]).split('-')
            p1s = score[0]
            p2s = score[1]

            # meccs ell. h letezik-e
            mycursor.execute('select id from matches')
            for item in mycursor:
                i = item
            if mid not in i:
                await message.channel.send("Nincs ilyen match ID!")
            else:
                #meccs jatekosainak lekerese
                mycursor.execute('select player_1,player_2 from matches where id=' + mid)
                playerids=[]
                players=[]
                for item in mycursor:
                    playerids.append(int(item[0]))
                    playerids.append(int(item[1]))
                for item in Users:
                    if item.dcid==message.author.id:
                        player_1=item
                    if item.dcid in playerids:
                        if item.dcid!=message.author.id:
                            player_2=item

                # kerelmi embed letrehozasa
                embed = discord.Embed(title="Módosítási kérelem", color=0x020053, description=f'<@{player_1.dcid}> módosítani szeretné, a ID: {mid} meccset!')
                embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/sport-8/70/ping_pong-512.png")

                # kerelmi embed gombjainak letrehozasa
                acceptb = Button(label="Accept", style=discord.ButtonStyle.green, custom_id="acceptb")
                declineb = Button(label="Decline", style=discord.ButtonStyle.red, custom_id="declineb")

                async def accept(interaction):
                    acceptb.disabled = True
                    acceptb.label = "Accepted"
                    view.remove_item(declineb)
                    await interaction.response.edit_message(view=view)
                    userDM = await client.fetch_user(player_1.dcid)
                    embed = discord.Embed(title='Módosítási kérelem elfogadva!', color=0x025300,
                                          description=f'<@{player_2.dcid}> elfogadta a kérelmet!')
                    embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/sport-8/70/ping_pong-512.png")
                    await userDM.send(embed=embed)
                    matchEmbed = discord.Embed(title=f"Match módosítása\tID: {mid}", description="Lejátszott meccs eredményének módosítása", color=0x5865F2)
                    matchEmbed.add_field(name="Player 1", value=f"```{p1s}```", inline=True)
                    matchEmbed.add_field(name="Player 2", value=f"```{p2s}```", inline=True)
                    matchEmbed.set_thumbnail(url="https://img.icons8.com/ios-glyphs/30/FFFFFF/edit--v1.png")
                    bo3b = Button(label="BO3", style=discord.ButtonStyle.grey, custom_id="bo3")
                    p1 = Button(label=f"{player_1.dcnev}", custom_id="play1")
                    players.append(player_1.dcid)
                    p2 = Button(label=f"{player_2.dcnev}", custom_id="play2")
                    players.append(player_2.dcid)
                    sendb = Button(label="Send", style=discord.ButtonStyle.primary, custom_id="send")

                    view2 = View()
                    view2.add_item(bo3b)
                    view2.add_item(p1)
                    view2.add_item(p2)
                    view2.add_item(sendb)

                    async def bo3s(interaction):
                        if bo3b.style == discord.ButtonStyle.grey:
                            bo3b.style = discord.ButtonStyle.green
                        else:
                            bo3b.style = discord.ButtonStyle.grey
                        await interaction.response.edit_message(view=view2)

                    async def winnerselect1(interaction):
                        if p1.style == discord.ButtonStyle.grey:
                            p1.style = discord.ButtonStyle.green
                            p1.emoji = "🥇"
                            p2.style = discord.ButtonStyle.blurple
                            p2.emoji = "🥈"
                        elif p1.style == discord.ButtonStyle.blurple:
                            p1.style = discord.ButtonStyle.green
                            p1.emoji = "🥇"
                            p2.style = discord.ButtonStyle.blurple
                            p2.emoji = "🥈"
                        await interaction.response.edit_message(view=view2)

                    async def winnerselect2(interaction):
                        if p2.style == discord.ButtonStyle.grey:
                            p2.style = discord.ButtonStyle.green
                            p2.emoji = "🥇"
                            p1.style = discord.ButtonStyle.blurple
                            p1.emoji = "🥈"
                        elif p2.style == discord.ButtonStyle.blurple:
                            p2.style = discord.ButtonStyle.green
                            p2.emoji = "🥇"
                            p1.style = discord.ButtonStyle.blurple
                            p1.emoji = "🥈"
                        await interaction.response.edit_message(view=view2)

                    async def submit(interaction):
                        bo3b.disabled = True
                        p1.disabled = True
                        p2.disabled = True

                        if bo3b.style==discord.ButtonStyle.green:
                            bo3=True
                        else:
                            bo3=False

                        if p1.style == discord.ButtonStyle.green:
                            sql = "UPDATE matches set gyoztes=%s,vesztes=%s,eredmeny=%s,bo3=%s where id=%s"
                            val = (players[0], players[1], msg[3], bo3, mid)
                            mycursor.execute(sql, val)
                            mydb.commit()
                        elif p2.style == discord.ButtonStyle.green:
                            sql = "UPDATE matches set gyoztes=%s,vesztes=%s,eredmeny=%s,bo3=%s where id=%s"
                            val = (players[1], players[0], msg[3], bo3, mid)
                            mycursor.execute(sql, val)
                            mydb.commit()
                        await interaction.response.edit_message(view=view2)

                    bo3b.callback = bo3s
                    p1.callback = winnerselect1
                    p2.callback = winnerselect2
                    sendb.callback = submit
                    await message.channel.send(embed=matchEmbed, view=view2)  # !!

                async def decline(interaction):
                    declineb.disabled = True
                    declineb.label = "Declined"
                    view.remove_item(acceptb)
                    await interaction.response.edit_message(view=view)
                    userDM = await client.fetch_user(player_1.dcid)
                    embed = discord.Embed(title='Módosítási kérelem elutasítva!', color=0x530200,
                                          description=f'<@{player_2.dcid}> nem fogadta el a kérelmet!')
                    embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/sport-8/70/ping_pong-512.png")
                    await userDM.send(embed=embed)

                acceptb.callback = accept
                declineb.callback = decline

                view = View()
                view.add_item(acceptb)
                view.add_item(declineb)

                userDM = await client.fetch_user(player_2.dcid)
                await message.reply('Módosítási kérelem elküldve!')
                await userDM.send(embed=embed, view=view)

        # help parancs
        if 'help' in message.content:
            embedVar = discord.Embed(title="Help", description="PongBot parancsok", color=0xffffff)
            embedVar.add_field(name="`ping kihiv {username}`", value="Kihívja a kért játékost", inline=False)
            embedVar.add_field(name="`ping result {matchID} {sco-re}`", value="A megadott meccshez lehet adatokat felvinni (eredmény,győztes,vesztes,bo3 volt-e)\nA gombokon lévő két player közül "
                                                                              "ki kell választani a győztest, megadhatjuk azt is h a meccs BO3 volt a BO3 gomb segítségével, majd érvényesíteni kell "
                                                                              "a send gombbal",inline=False)
            embedVar.add_field(name="`ping edit {matchID} {sco-re}`", value="Meccs adat módosítási kérelmet küld", inline=False)
            embedVar.add_field(name="`ping features`", value="Kiírja a PongBot várható újdonságait ", inline=False)
            embedVar.set_footer(text="Egyes parancsok használatba vétele előtt lehetséges hogy kell legalább egy 'ping' parancs használata")
            embedVar.set_thumbnail(url="https://cdn.pixabay.com/photo/2017/03/17/05/20/info-2150938_960_720.png")
            await message.channel.send(embed=embedVar)

        # features parancs
        if 'features' in message.content:
            embedVar = discord.Embed(title="Features", description="PongBot várható parancsai", color=0xffff00)
            embedVar.add_field(name="`ping leaderboard`", value="Kiírja a játékosok leaderboard-ját", inline=False)
            embedVar.add_field(name="`ping datum {helyszín} {DateTime}`", value="A mecss helyszínének,dátumának bevitele, google remindert készít", inline=False)
            embedVar.add_field(name="`ping history`", value="Kiírja az eddig lejátszott meccseidet", inline=False)
            embedVar.add_field(name="`ping pending`", value="Kiírja a rád váró meccseket", inline=False)
            embedVar.set_thumbnail(url="https://cdn.discordapp.com/attachments/1002233930264608858/1004025300042141826/feature.png")
            await message.channel.send(embed=embedVar)

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