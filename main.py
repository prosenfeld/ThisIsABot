import discord
import os
import math
import logging
from datetime import datetime, timedelta
from aiohttp import ClientSession
import feedparser
import random
import requests
from bs4 import BeautifulSoup

# from keep_alive import keep_alive
import unicodedata
from keep_alive import keep_alive
from discord.ext import commands

# ךogging.basicConfig(level=logging.DEBUG)


logger = logging.getLogger('discord')
logging.basicConfig(filename='discord.log' , level=logging.DEBUG, format='(asctime)s:%(levelname)s:%(name)s: %(message)s')
print("sanity test")
logging.warning("sanity test")

client = commands.Bot(command_prefix="_", help_command=None)
map_key = os.getenv("MAPBOX_KEY")

def find_xkcd():
    comics = feedparser.parse("https://xkcd.com/rss.xml")
    summary = comics['entries'][0]["summary"]
    xkcd_number = comics ['entries'][0]["links"][0]["href"].split("/")[-2]
    xkcd_url= summary[summary.find("src=")+5:summary.find(".png")+4]
    xkcd_text= summary[summary.find("alt=")+5:summary.find("src=")-2]
    return xkcd_text,xkcd_url,xkcd_number


def get_xkcd_by_number(number):
    xkcd = requests.get("http://xkcd.com/{}".format(number))
    soup = BeautifulSoup(xkcd.text)
    comic = soup.find("div", {"id": "comic"}).img['src'][2:]
    comic="https://"+comic
    text = soup.find("div", {"id": "comic"}).img['title']
    return comic,text,number


# async def ping(channel):
#    await channel.send(f'pong!\n{round(bot.latency * 1000)}ms')
# def whois(member: discord.Member):
#    embed=discord.Embed()
#    user = discord.get_member(member)
#    embed.set_thumbnail(url=user.avatar_url)
#    return embed
async def get_weather(place="Washington DC"):
    async with ClientSession() as session:
        place = place.lower()
        response = await session.request(method='GET',
                                         url=f"https://weather.ls.hereapi.com/weather/1.0/report.json?apiKey={map_key}&product=observation&name={place}")
        response_json = await response.json()
        logging.debug(response_json)
        print(response_json)
        new_json = response_json
        temp = new_json["observations"]["location"][0]["observation"][0]["temperature"]
        desc = new_json["observations"]["location"][0]["observation"][0]["description"]
        real_city_name = new_json["observations"]["location"][0]["observation"][0]["city"]
        real_city_country = new_json["observations"]["location"][0]["observation"][0]["country"]
        real_city_state = new_json["observations"]["location"][0]["observation"][0]["state"]
        wind_speed= new_json["observations"]["location"][0]["observation"][0]["windSpeed"]
        wind_direction= new_json["observations"]["location"][0]["observation"][0]["windDesc"]
        wind_direction_long=new_json["observations"]["location"][0]["observation"][0]["windDirection"]
        print(wind_direction_long)
        
        # print(f"In {place} it is currently {temp} degrees C ({(float(temp)*1.8)+32}F) and  {desc}.")
        embed = discord.Embed(
            title=f'Weather for {real_city_name}, {real_city_state}, {real_city_country} ',
            description=f"Currently {temp} degrees C ({round((float(temp) * 1.8) + 32, 2)} F) and  {desc}. \n Wind {wind_speed} km/h ({round(float(wind_speed)*0.6213,2)} mph) from the {wind_direction} ({wind_direction_long}°).",
            color=discord.Colour.red()
        )
        embed.set_thumbnail(
            url=new_json["observations"]["location"][0]["observation"][0]["iconLink"] + f"?apikey={map_key}")
        
        print(new_json["observations"]["location"][0]["observation"][0]["iconLink"])
        # return (
        # f"In {real_city_name}, {real_city_state}, {real_city_country} it is currently {temp} degrees C ({round((float(temp) * 1.8) + 32, 2)} F) and  {desc}.")
        return embed
        # return (
        # f"In {real_city_name}, {real_city_state}, {real_city_country} it is currently {temp} degrees C ({round((float(temp) * 1.8) + 32, 2)} F) and  {desc}.")


async def pull_a_passuk(sefer, perek, passuk, translation=False):
    async with ClientSession() as session:
        get_text = await session.request(method='GET',
                                         url=f"https://www.sefaria.org/api/texts/{sefer}.{perek}.{passuk}?context=0 ")
        json_of_txt = await get_text.json()
        logging.debug(json_of_txt)
        nikudnik = json_of_txt["he"]

        if translation:
            give_translation = json_of_txt["text"]
            normalized = unicodedata.normalize("NFKD", nikudnik)
            flattened = "".join([c for c in normalized if not unicodedata.combining(c)])
            flattened = flattened.replace("(פ)", "")
            flattened = flattened.replace("(ס)", "")
            give_translation = give_translation.replace("<i>", " ").replace("</i>", " ").replace("<b>", " ").replace(
                "</b>", " ")
            return flattened + "\n " + give_translation
        else:
            normalized = unicodedata.normalize("NFKD", nikudnik)
            flattened = "".join([c for c in normalized if not unicodedata.combining(c)])
            flattened = flattened.replace("(פ)", "")
            flattened = flattened.replace("(ס)", "")
            return flattened


async def pull_a_perek(sefer, perek, translation):
    async with ClientSession() as session:
        get_text = await session.request(method='GET',
                                         url=f"https://www.sefaria.org/api/texts/{sefer}.{perek}?context=0")
        json_of_txt = await get_text.json()
        logging.debug(json_of_txt)
        if translation:
            nikudnik = "".join(json_of_txt["he"])
            normalized = unicodedata.normalize("NFKD", nikudnik)
            flattened = "".join([c for c in normalized if not unicodedata.combining(c)])
            logging.debug(flattened)
            give_translation = "".join(json_of_txt["text"])
            give_translation = give_translation.replace("<i>", " ").replace("</i>", " ").replace("<b>", " ").replace(
                "</b>", " ")
            return flattened + give_translation.replace("<i></i>", "")
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


async def get_zmanim(place: str):
    async with ClientSession() as session:
        relevant_results = {}
        pulled_timing = await session.request(method='GET',
                                              url=f"https://weather.ls.hereapi.com/weather/1.0/report.json?apiKey={map_key}&product=forecast_astronomy&name={place}")
        new_json = await pulled_timing.json()
        print(new_json)
        relevant_results["city"] = new_json["astronomy"]["city"]
        relevant_results["state"] = new_json["astronomy"]["state"]
        relevant_results["country"] = new_json["astronomy"]["country"]
        relevant_results["sunrise"] = new_json["astronomy"]["astronomy"][0]["sunrise"]
        relevant_results["sunset"] = new_json["astronomy"]["astronomy"][0]["sunset"]

        sunrise = relevant_results["sunrise"][:-2]
        sunset = relevant_results["sunset"][:-2]
        hours = sunset[:-2].replace(":", "")
        minutes = sunset[-2:]
        sunset = str(int(hours) + 12) + minutes
        sunset = sunset[:-2] + ":" + sunset[-2:]
        FMT = '%H:%M'
        tdelta = datetime.strptime(sunset, FMT) - datetime.strptime(sunrise, FMT)
        sunset = datetime.strptime(sunset, FMT)
        sunrise = datetime.strptime(sunrise, FMT)

        shaot_zmaniot = tdelta / 12
        shaot_zmaniot_convert = round(shaot_zmaniot.seconds / 60, 4)
        relevant_results["shaot_zmaniot"] = shaot_zmaniot_convert

        chatzot = shaot_zmaniot * 6 + sunrise
        relevant_results["chatzot"] = (shaot_zmaniot * 6 + sunrise).strftime('%H:%M')

        alos = sunrise - timedelta(minutes=72)
        relevant_results["alos hashachar"] = datetime.strftime(alos, "%H:%M")

        tzais = sunset + timedelta(minutes=45)
        relevant_results["tzais hakochavim"] = datetime.strftime(tzais, "%H:%M")

        latest_davening = (shaot_zmaniot * 4 + sunrise).strftime('%H:%M')
        relevant_results["latest davening"] = latest_davening

        mincha_gedola = (shaot_zmaniot * 0.5) + chatzot
        relevant_results["mincha gedola"] = mincha_gedola.strftime("%H:%M")

        candlelighting = sunset - timedelta(minutes=18)
        relevant_results["candlelighting"] = candlelighting.strftime("%H:%M")

        mincha_katana = sunset - (shaot_zmaniot * 2.5)
        relevant_results["mincha katana"] = mincha_katana.strftime("%H:%M")

        plag = sunset - (shaot_zmaniot * 1.25)
        relevant_results["plag hamincha"] = plag.strftime("%H:%M")

        latest_shma = sunrise + (shaot_zmaniot * 3)
        relevant_results["latest shma"] = latest_shma.strftime("%H:%M")

        misheyakir = sunrise - timedelta(minutes=45)
        relevant_results["misheyakir"] = misheyakir.strftime("%H:%M")

        return relevant_results


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    logging.info("We have logged in as {0.user}".format(client))
    await client.change_presence(activity=discord.Game(name='Use _help for help'))


@client.command()
async def hello(ctx):
    print(ctx)
    await ctx.message.author.send("Greetings!")
    await ctx.send("Hello {}".format(ctx.message.author.mention))


@client.command()
async def zmanim(ctx):
    split_message = ctx.message.content.split()
    print(split_message)
    place_name = " ".join(split_message[1:])
    try:
        gz = await get_zmanim(place_name)
        print(gz)
        # await old_string= f"Zmanim for {gz["city"]}, {gz["state"]},{gz["country"]}"

        embed = discord.Embed(
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
        await ctx.send(embed=embed)

    except:
        await ctx.send("Something didn't go right.")


@client.command()
async def weather(ctx):
    try:
        split_message = ctx.message.content.split()
        place_name = " ".join(split_message[1:])
        logging.debug(place_name)
        # try:
        weather_there = await get_weather(place_name)
        await ctx.send(embed=weather_there)
    except:
        await ctx.send("Something didn't go right.")


@client.command()
async def passuk(ctx):
    split_message = ctx.message.content.split()
    try:
        sefer = split_message[1]
        perek = split_message[2]
        passuk = split_message[3]
        if "-t" in ctx.message.content:
            response = await pull_a_passuk(sefer, perek, passuk, translation=True)
        else:
            response = await pull_a_passuk(sefer, perek, passuk, translation=False)
        logging.debug(response)
        if len(response) > 1994:
            blocks_required = math.ceil(len(response) / 1994)
            logging.debug(blocks_required)
            for i in range(blocks_required):
                await ctx.send("```"+response[i * 1994:(i + 1) * 1994]+"```")
        else:
            await ctx.send("```"+response+"```")
    except:
        await ctx.send("Invalid Syntax. Must be _passuk {Book} {Perek} {Passuk}")


@client.command()
async def perek(ctx):
    split_message = ctx.message.content.split()
    if "-t" in ctx.message.content:
        translation = True
    else:
        translation = False

    try:
        sefer = split_message[1]
        perek = split_message[2]
        response = await pull_a_perek(sefer, perek, translation)

        if len(response) > 1994:
            blocks_required = math.ceil(len(response) / 1994)
            logging.debug(blocks_required)
            for i in range(blocks_required):
                await ctx.send("```"+response[i * 1994:(i + 1) * 1994]+"```")
        else:
            await ctx.send("```"+response+"```")
    except:
        await ctx.send("Invalid Syntax. Must be _passuk {Book} {Perek}")


@client.command()
async def help(ctx):
    link_to = discord.Embed(
        title="ThisIsABot Help",
        description="""
        Things in brackets mean things that you should replace when using the command
        Command _hello sends a hello message
        Comand _weather [place] will output weather in that place
        Command _passuk [Book] [Perek] [Passuk] [-t]  outputs the specified passuk. Adding "-t" will add translation.
        Command _perek [Book] [Perek] [-t] outputs the specified perek Adding "-t" will add translation.
        Command _zmanim [place] will provide today's zmanim in that place.
        Command _echo [Message] echos.
        Command _xkcd [random][number] will send the latest xkcd. Adding random will make it a random xkcd. Putting a number instead will give the xkcd of that number.
        There is a hidden command. Not telling you what it is... :-)
        For help message @ computerjoe314

         """,
        color=discord.Colour.teal()
    )
    await ctx.send(embed=link_to)


@client.command()
async def explode(ctx):
  try:
    await ctx.message.delete()
  except:
    pass
  await ctx.send(":brain: \n :exploding_head:")


@client.command()
async def echo(ctx):
  try:
    await ctx.message.delete()
  except:
    pass
  print(str(ctx.message.content.split()[1:]))
  await ctx.send(ctx.message.author.mention + " says " + " ".join(ctx.message.content.split()[1:]))

@client.command()
async def xkcd(ctx):
  message = ctx.message.content
  try:
    if "random" in message.lower():
      total_xkcds=find_xkcd()[2]
      random_xkcd = get_xkcd_by_number(random.randint(0,int(total_xkcds)))
      await ctx.send(random_xkcd[0])
      await ctx.send(random_xkcd[1]+" - (XKCD #"+str(random_xkcd[2])+")")
    elif len(message.split()) > 1 and message.split()[1].isdigit():
      specific_xkcd = get_xkcd_by_number(int(message.split()[1]))
      await ctx.send(specific_xkcd[0])
      await ctx.send(specific_xkcd[1]+" - (XKCD #"+str(specific_xkcd[2])+")")
    else:
      latest = find_xkcd()
      await ctx.send(latest[1])
      await ctx.send(latest[0]+" - (XKCD #"+str(latest[2])+")")
  except Exception:
    await ctx.send("Something did work. ")
    print("Something failed: " + Exception)


keep_alive()
client.run(os.getenv("TOKEN"))
