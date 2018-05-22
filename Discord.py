import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import pickle
from methods import *

Client = discord.Client() #Initialise Client
client = commands.Bot(command_prefix = "?") #Initialise client bot

namesAndIDs = []
whitelistIDs = []

steamIDremoval = 76561197960265728

@client.event
async def on_ready():
    print("Bot is online and connected to Discord") #This will be called when the bot connects to the server

@client.event
async def on_message(message):

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
            whitelistIDs.append(DotaID)
        pickle.dump(whitelistIDs, open("whitelistt.p", "wb"))

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

    if (message.content.upper() == "!JAFAR"):
        voice = await client.join_voice_channel(message.author.voice_channel)
        player = voice.create_ffmpeg_player('./sounds/jafar.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        await voice.disconnect()

    if (message.content.upper() == "!JONI"):
        voice = await client.join_voice_channel(message.author.voice_channel)
        player = voice.create_ffmpeg_player('./sounds/Pud_laugh_05.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        await voice.disconnect()
        #await client.join_voice_channel(message.author.voice_channel)

    if (message.content.upper() == "!JONI2"):
        voice = await client.join_voice_channel(message.author.voice_channel)
        player = voice.create_ffmpeg_player('./sounds/Chaknight_laugh_17.mp3')
        player.start()
        counter = 0
        duration = 4  # In seconds
        while not counter >= duration:
            await asyncio.sleep(1)
            counter = counter + 1
        await voice.disconnect()

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

    if (message.content.upper() == "!LASTMATCH"):
        await queryLastMatch(message.author.id, message, client)

    if (message.content.upper().startswith("!PW") and message.author.id in namesAndIDs):
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
            if (len(DotaID) >= 16):
                DotaID = int(DotaID) - steamIDremoval
                DotaID = str(DotaID)
                print(DotaID)
            await playedWith(message.author.id,message,client,DotaID)

    if (message.content.upper() == "!COMMANDS" or message.content.upper() == "!HELP"):
        print("Comamnd was given by:")
        print(message.author)
        await client.send_message(message.channel, "List of commands: \n```!add_id <dotaID>"
                                                   "\n!delete_id"
                                                   "\n!list"
                                                   "\n!me"
                                                   "\n!pw <dotaID or steam64>"
                                                   "\n!sounds"
                                                   "\n!profile<dotaID or steam64```"
                                                   "\n!lastmatch```")

    if (message.content.upper() == "!SOUNDS"):
        print("Comamnd was given by:")
        print(message.author)
        await client.send_message(message.channel, "List of sounds: \n```!joni"
                                                   "\n!joni2```"
                                                   "\n!jafar```")

    if (message.content.upper() == "EXIT"):
        print("Comamnd was given by:")
        print(message.author)
        pickle.dump(namesAndIDs,open("save.p","wb"))
        print("Exiting")
        exit()

client.run("token") #Replace token with your bots token
