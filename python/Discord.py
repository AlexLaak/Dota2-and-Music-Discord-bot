import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import pickle
import re
import queue
from methods import *

Client = discord.Client() #Initialise Client
client = commands.Bot(command_prefix = "?") #Initialise client bot

namesAndIDs = []
whitelistIDs = []
players = {}
pauseQueue = queue.Queue()
playQueue = queue.Queue()

steamIDremoval = 76561197960265728

async def check_if_playing(message):
    while True:
        if (players[message.server.id].is_playing()):
            pass
        else:
            if (playQueue.empty()):
                break
            elif (pauseQueue.empty() == False):
                print("paused")
                pass
            else:
                voice = client.voice_client_in(message.author.server)
                player = await voice.create_ytdl_player(playQueue.get())
                player.volume = 0.4
                players[message.server.id] = player
                player.start()
                print("swapping song")
        await asyncio.sleep(5)

@client.event
async def on_ready():
    print("Bot is online and connected to Discord") #This will be called when the bot connects to the server
    await client.change_presence(game=discord.Game(name='!commands'))
@client.event
async def on_message(message):

    channel = message.channel.name
    if (channel != "pakettipaskaa"):
        return

    #print(client.get_server('153251390909579264').name)
    print(client.is_voice_connected(message.author.server))

    try:
        namesAndIDs = pickle.load(open("save.p", "rb"))
    except (OSError, IOError):
        namesAndIDs = []
    try:
        whitelistIDs = pickle.load(open("whitelistt.p", "rb"))
    except (OSError, IOError):
        whitelistIDs = []


    if (message.content.upper().startswith("!ADD_ID") and message.author.id not in namesAndIDs):       #ADD ID TO LIST IF USER NOT ALREADY ADDED ONE
        print("Comamnd was given by:")
        print(message.author)
        DotaID = ""
        notFound = True
        for x in range(0,len(message.content)):
            if (message.content[x] == ' ' and notFound):
                notFound = False
                continue
            if (notFound == False):
                DotaID += message.content[x]
        if (len(DotaID) <= 2 or DotaID[0] == ""):
            await client.send_message(message.channel, "Invalid ID!")
        else:
            namesAndIDs.append(DotaID)
            namesAndIDs.append(message.author.id)
        pickle.dump(namesAndIDs, open("save.p", "wb"))

    if (message.content.upper().startswith("!DELETE_ID") and message.author.id in namesAndIDs):
        print("Comamnd was given by:")
        print(message.author)
        namesAndIDs.remove(namesAndIDs[namesAndIDs.index(message.author.id) - 1])
        namesAndIDs.remove(message.author.id)
        pickle.dump(namesAndIDs, open("save.p", "wb"))

    if (message.content.upper().startswith("!WHITELIST")):
        print("Comamnd was given by:")
        print(message.author)
        DotaID = ""
        notFound = True
        for x in range(0, len(message.content)):
            if (message.content[x] == ' ' and notFound):
                notFound = False
                continue
            if (notFound == False):
                DotaID += message.content[x]
        if (len(DotaID) <= 2 or DotaID[0] == ""):
            await client.send_message(message.channel, "Invalid ID!")
        else:
            if (whitelistIDs.__contains__(DotaID) == False):
                    whitelistIDs.append(DotaID)
                    pickle.dump(whitelistIDs, open("whitelistt.p", "wb"))

    if (message.content.upper() == "!PRIZE" ):
        await client.send_message(message.channel, await checkPricePool())

    if (message.content.upper() == "!LIST"):
        try:
            namesAndIDs = pickle.load(open("save.p", "rb"))
        except (OSError, IOError):
            namesAndIDs = []
        try:
            whitelistIDs = pickle.load(open("whitelistt.p", "rb"))
        except (OSError, IOError):
            whitelistIDs = []
        print("Comamnd was given by:")
        print(message.author)
        print(whitelistIDs)
        await client.send_message(message.channel, namesAndIDs)  # print list of names

    if (message.content.upper() == "!ME"):
        print("Comamnd was given by:")
        print(message.author)
        await queryProfile(message.author.id,message,client)

    if (message.content.upper().startswith("!PROFILE")):
        print("Comamnd was given by:")
        print(message.author)
        DotaID = ""                                                         #For parsing ID from message
        notFound = True
        for x in range(0, len(message.content)):
            if (message.content[x] == ' ' and notFound):
                notFound = False
                continue
            if (notFound == False):
                DotaID += message.content[x]
        if (len(DotaID) <= 2 or DotaID[0] == ""):
            await client.send_message(message.channel, "Invalid ID!")       #-----
        else:
            if (len(DotaID) >= 16):
                DotaID = int(DotaID) - steamIDremoval
                DotaID = str(DotaID)
                print(DotaID)
            await queryProfileNoAuth(message, client, DotaID)

    if (message.content.upper() == "!LASTMATCHPLAYERS"):
        await queryLastMatch(message.author.id, message, client)

    if (message.content.upper().startswith("!PW") and message.author.id in namesAndIDs):
        DotaID = ""
        notFound = True

        if (len(message.content) >= 48):
            DotaID = str(re.findall('\d+', message.content)[0])
            print(DotaID)

        if (len(DotaID) < len(message.content)):
            message.content = DotaID

        for x in range(0, len(message.content)):
            if (message.content[x] == ' ' and notFound):
                notFound = False
                continue
            if (notFound == False):
                DotaID += message.content[x]
        if (len(DotaID) <= 2 or DotaID[0] == ""):
            await client.send_message(message.channel, "Invalid ID!")
        else:
            if (len(DotaID) >= 16):
                DotaID = int(DotaID) - steamIDremoval
                DotaID = str(DotaID)
                print(DotaID)
            await playedWith(message.author.id,message,client,DotaID)

    if (message.content.upper() == "!LASTMATCH" or message.content.upper() == "!LM"):
        ID = await getProfileID(message.author.id)
        if (ID == "None"):
            await client.send_message(message.channel, "No ID set!")
            return
        await playedWithLastGame(await queryHelper(message.author.id),ID, message, client)

    if (message.content.upper() == "!COMMANDS" or message.content.upper() == "!HELP"):
        print("Comamnd was given by:")
        print(message.author)
        await client.send_message(message.channel, "List of commands:"
                                                   "\n```!add_id <dotaID>"              
                                                   "\n!delete_id"
                                                   "\n!list"
                                                   "\n!me"
                                                   "\n!pw <dotaID/steam64>"
                                                   "\n!sounds"
                                                   "\n!profile <dotaID/steam64>"
                                                   "\n!lastmatch"
                                                   "\n!lastmatchplayers"   
                                                   "\n!prize```")
    if (message.content.upper() == "!SOUNDS"):
        print("Comamnd was given by:")
        print(message.author)
        await client.send_message(message.channel, "List of sound commands:"
                                                    "\n```!summon"
                                                    "\n!leave"
                                                    "\n!joni"
                                                    "\n!joni2"
                                                    "\n!joni3"
                                                    "\n!jonisekoo"
                                                    "\n!jafar"
                                                    "\n!enigma"
                                                    "\n!clasu"
                                                    "\n!kivääri"
                                                    "\n!hävitty"
                                                    "\n!marko1"
                                                    "\n!marko2"
                                                    "\n!marko3"
                                                    "\n!lehtone"
                                                    "\n!lehtone1"
                                                    "\n!muija"
                                                    "\n!oliivi"
                                                    "\n!ismo1"
                                                    "\n!ismo2"
                                                    "\n!sandstorm"
                                                    "\n!höpsit"
                                                    "\n!sinnemeni"
                                                    "\n!grilli" 
                                                    "\n!leivät"
                                                    "\n!siellä"
                                                    "\n!mötkö"
                                                    "\n!kuvaa"
                                                    "\n!aaa"
                                                    "\n!siika"
                                                    "\n!ota"
                                                    "\n!terve"
                                                    "\n!aamupala"
                                                    "\n!enigma```")

            #############SOUNDS###########
    if (message.content.upper() == "!AAA" or message.content.upper() == "!AA"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/aaa.mp3')
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()
        print("haLÖOOO")

    if (message.content.upper() == "!SUMMON"):
        if (client.is_voice_connected(message.author.server) == True):
                holder = client.voice_client_in(message.author.server)
                if (holder.channel != message.author.voice_channel):
                    voice = client.voice_client_in(message.author.server)
                    await voice.disconnect()
                    await client.join_voice_channel(message.author.voice_channel)
        else:
            voice = await client.join_voice_channel(message.author.voice_channel)

    if (message.content.upper() == "!LEAVE"):
        if (client.is_voice_connected(message.author.server) == True):
            voice = client.voice_client_in(message.author.server)
            await voice.disconnect()

    if (message.content.upper() == "!JAFAR"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/jafar.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!ENIGMA"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/enigma.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!JONI"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/Pud_laugh_05.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()
        #await client.join_voice_channel(message.author.voice_channel)

    if (message.content.upper() == "!JONI2"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/Chaknight_laugh_17.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!CLASU" or message.content.upper() == "!NYT"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/clasu.mp3')
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!HÄVITTY" or message.content.upper() == "!LOST"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/havitty.mp3')
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!KIVAARI" or message.content.upper() == "!KIVÄÄRI"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/kivääri.mp3')
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MARKO1"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/marko1.mp3')
        player.start()
        counter = 0
        duration = 6  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!LEHTONE" or message.content.upper() == "!MORJESTA"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/morjesta.mp3')
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MOTIGONE" or message.content.upper() == "!MOTI"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/motigone.mp3')
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MUIJA" or message.content.upper() == "!HOMMAAMUIJA"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/muija.mp3')
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!OLIIVI" or message.content.upper() == "!LOIRI"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/oliivi.mp3')
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!ONKELMA" or message.content.upper() == "!MARKO2"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/onkelma.mp3')
        player.start()
        counter = 0
        duration = 7  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!PASKAA" or message.content.upper() == "!ISMO1"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/paskaa.mp3')
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!VANTAALLE" or message.content.upper() == "!LEHTONE1"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/potkin.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!HÖPSIT" or message.content.upper() == "!RAKAS"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/rakas.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!DARUDE" or message.content.upper() == "!SANDSTORM"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/sandstorm.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!SINNEMENI" or message.content.upper() == "!MENI"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/sinnemeni.mp3')
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!TURPAKII" or message.content.upper() == "!ISMO2"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/turpakii.mp3')
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MARKO3" or message.content.upper() == "!GRILLI"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/arkiviholinen.mp3')
        player.start()
        counter = 0
        duration = 9  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MARKO4" or message.content.upper() == "!LEIVÄT"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/leivat.mp3')
        player.start()
        counter = 0
        duration = 9  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!2KG" or message.content.upper() == "!SIIKA"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/2kgsiika.mp3')
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!KUVAA" or message.content.upper() == "!KUVAATULEE"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
             voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/kuvaa.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MÖTKÖ" or message.content.upper() == "!MÖTKÖÖ"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/motko.mp3')
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!OTASIIKA" or message.content.upper() == "!OTA"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/otasiika.mp3')
        player.start()
        counter = 0
        duration = 6  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!SIIKAHAN" or message.content.upper() == "!SIELLÄ"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/siikahan.mp3')
        player.start()
        counter = 0
        duration = 7  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!TERVE" or message.content.upper() == "!ISMO3"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/terv.mp3')
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!AAMUPALA" or message.content.upper() == "!PIZZAA" or message.content.upper() == "!MARKO3"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/aamupala.mp3')
        player.start()
        counter = 0
        duration = 15  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!JONI3" or message.content.upper() == "!ESA"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/jonirepe.mp3')
        player.volume = 2.0
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!JONISEKOO" or message.content.upper() == "!JAFAR2"):
        if (client.is_voice_connected(message.author.server) == True):
            holder = client.voice_client_in(message.author.server)
            if (holder.channel != message.author.voice_channel):
                voice = client.voice_client_in(message.author.server)
                await voice.disconnect()
        joined = True
        if (client.is_voice_connected(message.author.server) == False):
            voice = await client.join_voice_channel(message.author.voice_channel)
            joined = False
        else:
            voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player('./sounds/jonisekoo.mp3')
        player.volume = 2.0
        player.start()
        counter = 0
        duration = 20  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

        #####SOUNDS END##########

    if (message.content.upper() == "EXIT" and message.author.id == '95497315078381568'):
        print("Comamnd was given by:")
        print(message.author)
        pickle.dump(namesAndIDs,open("save.p","wb"))
        print("Exiting")
        exit()

    if (message.content.upper().startswith("!YT")):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Another video playing!")
                return
        except:
            pass
        url = ""
        notFound = True
        for x in range(0, len(message.content)):
            if (message.content[x] == ' ' and notFound):
                notFound = False
                continue
            if (notFound == False):
                url += message.content[x]
        if (len(url) <= 2 or url[0] == ""):
            await client.send_message(message.channel, "Invalid url!")
        else:
            voice = client.voice_client_in(message.author.server)
            player = await voice.create_ytdl_player(url)
            player.volume = 0.6
            players[message.server.id] = player
            player.start()

    if (message.content.upper().startswith("!QUEUE")):
        url = ""
        notFound = True
        for x in range(0, len(message.content)):
            if (message.content[x] == ' ' and notFound):
                notFound = False
                continue
            if (notFound == False):
                url += message.content[x]
        if (len(url) <= 2 or url[0] == ""):
            await client.send_message(message.channel, "Invalid url!")
        else:
            try:
                if (players[message.server.id].is_playing()):
                    await client.send_message(message.channel, "Added video to queue!")
                    playQueue.put(url)
                    return
            except:
                pass
        voice = client.voice_client_in(message.author.server)
        player = await voice.create_ytdl_player(url)
        player.volume = 0.3
        players[message.server.id] = player
        player.start()
        djMode = True
        client.loop.create_task(check_if_playing(message))

    if (message.content.upper() == "!PLAYQUE"):
        await client.send_message(message.channel, list(playQueue.queue))

    if (message.content.upper() == "!PAUSE"):
        try:
            pauseQueue.put(1)
            players[message.server.id].pause()
        except:
            pass

    if (message.content.upper() == "!RESUME"):
        try:
            pauseQueue.get()
            players[message.server.id].resume()
        except:
            pass

    if (message.content.upper().startswith("!VOLUME")):
        value = ""
        notFound = True
        for x in range(0, len(message.content)):
            if (message.content[x] == ' ' and notFound):
                notFound = False
                continue
            if (notFound == False):
                value += message.content[x]
        if (len(value) >= 5 or value[0] == ""):
            await client.send_message(message.channel, "Invalid value!")
        else:
            try:
                print(value)
                print(players[message.server.id].volume)
                players[message.server.id].volume = float(value)
                print(players[message.server.id].volume)
            except:
                pass

    if (message.content.upper() == "!SKIP"):
        try:
            players[message.server.id].stop()
        except:
            pass

    if (message.content.upper() == "!STOP"):
        try:
            while (playQueue.empty() == False):
                playQueue.get()
            players[message.server.id].stop()
        except:
            pass

    if (message.content.upper() == "!CLEARQUE"):
        while (playQueue.empty() == False):
            playQueue.get()

    if (message.content.upper() == "!RESET"):
        voice = client.voice_client_in(message.author.server)
        await voice.disconnect()
        await client.join_voice_channel(message.author.voice_channel)


client.run("token") #Replace token with your bots token
