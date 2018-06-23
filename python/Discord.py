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
radioQueue = queue.Queue()

steamIDremoval = 76561197960265728

async def check_if_playing(message):
    while True:
        if (players[message.server.id].is_playing()):
            pass
        else:
            if (playQueue.empty()):
                await client.change_presence(game=discord.Game(name='!commands'))
                break
            elif (pauseQueue.empty() == False):
                print("paused")
                pass
            else:
                voice = client.voice_client_in(message.author.server)
                url = playQueue.get()
                player = await voice.create_ytdl_player(url)
                player.volume = 0.4
                players[message.server.id] = player
                player.start()
                print("swapping song")
                await client.change_presence(game=discord.Game(name=await getYoutubeTitle(url)))
        await asyncio.sleep(5)

@client.event
async def on_ready():
    print("Bot is online and connected to Discord") #This will be called when the bot connects to the server
    await client.change_presence(game=discord.Game(name='!commands'))
@client.event
async def on_message(message):

    channel = message.channel.name
    if (channel != "pakettipaskaa"):                #To listen only messages from certain channel
        return

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
            namesAndIDs.append(message.author.name)
            namesAndIDs.append(message.author.id)
        pickle.dump(namesAndIDs, open("save.p", "wb"))

    if (message.content.upper().startswith("!DELETE_ID") and message.author.id in namesAndIDs):
        print("Comamnd was given by:")
        print(message.author)
        namesAndIDs.remove(namesAndIDs[namesAndIDs.index(message.author.id) - 2])
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
        listToPrint = ""
        print(len(namesAndIDs))
        b = 0
        for x in range(0,len(namesAndIDs)):
            print(b)
            listToPrint += "Dota ID: " + namesAndIDs[b] + " Username: " + namesAndIDs[b+1] + '\n'
            b = b + 3
            if (b >= len(namesAndIDs)):
                break
        await client.send_message(message.channel, "```"+listToPrint+"```")  # print list of names

    if (message.content.upper() == "!ME"):
        print("Comamnd was given by:")
        print(message.author)
        await queryProfile(message.author.id,message,client)

    if (message.content.upper().startswith("!PROFILE")):
        DotaID = ""
        notFound = True

        if (len(message.content) >= 48):
            DotaID = str(re.findall('\d+', message.content)[0])
            if (len(DotaID) < len(message.content)):
                message.content = DotaID
                DotaID = message.content

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
                print(DotaID)
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
            if (len(DotaID) < len(message.content)):
                message.content = DotaID
                DotaID = message.content

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
        "\n```!sounds                        -Displays list of all sound clips"   
        "\n"
        "\n!radio                         -Displays list of all radio commands"
        "\n"
        "\n!summon                        -Summons bot to voice channel"
        "\n"
        "\n!yt <youtube link>             -Plays youtube video from link"
        "\n"
        "\n!play <youtube search>         -Search from youtube and then play."
        "\n"
        "\n!playque                       -Displays current youtube video queue"
        "\n"
        "\n!stop                          -Stops music playback and clears queue"
        "\n"
        "\n!volume <value>                -Adjust volume of current sound clip"
        "\n"
        "\n!skip                          -Skips currently playing youtube video"
        "\n"
        "\n"
        "\nDota Commands:"
        "\n"
        "\n!add_id <dotaID>               -Adds given dotaID to the bots list"
        "\n"
        "\n!delete_id                     -Deletes your current dotaID from list"
        "\n"
        "\n!list                          -Displays list of added dotaIDs"
        "\n"
        "\n!me                            -Displays your Dota profile"
        "\n"
        "\n!pw <dotaID/steam64>           -Searches if you have played with"   
        "\n"
        "\n!profile <dotaID/steam64>      -Display given profile"       
        "\n"
        "\n!lastmatch                     -Checks if you have played against \n"
        "                                            last match players"
        "\n"
        "\n!whitelist <dotaID>            -Adds given dotaID to whitelist which \n"
        "                 is used to filter given dotaID from showing in !lastmatch" 
        "\n"
        "\n!prize                         -Display current TI8 prize pool```")

    if (message.content.upper() == "!RADIO" or message.content.upper() == "!RADIOCOMMANDS"):
        print("Comamnd was given by:")
        print(message.author)
        await client.send_message(message.channel, "List of radio commands:"
                                                   "\n```!radiorock"              
                                                   "\n!nrj"
                                                   "\n!loop"
                                                   "\n!hitmix"
                                                   "\n!summon"
                                                   "\n!leave"
                                                   "\n!resume"
                                                   "\n!pause"
                                                   "\n!stop```")

    if (message.content.upper() == "!SOUNDS"):
        print("Comamnd was given by:")
        print(message.author)
        await client.send_message(message.channel, "List of sound clips:"
                                                    "\n```!summon"
                                                    "\n!leave"
                                                    "\n!joni"
                                                    "\n!joni2"
                                                    "\n!joni3"
                                                    "\n!joni4"
                                                    "\n!jonisekoo"
                                                    "\n!jonilogic"
                                                    "\n!joona" 
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
                                                    "\n!lehtone2"
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
        if (players[message.server.id].is_playing()):
            await client.send_message(message.channel, "Currently playing! use !stop to stop playing!")
            return
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

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
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        player.volume = 2.0
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!ENIGMA"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!JONI"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
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
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!CLASU" or message.content.upper() == "!NYT"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!HÄVITTY" or message.content.upper() == "!LOST"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!KIVAARI" or message.content.upper() == "!KIVÄÄRI"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MARKO1"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 6  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!LEHTONE" or message.content.upper() == "!MORJESTA"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MOTIGONE" or message.content.upper() == "!MOTI"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MUIJA" or message.content.upper() == "!HOMMAAMUIJA"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!OLIIVI" or message.content.upper() == "!LOIRI"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!ONKELMA" or message.content.upper() == "!MARKO2"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 7  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!PASKAA" or message.content.upper() == "!ISMO1"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!VANTAALLE" or message.content.upper() == "!LEHTONE1"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!HÖPSIT" or message.content.upper() == "!RAKAS"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!DARUDE" or message.content.upper() == "!SANDSTORM"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!SINNEMENI" or message.content.upper() == "!MENI"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!TURPAKII" or message.content.upper() == "!ISMO2"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MARKO3" or message.content.upper() == "!GRILLI"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 9  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MARKO4" or message.content.upper() == "!LEIVÄT"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 9  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!2KG" or message.content.upper() == "!SIIKA"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!KUVAA" or message.content.upper() == "!KUVAATULEE"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!MÖTKÖ" or message.content.upper() == "!MÖTKÖÖ"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!OTASIIKA" or message.content.upper() == "!OTA"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 6  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!SIIKAHAN" or message.content.upper() == "!SIELLÄ"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 7  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!TERVE" or message.content.upper() == "!ISMO3"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 3  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!AAMUPALA" or message.content.upper() == "!PIZZAA" or message.content.upper() == "!MARKO3"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 15  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!JONI3" or message.content.upper() == "!ESA"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!JONISEKOO" or message.content.upper() == "!JAFAR2"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 20  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!JONILOGIC" or message.content.upper() == "!LOGIC"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        player = voice.create_ffmpeg_player('./sounds/jonilogic.mp3')
        player.volume = 2.0
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!LEHTONE2" or message.content.upper() == "!PAPAL"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        player = voice.create_ffmpeg_player('./sounds/lehtonen.mp3')
        player.volume = 2.0
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 5  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!JOONA" or message.content.upper() == "!KUOLIN"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        player = voice.create_ffmpeg_player('./sounds/joona.mp3')
        player.volume = 2.0
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 8  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!JOONA2" or message.content.upper() == "!LIMAA"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        player = voice.create_ffmpeg_player('./sounds/limaa.mp3')
        player.volume = 2.0
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 6  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()

    if (message.content.upper() == "!JONI4" or message.content.upper() == "!CHRONO"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
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
        player = voice.create_ffmpeg_player('./sounds/jonichrono.mp3')
        player.volume = 2.0
        players[message.server.id] = player
        player.start()
        counter = 0
        duration = 6  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        if (joined == False):
            await voice.disconnect()
        #####SOUNDS END##########

    if (message.content.upper() == "EXIT" and message.author.id == '95497315078381568'):
        pickle.dump(namesAndIDs,open("save.p","wb"))
        quit()

    #DEPRECATED
    if (message.content.upper().startswith("!vanhaaa")):
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

    if (message.content.upper().startswith("!QUEUE") or message.content.upper().startswith("!YT")):
        if (client.is_voice_connected(message.author.server) == False):
            await client.send_message(message.channel, "Summon me first to your channel! *!summon")
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
                if (pauseQueue.empty() == False):
                    print("paused but still added to que")
                    playQueue.put(url)
                    await client.send_message(message.channel, "Added video to queue!")
                    return
            except:
                pass
        voice = client.voice_client_in(message.author.server)
        player = await voice.create_ytdl_player(url)
        player.volume = 0.3
        players[message.server.id] = player
        player.start()
        await client.change_presence(game=discord.Game(name=await getYoutubeTitle(url)))
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
                players[message.server.id].volume = float(value)
            except:
                pass

    if (message.content.upper() == "!SKIP"):
        try:
            players[message.server.id].stop()
        except:
            pass

    if (message.content.upper() == "!STOP"):
        try:
            if (radioQueue.empty() == False):
                radioQueue.get()
            while (playQueue.empty() == False):
                playQueue.get()
            players[message.server.id].stop()
            await client.change_presence(game=discord.Game(name='!commands'))
        except:
            pass

    #SEARCH
    if (message.content.upper().startswith("!PLAY")):
        if (client.is_voice_connected(message.author.server) == False):
            await client.send_message(message.channel, "Summon me first to your channel! *!summon")
            return
        value = ""
        notFound = True
        for x in range(0, len(message.content)):
            if (message.content[x] == ' ' and notFound):
                notFound = False
                continue
            if (notFound == False):
                if (message.content[x] == ' '):
                    value += '+'
                else:
                    value += message.content[x]
        if (len(value) <= 1 or value[0] == ""):
            await client.send_message(message.channel, "Invalid search!")
            return
        else:
            url = await searchYT(value)
            try:
                if (players[message.server.id].is_playing()):
                    await client.send_message(message.channel, "Added video to queue!")
                    playQueue.put(url)
                    return
                if (pauseQueue.empty() == False):
                    print("paused but still added to que")
                    playQueue.put(url)
                    await client.send_message(message.channel, "Added video to queue!")
                    return
            except:
                pass
        voice = client.voice_client_in(message.author.server)
        player = await voice.create_ytdl_player(url)
        player.volume = 0.3
        players[message.server.id] = player
        await client.change_presence(game=discord.Game(name=await getYoutubeTitle(url)))
        player.start()
        client.loop.create_task(check_if_playing(message))

        #get radio playing song
    if (message.content.upper() == "!SONG"):
        if (players[message.server.id].is_playing() == False):
            await client.send_message(message.channel, "Radio is not on!")
            return
        url = radioQueue.get()
        radioQueue.put(url)
        await client.send_message(message.channel, await getRadioSong(url))

    if (message.content.upper() == "!RADIOROCK"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
        url = "http://icelive0.80692-icelive0.cdn.qbrick.com/10565/80692_RadioRock.mp3"
        radioQueue.put("https://biisit.info/rock")
        voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player(url)
        player.volume = 0.3
        players[message.server.id] = player
        player.start()
        await client.change_presence(game=discord.Game(name='Radio Rock'))

    if (message.content.upper() == "!HITMIX"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
        url = "http://icelive0-80692-icelive0.dna.qbrick.com/10162/80692_HitMix.mp3"
        radioQueue.put("https://biisit.info/hitmix")
        voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player(url)
        player.volume = 0.3
        players[message.server.id] = player
        player.start()
        await client.change_presence(game=discord.Game(name='HitMix'))

    if (message.content.upper() == "!NRJ"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
        url = "http://cdn.nrjaudio.fm/adwz1/fi/35001/mp3_128.mp3"
        radioQueue.put("https://biisit.info/nrj")
        voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player(url)
        player.volume = 0.3
        players[message.server.id] = player
        player.start()
        await client.change_presence(game=discord.Game(name='NRJ'))

    if (message.content.upper() == "!LOOP"):
        try:
            if (players[message.server.id].is_playing()):
                await client.send_message(message.channel, "Currently playing! use !stop to stop playing")
                return
        except:
            pass
        url = "http://icelive0.80692-icelive0.cdn.qbrick.com/10561/80692_Loop.mp3"
        radioQueue.put("https://biisit.info/loop")
        voice = client.voice_client_in(message.author.server)
        player = voice.create_ffmpeg_player(url)
        player.volume = 0.3
        players[message.server.id] = player
        player.start()
        await client.change_presence(game=discord.Game(name='Loop'))

    if (message.content.upper() == "!CLEARQUE"):
        while (playQueue.empty() == False):
            playQueue.get()

    if (message.content.upper() == "!RESET"):
        voice = client.voice_client_in(message.author.server)
        await voice.disconnect()
        await client.join_voice_channel(message.author.voice_channel)


client.run("token here")