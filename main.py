import asyncio
import discord
from discord.ext import commands
import subprocess
import settings
import AvorionServer

from time import localtime, strftime
bot = commands.Bot(command_prefix="!", description="Gameserver Bot")


def is_admin():
    def invo(ctx):
        return ctx.author.id in settings.list_Admins

    return commands.check(invo)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print(bot.guilds)

    #for guild in bot.guilds:
    #    print(guild.name)
    #    #print(guild.channels)
    #    for channel in guild.channels:
    #        if channel.name == "botbay":
     #           print(channel.id)
    #            print("bay found in:"+guild.name+" "+channel.name +"-"+ str(channel.id))
   #             channel.send("Hello Master!")
    #            bot_debug = channel

    settings.bot_debug = bot.get_channel(settings.bot_debug_id)


@bot.command()
async def changename(ctx, *, name: str):
    if ctx.author.id in settings.list_Admins:
        await bot.user.edit(username=name)
        await ctx.send(ctx.author.mention + " - Changed name to: " + name)
    else:
        return

@bot.command()
@is_admin()
async def startsrv(ctx):
    tmpmsg = await ctx.send(ctx.author.mention + " - Starting server.")
    startsh = subprocess.call("./startserver.sh")

@bot.command()
async def answer(ctx):
    strAnswer = ""
    if ctx.author.id in settings.list_Admins:
        strAnswer = "Hello Master."
    else:
        strAnswer = "Hallo " + ctx.author.mention + " ich bin Avorioni."

    await log(strAnswer)
    await ctx.send(strAnswer)

@bot.command()
async def servStop(ctx):
    strText = "stoppe Avorion Server"
    await log(strText)
    await ctx.send(strText)

    try:
        AvorionServer.stop()
        strText = "Server gestopt"
        await log(strText)
        await ctx.send(strText)
    except UnicodeDecodeError:
		
@bot.command()
@is_admin()
async def servBackup(ctx):
	strText = "Erstelle Backup"
	await log(strText)
	await ctx.send(strText)
	
	try:
        AvorionServer.backup()
        strText = "Backup erstellt"
        await log(strText)
        await ctx.send(strText)
    except UnicodeDecodeError:
		strText = "Es ging etwas schief"
        await log(strText)
        await ctx.send(strText)



async def log(strLoggingText):
    strLoggingText = strftime("%Y.%m.%d %H:%M:%S", localtime()) +" - "+ strLoggingText
    print(strLoggingText)
    await settings.bot_debug.send(strLoggingText)


bot.run(settings.bot_id, loop="botloop")
