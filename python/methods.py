import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import requests
from html.parser import HTMLParser
import pickle
from decimal import Decimal
from decimal import Context
import time
from bs4 import BeautifulSoup

ranks = [10, "Herald 0", 11, "Herald 1", 12, "Herald 2", 13, "Herald 3", 14, "Herald 4", 15, "Herald 5",
         20, "Guardian 0", 21, "Guardian 1", 22, "Guardian 2", 23, "Guardian 3", 24, "Guardian 4", 25, "Guardian 5",
         30, "Crusader 0", 31, "Crusader 1", 32, "Crusader 2", 33, "Crusader 3", 34, "Crusader 4", 35, "Crusader 5",
         40, "Archon 0", 41, "Archon 1", 42, "Archon 2", 43, "Archon 3", 44, "Archon 4", 45, "Archon 5",
         50, "Legend 0", 51, "Legend 1", 52, "Legend 2", 53, "Legend 3", 54, "Legend 4", 55, "Legend 5",
         60, "Ancient 0", 61, "Ancient 1", 62, "Ancient 2", 63, "Ancient 3", 64, "Ancient 4", 65, "Ancient 5",
         70, "Divine 0", 71, "Divine 1", 72, "Divine 2", 73, "Divine 3", 74, "Divine 4", 75, "Divine 5", 76, "Divine 6"]

async def playedWith(author,msg,client,givenID):
    matches = []
    try:
        namesAndIDs = pickle.load(open("save.p", "rb"))
    except (OSError, IOError):
        namesAndIDs = []
    if author in namesAndIDs:
        index = namesAndIDs.index(author) - 1
        ID = namesAndIDs[index]
    try:
        URL = "https://api.opendota.com/api/players/" + ID + "/matches?included_account_id=" + givenID
        URL2 = "https://api.opendota.com/api/players/" + givenID + "/"
        r = requests.get(url=URL)
        r2 = requests.get(url=URL2)
        data = r.json()
        data2 = r2.json()
        if (len(r.content) <= 6):
            await client.send_message(msg.channel, "No matches found or invalid ID given!")
            return
        if (len(r2.content) <= 6):
            await client.send_message(msg.channel, "Invalid ID!")
            return
        i = 0
        while True:
            try:
                print(str(data[i]['match_id']))
                matches.append(str(data[i]['match_id']))
                i = i + 1
            except IndexError:
                i = 0
                break
        print("Number of matches played with: ")
        print(len(matches))
        print("Match id('s): ")
        e = discord.Embed(title=str(data2['profile']['personaname']), url="https://www.dotabuff.com/players/" + givenID, color=0xffffff)
        thumbnail = str(data2['profile']['avatarmedium'])
        e.set_thumbnail(url=thumbnail)
        for x in range(0,len(matches)):
            print(matches[x])
            e.add_field(name=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(str(data[x]['start_time'])))), value="https://www.dotabuff.com/matches/" + matches[x], inline=False)
        await client.send_message(msg.channel, embed=e)
    except requests.exceptions.RequestException as e:
        print(e)
        await client.send_message(msg.channel, "Invalid ID or fetching failed!")

async def queryProfileNoAuth(msg,client,ID):
        try:
            URL = "https://api.opendota.com/api/players/" + ID + "/"
            URL2 = "https://api.opendota.com/api/players/" + ID + "/wl"
            URL3 = "https://raw.githubusercontent.com/AlexLaak/discoBotTesting/master/dotaHeroes.json"  # For dota 2 heroes
            URL4 = "https://api.opendota.com/api/players/" + ID + "/heroes?having=30"
            r = requests.get(url=URL)    # profile request
            r2 = requests.get(url=URL2)  # W/L request
            r3 = requests.get(url=URL3)  # Dota 2 heroes JSON request
            r4 = requests.get(url=URL4)  # GET heroes played from opendota
            data = r.json()
            data2 = r2.json()
            data3 = r3.json()
            data4 = r4.json()
            if (len(r.content) <= 134):  # Response was invalid
                await client.send_message(msg.channel, "Invalid DOTA ID set!")
                return
            bestHeroes = []
            i = 0
            while True:
                try:
                    games = str(data4[i]['games'])
                    wins = str(data4[i]['win'])
                    hero_id = str(data4[i]['hero_id'])
                    winrate = Decimal(int(wins) / int(games)).quantize(Decimal('.0001'))
                    winrate *= 100
                    winrate = str(winrate)
                    i = i + 1
                    if (len(bestHeroes) < 6):
                        bestHeroes.append(hero_id)
                        bestHeroes.append(winrate)
                        continue
                    if (len(bestHeroes) == 6):
                        hero_wr = 0
                        new_arr = []
                        x = 1
                        for x in range(1, len(bestHeroes), 2):
                            new_arr.append(bestHeroes[x])
                            x = x + 2
                            if (x > len(bestHeroes)):
                                break
                        if (Decimal(winrate) > Decimal(min(new_arr))):
                            bestHeroes.pop(bestHeroes.index(min(new_arr)) - 1)
                            bestHeroes.pop(bestHeroes.index(min(new_arr)))
                            bestHeroes.append(hero_id)
                            bestHeroes.append(winrate)
                except IndexError:
                    i = 0
                    break
            heroNames = []
            heroNamesFinal = []
            heroWinRates = []
            y = 1
            for x in range(0, len(bestHeroes), 2):
                heroNames.append(bestHeroes[x])
                heroWinRates.append(bestHeroes[y])
                y = y + 2
                x = x + 2
            print("heroids:")
            print(heroNames)
            print("herowrs:")
            print(heroWinRates)
            c = 0
            for x in range(0, len(heroNames)):
                if (int(heroNames[c]) <= 23):
                    heroNamesFinal.append(str(data3['heroes'][int(heroNames[c]) - 1]['localized_name']))
                if (int(heroNames[c]) > 23 and int(heroNames[c]) <= 114):
                    heroNamesFinal.append(str(data3['heroes'][int(heroNames[c]) - 2]['localized_name']))
                if (int(heroNames[c]) == 119):
                    heroNamesFinal.append(str(data3['heroes'][113]['localized_name']))
                if (int(heroNames[c]) == 120):
                    heroNamesFinal.append(str(data3['heroes'][114]['localized_name']))
                c = c + 1
            print("heronames:")
            print(heroNamesFinal)
            name = str(data['profile']['personaname'])
            wins = str(data2['win'])
            lBoardRank = str(data['leaderboard_rank'])
            losses = str(data2['lose'])
            matches = int(wins) + int(losses)
            ratio = Decimal(int(wins) / matches).quantize(Decimal('.0001'))  # this should be shortened
            ratio *= 100                                                     # *
            ratio = str(ratio)                                               # to one line
            mmr = str(data['competitive_rank'])
            rank = ranks[ranks.index(int(data['rank_tier'])) + 1]
            e = discord.Embed(title=name, url="https://www.dotabuff.com/players/" + ID, color=0xff0000)
            thumbnail = str(data['profile']['avatarmedium'])
            e.set_thumbnail(url=thumbnail)
            e.add_field(name="MMR", value=mmr, inline=False)
            if (lBoardRank == "None"):
                if (ID == "16461609"):
                    e.add_field(name="Rank", value="Divine 6 ( 1 )", inline=False)
                elif (ID == "52771243"):
                    e.add_field(name="Rank", value="Divine 1337 ( ??? )", inline=False)
                else:
                    e.add_field(name="Rank", value=rank, inline=False)
            else:
                e.add_field(name="Rank", value="Divine 6  (" + lBoardRank + ")", inline=False)
            e.add_field(name="Win/Loss", value= wins + "-" + losses + " (" + ratio[:5] + "%)",
                        inline=False)
            e.add_field(name="Top Heroes", value=heroNamesFinal[0] + " (" + heroWinRates[0][:5] + "%)" +
                                                 "\n" + heroNamesFinal[1] + " (" + heroWinRates[1][:5] + "%)" +
                                                 "\n" + heroNamesFinal[2] + " (" + heroWinRates[2][:5] + "%)",
                        inline=False)
            await client.send_message(msg.channel, embed=e)
        except requests.exceptions.RequestException as e:
            print(e)
            await client.send_message(msg.channel, "Invalid ID or fetching failed!")

async def queryProfile(author,msg,client):
    try:
        namesAndIDs = pickle.load(open("save.p", "rb"))
    except (OSError, IOError):
        namesAndIDs = []
    if author in namesAndIDs:
        index = namesAndIDs.index(author) - 1
        ID = namesAndIDs[index]
        try:
            URL = "https://api.opendota.com/api/players/" + ID + "/"
            URL2 = "https://api.opendota.com/api/players/" + ID + "/wl"
            URL3 = "https://raw.githubusercontent.com/AlexLaak/discoBotTesting/master/dotaHeroes.json"  # For dota 2 heroes
            URL4 = "https://api.opendota.com/api/players/" + ID + "/heroes?having=30"
            r = requests.get(url=URL)    # profile request
            r2 = requests.get(url=URL2)  # W/L request
            r3 = requests.get(url=URL3)  # Dota 2 heroes JSON request
            r4 = requests.get(url=URL4)  # GET heroes played from opendota
            data = r.json()
            data2 = r2.json()
            data3 = r3.json()
            data4 = r4.json()
            if (len(r.content) <= 134):  # Response was invalid
                await client.send_message(msg.channel, "Invalid DOTA ID set!")
                return
            bestHeroes = []
            i = 0
            while True:
                try:
                    games = str(data4[i]['games'])
                    wins = str(data4[i]['win'])
                    hero_id = str(data4[i]['hero_id'])
                    winrate = Decimal(int(wins) / int(games)).quantize(Decimal('.0001'))
                    winrate *= 100
                    winrate = str(winrate)
                    i = i + 1
                    if (len(bestHeroes) < 6):
                        bestHeroes.append(hero_id)
                        bestHeroes.append(winrate)
                        continue
                    if (len(bestHeroes) == 6):
                        hero_wr = 0
                        new_arr = []
                        x = 1
                        for x in range(1, len(bestHeroes), 2):
                            new_arr.append(bestHeroes[x])
                            x = x + 2
                            if (x > len(bestHeroes)):
                                break
                        if (Decimal(winrate) > Decimal(min(new_arr))):
                            bestHeroes.pop(bestHeroes.index(min(new_arr)) - 1)
                            bestHeroes.pop(bestHeroes.index(min(new_arr)))
                            bestHeroes.append(hero_id)
                            bestHeroes.append(winrate)
                except IndexError:
                    i = 0
                    break
            heroNames = []
            heroNamesFinal = []
            heroWinRates = []
            y = 1
            for x in range(0, len(bestHeroes), 2):
                heroNames.append(bestHeroes[x])
                heroWinRates.append(bestHeroes[y])
                y = y + 2
                x = x + 2
            print("heroids:")
            print(heroNames)
            print("herowrs:")
            print(heroWinRates)
            c = 0
            for x in range(0, len(heroNames)):
                if (int(heroNames[c]) <= 23):
                    heroNamesFinal.append(str(data3['heroes'][int(heroNames[c]) - 1]['localized_name']))
                if (int(heroNames[c]) > 23 and int(heroNames[c]) <= 114):
                    heroNamesFinal.append(str(data3['heroes'][int(heroNames[c]) - 2]['localized_name']))
                if (int(heroNames[c]) == 119):
                    heroNamesFinal.append(str(data3['heroes'][113]['localized_name']))
                if (int(heroNames[c]) == 120):
                    heroNamesFinal.append(str(data3['heroes'][114]['localized_name']))
                c = c + 1
            print("heronames:")
            print(heroNamesFinal)
            name = str(data['profile']['personaname'])
            wins = str(data2['win'])
            lBoardRank = str(data['leaderboard_rank'])
            losses = str(data2['lose'])
            matches = int(wins) + int(losses)
            ratio = Decimal(int(wins) / matches).quantize(Decimal('.0001'))  # this should be shortened
            ratio *= 100  # *
            ratio = str(ratio)  # to one line
            mmr = str(data['competitive_rank'])
            rank = ranks[ranks.index(int(data['rank_tier'])) + 1]
            e = discord.Embed(title=name, url="https://www.dotabuff.com/players/" + ID, color=0xff0000)
            thumbnail = str(data['profile']['avatarmedium'])
            e.set_thumbnail(url=thumbnail)
            e.add_field(name="MMR", value=mmr, inline=False)
            if (lBoardRank == "None"):
                if (ID == "16461602"):              ##if u want to prank someone, add their id here
                    e.add_field(name="Rank", value="Divine 6 ( 1 )", inline=False)
                elif (ID == "52771363"):
                    e.add_field(name="Rank", value="Divine 1337 ( ??? )", inline=False)
                else:
                    e.add_field(name="Rank", value=rank, inline=False)
            else:
                e.add_field(name="Rank", value="Divine 6  (" + lBoardRank + ")", inline=False)
            e.add_field(name="Win/Loss", value= wins + "-" + losses + " (" + ratio[:5] + "%)",
                        inline=False)
            e.add_field(name="Top Heroes", value=heroNamesFinal[0] + " (" + heroWinRates[0][:5] + "%)" +
                                                 "\n" + heroNamesFinal[1] + " (" + heroWinRates[1][:5] + "%)" +
                                                 "\n" + heroNamesFinal[2] + " (" + heroWinRates[2][:5] + "%)",
                        inline=False)
            await client.send_message(msg.channel, embed=e)
        except requests.exceptions.RequestException as e:
            print(e)
            await client.send_message(msg.channel, "Invalid ID or fetching failed!")

    else:
        await client.send_message(msg.channel, "You have not setup your ID!")

async def checkPricePool():
    r = requests.get("http://dota2.prizetrac.kr/international2018")
    soup = BeautifulSoup(r.text, "html.parser")
    soup2 = BeautifulSoup(r.text, "html.parser")
    pool = soup.find('h1',{'class':'ui green header'}).text
    text = soup2.find('div',{'class':'ui green message'}).text
    return "```TI8 Prize pool atm:\n" + pool + "\n\n" + text + "```"

async def queryLastMatch(author,msg,client):
    print("haloo")
    playerIDs = []
    try:
        namesAndIDs = pickle.load(open("save.p", "rb"))
    except (OSError, IOError):
        namesAndIDs = []
    if author in namesAndIDs:
        index = namesAndIDs.index(author) - 1
        ID = namesAndIDs[index]
    try:
        URL = "https://api.opendota.com/api/players/" + ID + "/recentMatches"
        r = requests.get(url=URL)
        data = r.json()
        matchID = str(data[0]['match_id'])
        URL2 = "https://api.opendota.com/api/matches/" + matchID
        r2 = requests.get(url=URL2)
        data2 = r2.json()
        if (len(r.content) <= 6):
            await client.send_message(msg.channel, "No matches found or invalid ID given!")
            return
        if (len(r2.content) <= 6):
            await client.send_message(msg.channel, "No matches found or invalid ID given!")
            return
        print("Match ID:  ")
        print(matchID)
        i = 0
        while True:
            try:
                add = str(data2['players'][i]['account_id'])
                if (add != "None"):
                    playerIDs.append(str(data2['players'][i]['personaname']))
                    playerIDs.append(add)
                i = i + 1
            except IndexError:
                break
        print(playerIDs)
        await client.send_message(msg.channel, playerIDs)
    except requests.exceptions.RequestException as b:
        print(b)
        await client.send_message(msg.channel, "Invalid ID or fetching failed!")

async def queryHelper(author):
    playerIDs = []
    try:
        whitelist = pickle.load(open("whitelistt.p", "rb"))
    except (OSError, IOError):
        whitelist = []
    try:
        namesAndIDs = pickle.load(open("save.p", "rb"))
    except (OSError, IOError):
        namesAndIDs = []
    if author in namesAndIDs:
        index = namesAndIDs.index(author) - 1
        ID = namesAndIDs[index]
    try:
        URL = "https://api.opendota.com/api/players/" + ID + "/recentMatches"
        r = requests.get(url=URL)
        data = r.json()
        matchID = str(data[0]['match_id'])
        URL2 = "https://api.opendota.com/api/matches/" + matchID
        r2 = requests.get(url=URL2)
        data2 = r2.json()
        if (len(r.content) <= 6):
            return
        if (len(r2.content) <= 6):
            return
        print("Match ID:  ")
        print(matchID)
        i = 0
        while True:
            try:
                add = str(data2['players'][i]['account_id'])
                if (add != "None"):
                    if (add not in whitelist):
                        playerIDs.append(add)
                i = i + 1
            except IndexError:
                break
        return playerIDs
    except requests.exceptions.RequestException as b:
        print(b)
        return


async def playedWithLastGame(givenIDs, myID, msg, client):

    try:
        whitelist = pickle.load(open("whitelistt.p", "rb"))
    except (OSError, IOError):
        whitelist = []

    IDs = []
    IDs = givenIDs

    print(IDs)

    for x in range(0,len(IDs)):
        if (givenIDs[x] not in whitelist):
            matches = []
            try:
                URL = "https://api.opendota.com/api/players/" + myID + "/matches?included_account_id=" + givenIDs[x]
                URL2 = "https://api.opendota.com/api/players/" + givenIDs[x] + "/"
                r = requests.get(url=URL)
                r2 = requests.get(url=URL2)
                data = r.json()
                data2 = r2.json()
                if (len(r.content) <= 6):
                    return
                if (len(r2.content) <= 6):
                    return
                i = 0  #set to 1 if want to skip first game
                while True:
                    try:
                        print(str(data[i]['match_id']))
                        matches.append(str(data[i]['match_id']))
                        i = i + 1
                    except IndexError:
                        i = 0
                        break
                print("Number of matches played with: ")
                print(len(matches))
                print("Match id('s): ")
                e = discord.Embed(title=str(data2['profile']['personaname']),
                                  url="https://www.dotabuff.com/players/" + givenIDs[x], color=0xffffff)
                thumbnail = str(data2['profile']['avatarmedium'])
                e.set_thumbnail(url=thumbnail)
                for b in range(0, len(matches)):
                    print(matches[b])
                    if (len(matches) <= 1):
                        e.add_field(name='No matches found!',value='^^^^^^^^^^', inline=False)
                    else:
                        e.add_field(
                            name=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(str(data[b]['start_time'])))),
                            value="https://www.dotabuff.com/matches/" + matches[b], inline=False)
                await client.send_message(msg.channel, embed=e)
            except requests.exceptions.RequestException as e:
                print(e)
                await client.send_message(msg.channel, "Invalid ID or fetching failed!")
        else:
            print(whitelist)
            print(givenIDs[x])
async def getProfileID(author):
    try:
        namesAndIDs = pickle.load(open("save.p", "rb"))
    except (OSError, IOError):
        namesAndIDs = []
    print(author)
    if author in namesAndIDs:
        index = namesAndIDs.index(author) - 1
        ID = namesAndIDs[index]
        print("mit vitu")
        print(ID)
        return ID
    return "None"