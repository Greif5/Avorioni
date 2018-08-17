import	asyncio
import	discord
from	discord.ext         import commands
import	settings
import	ArkServer
import	AvorionServer
import	FactorioServer
import	sys
from	exceptionClasses    import *
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

	settings.bot_debug = bot.get_channel(settings.bot_debug_id)

@is_admin()
@bot.command()
async def changename(ctx, *, name: str):
	if ctx.author.id in settings.list_Admins:
		await bot.user.edit(username=name)
		await ctx.send(ctx.author.mention + " - Changed name to: " + name)
	else:
		return

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
@is_admin()
async def start(ctx, *args):
	if args:
		for arg in args:
			if arg.lower() in "ark":
				if ctx.author.id in settings.list_Ark:
					try:
						ArkServer.start()
						await ctx.send("ArkServer ist gestartet")
					except Server_notStarting as e:
						await ctx.send("ArkServer konnte nicht gestartet werden")
						await ctx.send("Der Fehler lautet:```"+str(e)+"```")
					except Server_isRunning as e:
						await ctx.send("ArkServer läuft bereits")
				else:
					await ctx.send("DU darfst den Server nicht befehlen")

				return

			elif arg.lower() in "avorion":
				if ctx.author.id in settings.list_Avorion:
					await ctx.send("ist Avorion")
				else:
					await ctx.send("DU darfst den Server nicht befehlen")
				return

			elif arg.lower() in "factorio":
				if ctx.author.id in settings.list_Factorio:
					try:
						FactorioServer.start()
						await ctx.send("FactorioServer ist gestartet")
					except Server_notStarting as e:
						await ctx.send("FactorioServer konnte nicht gestartet werden")
						await ctx.send("Der Fehler lautet:```"+str(e)+"```")
					except Server_isRunning as e:
						await ctx.send("FactorioServer läuft bereits")
				else:
					await ctx.send("DU darfst den Server nicht befehlen")
				return

	await ctx.send("Bitte gib einen Server zum Starten an.")
	await ctx.send("```!start Ark|Avorion|Factorio```")


@bot.command()
@is_admin()
async def stop(ctx, *args):
	if args:
		for arg in args:
			if arg.lower() in "ark":
				if ctx.author.id in settings.list_Ark:
					try:
						ArkServer.stop()
						await ctx.send("ArkServer ist gestoppt")
					except Server_notStopping as e:
						await ctx.send("ArkServer konnte nicht gestoppt werden")
						await ctx.send("Der Fehler lautet:```"+str(e)+"```")
				else:
					await ctx.send("DU darfst den Server nicht befehlen")

				return

			elif arg.lower() in "avorion":
				if ctx.author.id in settings.list_Avorion:
					await ctx.send("ist Avorion")
				else:
					await ctx.send("DU darfst den Server nicht befehlen")

				return

			elif arg.lower() in "factorio":
				if ctx.author.id in settings.list_Factorio:
					try:
						FactorioServer.stop()
						await ctx.send("FactorioServer ist gestoppt")
					except Server_notStopping as e:
						await ctx.send("FactorioServer konnte nicht gestoppt werden")
						await ctx.send("Der Fehler lautet:```"+str(e)+"```")
				else:
					await ctx.send("DU darfst den Server nicht befehlen")

				return

	await ctx.send("Bitte gib einen Server zum Stoppen an.")
	await ctx.send("```!stop Ark|Avorion|Factorio```")


@bot.command()
@is_admin()
async def save(ctx, *args):
	if args:
		for arg in args:
			if arg.lower() in "ark":
				try:
					ArkServer.save()
					await ctx.send("ArkServer wurde gesichert")
				except Server_notRunning as e:
					await ctx.send("ArkServer konnte nicht gesichert werden")
					await ctx.send("Der Fehler lautet:```"+str(e)+"```")
				return

			elif arg.lower() in "avorion":
				await ctx.send("ist Avorion")
				return

			elif arg.lower() in "factorio":
				try:
					FactorioServer.save()
					await ctx.send("FactorioServer wurde gesichert")
				except Server_notRunning as e:
					await ctx.send("FactorioServer konnte nicht gesichert werden")
					await ctx.send("Der Fehler lautet:```"+str(e)+"```")
				return

	await ctx.send("Bitte gib einen Server zum Sichern an.")
	await ctx.send("```!save Ark|Avorion|Factorio```")


async def log(strLoggingText):
	if any(strElement in ("-l", "--logging") for strElement in sys.argv):
		strLoggingText = strftime("%Y.%m.%d %H:%M:%S", localtime()) +" - "+ strLoggingText
		print(strLoggingText)
		await settings.bot_debug.send(strLoggingText)

bot.run(settings.bot_id, loop="botloop")