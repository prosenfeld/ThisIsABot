
import discord
import os
import requests
import json
import math
import logging
from datetime import datetime, timedelta
from aiohttp import ClientSession

#from keep_alive import keep_alive
import unicodedata
#from keep_alive import keep_alive
from discord.ext import commands
#ךogging.basicConfig(level=logging.DEBUG)


logger = logging.getLogger('discord')
logging.basicConfig(filename='discord.log', level=logging.DEBUG, format = '%(asctime)s:%(levelname)s:%(name)s: %(message)s')
#logger.addHandler(handler)
print("sanity test")
logging.warning("sanity test")

client = discord.Client()
map_key=os.getenv("MAPBOX_KEY")

#async def ping(channel):
#    await channel.send(f'pong!\n{round(bot.latency * 1000)}ms')
def whois(member: discord.Member):
    embed=discord.Embed()
    user = discord.get_member(member)
    embed.set_thumbnail(url=user.avatar_url)
    return embed
async def get_weather(place="Washington DC"):
    async with ClientSession() as session:
        place = place.lower()
        response = await session.request(method='GET', url=f"https://weather.ls.hereapi.com/weather/1.0/report.json?apiKey={map_key}&product=observation&name={place}")
        response_json = await response.json()
        logging.debug(response_json)
        print(response_json)
        new_json = response_json
        temp = new_json["observations"]["location"][0]["observation"][0]["temperature"]
        desc = new_json["observations"]["location"][0]["observation"][0]["description"]
        real_city_name = new_json["observations"]["location"][0]["observation"][0]["city"]
        real_city_country = new_json["observations"]["location"][0]["observation"][0]["country"]
        real_city_state = new_json["observations"]["location"][0]["observation"][0]["state"]
        # print(f"In {place} it is currently {temp} degrees C ({(float(temp)*1.8)+32}F) and  {desc}.")
        embed = discord.Embed(
            title=f'Weather for {real_city_name}, {real_city_state}, {real_city_country} ',
            description=f"Currently {temp} degrees C ({round((float(temp) * 1.8) + 32, 2)} F) and  {desc}.",
            color = discord.Colour.red()
        )
        embed.set_thumbnail(url=new_json["observations"]["location"][0]["observation"][0]["iconLink"]+f"?apikey={map_key}")
        print(new_json["observations"]["location"][0]["observation"][0]["iconLink"])
        # return (
        #f"In {real_city_name}, {real_city_state}, {real_city_country} it is currently {temp} degrees C ({round((float(temp) * 1.8) + 32, 2)} F) and  {desc}.")
        return embed
        #return (
            #f"In {real_city_name}, {real_city_state}, {real_city_country} it is currently {temp} degrees C ({round((float(temp) * 1.8) + 32, 2)} F) and  {desc}.")

async def pull_a_passuk(sefer, perek, passuk, translation=False):
    async with ClientSession() as session:
        get_text = await session.request(method='GET', url=f"https://www.sefaria.org/api/texts/{sefer}.{perek}.{passuk}?context=0 ")
        json_of_txt = await get_text.json()
        logging.debug(json_of_txt)
        nikudnik = json_of_txt["he"]

        if translation:
            give_translation =json_of_txt["text"]
            normalized = unicodedata.normalize("NFKD", nikudnik)
            flattened = "".join([c for c in normalized if not unicodedata.combining(c)])
            flattened = flattened.replace("(פ)" ,"")
            flattened = flattened.replace("(ס)" ,"")
            give_translation=give_translation.replace("<i>" , " ").replace("</i>"," ").replace("<b>"," ").replace("</b>"," ")
            return flattened +"\n " +give_translation
        else:
            normalized = unicodedata.normalize("NFKD", nikudnik)
            flattened = "".join([c for c in normalized if not unicodedata.combining(c)])
            flattened = flattened.replace("(פ)" ,"")
            flattened = flattened.replace("(ס)" ,"")
            return flattened


async def pull_a_perek(sefer, perek, translation):
    async with ClientSession() as session:
        get_text = await session.request(method='GET', url=f"https://www.sefaria.org/api/texts/{sefer}.{perek}?context=0")
        json_of_txt = await get_text.json()
        logging.debug(json_of_txt)
        if translation:
            nikudnik = "".join(json_of_txt["he"])
            normalized = unicodedata.normalize("NFKD", nikudnik)
            flattened = "".join([c for c in normalized if not unicodedata.combining(c)])
            logging.debug(flattened)
            give_translation = "".join(json_of_txt["text"])
            return flattened + give_translation.replace("<i></i>" ,"")
        else:
            nikudnik = "".join(json_of_txt["he"])
            normalized = unicodedata.normalize("NFKD", nikudnik)
            flattened = "".join([c for c in normalized if not unicodedata.combining(c)])
            logging.debug(flattened)
            return flattened

async def test():
    async with ClientSession() as session:
        response = await session.request(method='GET', url="https://www.sefaria.org/api/texts/exodus.1.1?context=0")
        response_json = await response.json()
        return response_json


async def get_zmanim(place:str):
    async with ClientSession() as session:
        relevant_results ={}
        pulled_timing = await session.request(method='GET', url=f"https://weather.ls.hereapi.com/weather/1.0/report.json?apiKey={map_key}&product=forecast_astronomy&name={place}")
        new_json = await pulled_timing.json()
        relevant_results["city" ] = new_json["astronomy"]["city"]
        relevant_results["state" ] = new_json["astronomy"]["state"]
        relevant_results["country" ] = new_json["astronomy"]["country"]
        relevant_results["sunrise" ] = new_json["astronomy"]["astronomy"][0]["sunrise"]
        relevant_results["sunset" ] = new_json["astronomy"]["astronomy"][0]["sunset"]

        sunrise = relevant_results["sunrise"][:-2]
        sunset = relevant_results["sunset"][:-2]
        hours = sunset[:-2].replace(":" , "")
        minutes = sunset[-2:]
        sunset = str(int(hours) +12) +minutes
        sunset = sunset[:-2] +":" +sunset[-2:]
        FMT = '%H:%M'
        tdelta = datetime.strptime(sunset, FMT) - datetime.strptime(sunrise, FMT)
        sunset = datetime.strptime(sunset ,FMT)
        sunrise = datetime.strptime(sunrise ,FMT)

        shaot_zmaniot = tdelta /12
        shaot_zmaniot_convert = round(shaot_zmaniot.seconds /60 ,4)
        relevant_results["shaot_zmaniot"] = shaot_zmaniot_convert

        chatzot = shaot_zmaniot * 6 +sunrise
        relevant_results["chatzot"]  = (shaot_zmaniot * 6 +sunrise).strftime('%H:%M')

        alos = sunrise - timedelta(minutes = 72)
        relevant_results["alos hashachar"] =datetime.strftime(alos ,"%H:%M")

        tzais = sunset +timedelta(minutes=45)
        relevant_results["tzais hakochavim"] = datetime.strftime(tzais ,"%H:%M")

        latest_davening = (shaot_zmaniot * 4 +sunrise).strftime('%H:%M')
        relevant_results["latest davening"] = latest_davening

        mincha_gedola =(shaot_zmaniot *0.5 ) +chatzot
        relevant_results["mincha gedola"] = mincha_gedola.strftime("%H:%M")

        candlelighting = sunset -timedelta(minutes=18)
        relevant_results["candlelighting"] = candlelighting.strftime("%H:%M")

        mincha_katana = sunset - (shaot_zmaniot * 2.5 )
        relevant_results["mincha katana"] = mincha_katana.strftime("%H:%M")

        plag = sunset - (shaot_zmaniot * 1.25)
        relevant_results["plag hamincha"] = plag.strftime("%H:%M")

        latest_shma = sunrise +(shaot_zmaniot * 3)
        relevant_results["latest shma"] = latest_shma.strftime("%H:%M")

        misheyakir = sunrise -timedelta(minutes=45)
        relevant_results["misheyakir"] = misheyakir.strftime("%H:%M")

        return relevant_results



@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    logging.info("We have logged in as {0.user}".format(client))
    await client.change_presence(activity=discord.Game(name='Use _help for help'))


@client.event
async def on_message(message):
    full_message = message.content
    split_message = full_message.split()
    if message.author == client.user:
        return

    if message.content.startswith("_hello"):
        await message.channel.send("Hello {}!".format(message.author.mention))
        await message.author.send("Greetings!")
        #await message.channel.send(discord.ext.commands.Bot.latency)
        print(message)
        print(message.content)

    elif message.content.startswith("COOL_KID_DONT_TOUCH"):
        person=message.content.split()[1]
        await message.channel.send(embed=whois(person))


    elif message.content.startswith("_zmanim"):
        place_name = " ".join(split_message[1:])
        try:
          gz = await get_zmanim(place_name)
          #await old_string= f"Zmanim for {gz["city"]}, {gz["state"]},{gz["country"]}"

          embed=discord.Embed(
            title=f'Zmanim for {gz["city"]}, {gz["state"]}, {gz["country"]}',
            color=discord.Colour.red()
          )
          embed.add_field(name="Proportional Hour", value="{} minutes".format(gz["shaot_zmaniot"]), inline=True)
          embed.add_field(name="Alos hashachar:", value=gz["alos hashachar"], inline=True)
          embed.add_field(name="Misheyakir (earliest tefilllin):", value=gz["misheyakir"], inline=False)
          embed.add_field(name="Sunrise:", value=gz["sunrise"], inline=True)
          embed.add_field(name="Sof Zeman K'reas Sh'ma:", value=gz["latest shma"], inline=True)
          embed.add_field(name="Sof Zeman T'feilah:", value=gz["latest davening"], inline=True)
          embed.add_field(name="Midday:", value=gz["chatzot"], inline=True)
          embed.add_field(name=" Mincha Gedola (Earliest Mincha):", value=gz["mincha gedola"], inline=True)
          embed.add_field(name="Mincha K'tana::", value=gz["mincha katana"], inline=True)
          embed.add_field(name="Plag HaMincha:", value=gz["plag hamincha"], inline=True)
          embed.add_field(name="Candle Lighting:", value=gz["candlelighting"], inline=True)
          embed.add_field(name="Sunset:", value=gz["sunset"], inline=True)
          embed.add_field(name="Tzais Hakochavim:", value=gz["tzais hakochavim"], inline=True)
          await message.channel.send(embed=embed)

        except:
          await message.channel.send("Something didn't go right.")

    elif message.content.startswith("_weather"):
        place_name = " ".join(split_message[1:])
        logging.debug(place_name)
        #try:
        weather_there = await get_weather(place_name)
        #weather_there = weather_two(weather_there)
        await message.channel.send(embed=weather_there)
        #except:
            #await message.channel.send("I don't know that place name.")
            #print(weather_there)

    elif message.content.startswith("_passuk"):
        await message.channel.send("Warning: This feature is in beta!")
        try:
            sefer = split_message[1]
            perek = split_message[2]
            passuk = split_message[3]
            if "-t" in message.content:
                 response = await pull_a_passuk(sefer, perek, passuk, translation=True)
            else:
                 response = await pull_a_passuk(sefer, perek, passuk, translation=False)
            logging.debug(response)
            if len(response) > 2000:
                blocks_required = math.ceil(len(response) / 2000)
                logging.debug(blocks_required)
                for i in range(blocks_required):
                    await message.channel.send(response[i * 2000:(i + 1) * 2000])
            else:
                await message.channel.send(response)
        except:
            await message.channel.send("Invalid Syntax. Must be _passuk {Book} {Perek} {Passuk}")
    elif message.content.startswith("_perek"):
        await message.channel.send("Warning: This feature is in beta!")
        if "-t" in message.content:
            translation = True
        else:
            translation = False

        try:
            sefer = split_message[1]
            perek = split_message[2]
            response = await pull_a_perek(sefer, perek, translation)

            if len(response) > 2000:
                blocks_required = math.ceil(len(response) / 2000)
                logging.debug(blocks_required)
                for i in range(blocks_required):
                    await message.channel.send(response[i * 2000:(i + 1) * 2000])
            else:
                await message.channel.send(response)
        except:
            await message.channel.send("Invalid Syntax. Must be _passuk {Book} {Perek}")
    #elif message.content.startswith("repeat repeat"):
      #await message.channel.send("repeat repeat")

    elif message.content.startswith("_help"):
        link_to=discord.Embed(
          title="ThisIsABot Help",
          description = """
    Things in brackets mean things that you should replace when using the command
    Command _hello sends a hello message
    Comand _weather [place] will output weather in that place
    Command _passuk [Book] [Perek] [Passuk] [-t]  outputs the specified passuk. Adding "-t" will add translation.
    Command _perek [Book] [Perek] [-t] outputs the specified perek Adding "-t" will add translation.
    Command _zmanim [place] will provide today's zmanim in that place. 
    There is a hidden command. Not telling you what it is...
    For help message @ computerjoe314

     """,
          color=discord.Colour.teal()
        )
        await message.channel.send(embed=link_to)

        # print(response)

        # print(message.content)
        # print(response.text)


#keep_alive()

client.run(os.getenv("TOKEN"))
