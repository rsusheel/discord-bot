

# Discord bot


################### BOT ###################

# importing libraries
from calendar import month
from dis import disco
from lib2to3.pgen2 import driver
import discord                                      # discord API
from discord.ext import commands, tasks             # to use bot commands
import os                                           # to access OS file system
import requests                                     # to send HTTP requests
import json                                         # to process JSON files
import time                                         # for sleep delay
import datetime                                     # for the timestamp
from dateutil.relativedelta import relativedelta
from selenium import webdriver                      # to use chrome web driver
from PIL import Image, ImageOps                     # to edit images 
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from tinydb import TinyDB, Query
db=TinyDB('symbols.json')
user=Query()


GOOGLE_CHROME_PATH = '/app/.apt/opt/google/chrome/google-chrome'
CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = GOOGLE_CHROME_PATH

################### LIST OF FUNCTIONS ###################

# FUNCTION: captureScreenshot
# INFO: function to visit Trading View web app and automate clicks to set the dark mode get the screenshot and save the screenshot by cropping it
# related to command 'ci'
def captureScreenshot(currency):

  # driver initialization
  # driver = webdriver.Chrome(os.getcwd()+"\chromedriver.exe")

  # access web page
  # url="https://www.tradingview.com/chart/?symbol=BINANCE%3A"+currency.upper()+"USDT"
  # driver.get(url)

  driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
  url="https://www.tradingview.com/chart/?symbol=BINANCE%3A"+currency.upper()+"USDT"
  driver.get(url)

  # web browser placement
  driver.execute_script("document.body.style.zoom='100%'")
  driver.set_window_size(1920,1080,driver.window_handles[0])
  driver.maximize_window()

  # web page auto clicks
  driver.find_element_by_class_name('content-1UNGmyXO').click()     # remove cookies box
  time.sleep(5)                                                     # sleep for 5 sec to let page load
  driver.find_element_by_class_name('button-2WfzAPA-').click()      # click on menu button
  driver.find_element_by_class_name('switcher-2WfzAPA-').click()    # click on dark mode
  driver.find_element_by_class_name('button-2WfzAPA-').click()      # click on menu button
  time.sleep(1)                                                     # sleep for 1 sec to let the screenshot take

  # capture screenshot and save the image as 'image.png' and close the browser
  driver.save_screenshot("images/image.png")
  driver.close()

  # image manipulation
  im = Image.open('images/image.png')                           # uses PIL library to open image in memory
  im = im.crop((72,50,1508,822))                         # defines crop points
  img = ImageOps.expand(im,border=8,fill='#F1C40F')     # adds border to image
  img.save('images/screenshot.png')                             # saves new cropped image


# FUNCTION: getCurrencyInfo
# INFO: function to get the info of the currency
# related to command 'cc'
def getCurrencyInfo(currency):

  # get JSON info of the currency
  url="https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids="+currency
  response = requests.get(url)
  json_data = json.loads(response.text)[0]
  curr_info=json_data
  
  # currency info items
  price = "**"+"{:,}".format(curr_info["current_price"])+" USD** "+"*("+"{:.2f}".format(curr_info["price_change_percentage_24h"])+"%)*"
  image=curr_info["image"]
  symbol=curr_info["symbol"]
  marketCap="{:,}".format(curr_info["market_cap"])
  marketCapAlt=int(curr_info["market_cap"])
  marketCapRank=curr_info["market_cap_rank"]
  high24="{:,}".format(curr_info["high_24h"])+" USD"
  low24="{:,}".format(curr_info["low_24h"])+" USD"
  
  # market cap suffix (million/billion/trillion)
  if marketCapAlt>=1000000 and marketCapAlt<1000000000:
      marketCapAltFinal=str(marketCapAlt//1000000)+"M"                 # suffix for million

  if marketCapAlt>=1000000000 and marketCapAlt<1000000000000:
      marketCapAltFinal=str(marketCapAlt//1000000000)+"B"              # suffix for billion

  if marketCapAlt>=1000000000000 and marketCapAlt<1000000000000000:
      marketCapAltFinal=str(marketCapAlt//1000000000000)+"T"           # suffix for trillion

  # final embed info
  finalEmbed={"price":price, "image":image, "symbol":symbol, "marketCap": marketCap,"marketCapAlt":marketCapAltFinal, "marketCapRank":marketCapRank, "high24":high24, "low24":low24}
  
  return finalEmbed


# FUNCTION: createEmbed
# INFO: creates embed for the information provided
# related to command 'cc'
def createEmbed(crr):
  crrid=db.search(user.symbol==crr)[0]["id"]
  det=getCurrencyInfo(crrid)
  embed = discord.Embed()
  embed.set_author(name=crrid.upper()[0]+crrid[1:].lower(), icon_url=det["image"])
  embed.set_thumbnail(url=det["image"])
  embed.description = "Symbol: *"+det["symbol"].upper()+"*"
  embed.title = det["price"]
  embed.add_field(name="Market Cap", value=det["marketCapAlt"]+" USD *($"+det["marketCap"]+")*", inline=True)
  embed.add_field(name="Market Cap Rank", value="Rank: "+str(det["marketCapRank"]), inline=False)
  embed.add_field(name="24h High", value=det["high24"], inline=True)
  embed.add_field(name="24h Low", value=det["low24"], inline=True)
  embed.set_footer(text="CoinGecko ("+str(datetime.datetime.now().strftime("%c"))+")")
  embed.colour = 0xF1C40F
  return embed


def historicalData(crr, days):
  if days[-1]=='d':
    days=int(days[0:-1])
    date=datetime.date.today() - relativedelta(days=days)
  elif days[-1]=='w':
    weeks=int(days[0:-1])
    date=datetime.date.today() - relativedelta(weeks=weeks)
  elif days[-1]=='m':
    months=int(days[0:-1])
    date=datetime.date.today() - relativedelta(months=months)
  elif days[-1]=='y':
    years=int(days[0:-1])
    date=datetime.date.today() - relativedelta(years=years)
  else:
    date=datetime.date.today() - datetime.timedelta(days=int(days))
  date=date.strftime('%d-%m-%Y')
  # get JSON info of the currency
  url="https://api.coingecko.com/api/v3/coins/"+crr+"/history?date="+date
  response = requests.get(url)
  jsonData = json.loads(response.text)
  thenPrice = jsonData["market_data"]["current_price"]["usd"]
  thumb=jsonData["image"]["thumb"]
  
  newUrl="https://api.coingecko.com/api/v3/simple/price?ids="+crr+"&vs_currencies=usd"
  newResponse=requests.get(newUrl)
  newJsonData=json.loads(newResponse.text)
  newPrice=newJsonData[crr]["usd"]

  coin=jsonData["id"]
  symbol=jsonData["symbol"]

  roi=(newPrice-thenPrice)*100/thenPrice

  dataJson={
    "id": coin,
    "symbol": symbol,
    "roi": roi,
    "thenPrice": "{:,}".format(round(thenPrice,2))+" USD",
    "newPrice": "{:,}".format(round(newPrice,2))+" USD",
    "date": date,
    "thumb": thumb,
  }

  return dataJson



################### BOT COMMANDS ###################

# set the bot command prefix, PREFIX: 'c'
bot = commands.Bot(command_prefix='/')


# COMMAND: 'c'
# FULL COMMAND: 'cc'
# INFO: creates an embed and sends as response to the command
# USE: 'cc [currency_name/surrency_symbol]'
@bot.command()
async def info(ctx, crr: str):
  embed=createEmbed(crr)
  await ctx.send(embed=embed)


# COMMAND: 'i'
# FULL COMMAND: 'ci'
# INFO: fetches the screenshot from captureScreenshot function and sends the image as response fro the command
# USE: 'ci [currency_name/currency_symbol]'
@bot.command()
async def chart(ctx, crr: str):
  captureScreenshot(crr)
  # driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
  # url="https://www.tradingview.com/chart/?symbol=BINANCE%3A"+crr.upper()+"USDT"
  # driver.get(url)
  # a=driver.page_source
  await ctx.send(file=discord.File('images/screenshot.png'))


@bot.command()
async def hist(ctx, crr: str, days: str):
  crrid=db.search(user.symbol==crr)[0]["id"]
  dataJson=historicalData(crrid, days)
  roi="{:,}".format(round(dataJson["roi"],2))+"%"
  newPrice=dataJson["newPrice"]
  thenPrice=dataJson["thenPrice"]
  date=dataJson["date"]
  thumb=dataJson["thumb"]
  embed=discord.Embed()
  embed.set_author(name="Gains (from: "+date+")", icon_url=thumb)
  embed.title=roi
  embed.description=dataJson["id"][0].upper()+dataJson["id"][1:]+" - *"+dataJson["symbol"].upper()+"*"
  embed.add_field(name="Price Then", value=thenPrice)
  embed.add_field(name="Price Now", value=newPrice)
  embed.set_footer(text="Today ("+str(datetime.datetime.now().strftime("%c"))+")")
  embed.colour = 0xF1C40F
  await ctx.send(embed=embed)
  

# COMMAND: 'mf'
# FULL COMMAND: 'cmf'
# INFO: calculates average maturity amount for certain mutual funds parameters
# USE: 'cmf [monthly | time | interest | principle]'
@bot.command()
async def sip(ctx, monthly: int, time: int, interest: int, principle: int):
  # formula from: 'https://www.thecalculatorsite.com/articles/finance/compound-interest-formula.php'
  # Future value of series: PMT × {[(1 + r/n)^(nt) - 1] / (r/n)}
  # CI for principle: P(1+r/n)^(nt)
  # total amount is sum of above two
  x=interest/(100*12)
  y=1+x
  matureSum=(principle*(pow(y,12*time)))+(monthly*((pow(y,12*time)-1)/x))+(monthly*(pow(y,12*time)))-monthly
  amount="{:,}".format(round(matureSum,2))
  embed=discord.Embed()
  embed.set_author(name="Monthly Compounded Interest", icon_url="https://clipground.com/images/arrow-up-clipart-20.jpg")
  embed.title="₹ "+str(amount)
  embed.colour = 0xF1C40F
  embed.add_field(name="Monthly", value="₹ "+"{:,}".format(monthly), inline=True)
  embed.add_field(name="Time", value=str(time)+" yrs", inline=True)
  embed.add_field(name="Interest", value=str(interest)+"% p.a.", inline=True)
  embed.add_field(name="Principle", value="₹ "+"{:,}".format(principle), inline=False)
  embed.add_field(name="Overall Investment", value="₹ "+"{:,}".format(round((monthly*time*12)+principle),2), inline=True)
  embed.add_field(name="Overall Interest", value="₹ "+"{:,}".format(round(matureSum-((monthly*time*12)+principle),2)))
  await ctx.send(embed=embed)


@bot.command()
async def insul(ctx):
  url="https://evilinsult.com/generate_insult.php?lang=en&type=json"
  response = requests.get(url)
  jsonData = json.loads(response.text)
  insult=jsonData["insult"]
  await ctx.send(insult)


@tasks.loop(minutes=30)
async def cointelegraph():
  tt=datetime.datetime.now().timestamp()
  lastUpdated=tt-1800
  ch=bot.get_channel(924979491409911838)
  url="https://rss-to-json-serverless-api.vercel.app/api?feedURL=https://cointelegraph.com/rss"
  response = requests.get(url)
  for i in range(len(json.loads(response.text)["items"])):
    jsonData = json.loads(response.text)["items"][i]
    timestamp=int(str(jsonData["published"])[0:-3])
    if timestamp<lastUpdated:
      break
    title=jsonData["title"]
    link=jsonData["link"]
    author=jsonData["author"][17:]
    description=jsonData["description"]
    image=jsonData["enclosures"][0]["url"]
    soup=BeautifulSoup(description, "html.parser")
    soup=soup.find_all('p')[1]
    embed=discord.Embed(title=title, url=link)
    embed.set_author(name="Cointelegraph", url="https://cointelegraph.com", icon_url="https://cointelegraph.com/assets/img/repostlogo.jpg")
    embed.description=str(soup)[3:-4]
    embed.set_image(url=image)
    embed.colour = 0xF1C40F
    footer="By "+author+" ("+datetime.datetime.fromtimestamp(timestamp).strftime("%d %B, %Y, %H:%M")+" GMT)"
    embed.set_footer(text=footer)
    await ch.send(embed=embed)

@cointelegraph.before_loop
async def before():
    await bot.wait_until_ready()
    print("Finished waiting")

cointelegraph.start()

################### RUN THE BOT ###################
token=os.environ.get("BOT_TOKEN")
bot.run(token)