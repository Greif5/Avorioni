from 	time 				import localtime, strftime
from	discord.ext			import commands
from	exceptionClasses	import *
import	asyncio
import	atexit
import	discord
import	ArkServer
import	AvorionServer
import	FactorioServer
import	os
import	sys
import	settings


"""
Parameter:

-c	--clear
	deletes Lockfile, exits.
	
-f	--force
	forces start even with existing lockfile
	
-l	--logging
	logs stuff

"""

if any(strElement in ("-c", "--clear") for strElement in sys.argv):
	try:
		os.remove(settings.LockFile)
		print("Lockfile entfernt")
	except Exception as ex:
		print("Lockfile konnte nicht entfernt werden" + str(ex))
	sys.exit()

if os.path.isfile(settings.LockFile):
	if not any(strElement in ("-f", "--force") for strElement in sys.argv):
		print("Server läuft bereits.")
		sys.exit()
else:
	f = open(settings.LockFile, "w+")
	f.close()


bot = commands.Bot(command_prefix="!", description="Gameserver Bot")

"""
**************************************************************************************
Bot only Funktions
**************************************************************************************
"""


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
async def backup(ctx, *args):
	if args:
		for arg in args:
			if arg.lower() in "avorion":
				if ctx.author.id in settings.list_Avorion:
					await ctx.send("ist Avorion")
				else:
					await ctx.send("DU darfst den Server nicht befehlen")
				return

			elif arg.lower() in "factorio":
				if ctx.author.id in settings.list_Factorio:
					try:
						await ctx.send(	"FactorioServer wird gesichert\nDies kann einige Sekunden dauern.")
						FactorioServer.backup(1)
						await ctx.send("FactorioServer wurde gesichert")
					except Server_notStarting as e:
						await ctx.send("FactorioServer konnte nicht gestartet werden")
						await ctx.send("Der Fehler lautet:```"+str(e)+"```")
					except Server_notStopping as e:
						await ctx.send("FactorioServer konnte nicht gestoppt werden")
						await ctx.send("Der Fehler lautet:```" + str(e) + "```")
					except Server_BackupFailed as e:
						await ctx.send("FactorioServer konnte nicht gesichert werden")
						await ctx.send("Bitte schau im Log nach dem Fehler.")
				else:
					await ctx.send("DU darfst den Server nicht befehlen")
				return

	await ctx.send("Bitte gib einen Server zum Sichern an.")
	await ctx.send("```!backup Avorion|Factorio```")


@bot.command()
async def start(ctx, *args):
	if args:
		for arg in args:
			if arg.lower() in "ark":
				if ctx.author.id in settings.list_Ark:
					try:
						ArkServer.start()
						await ctx.send("ArkServer wird gestartet")

						for i in range(42):
							print(ArkServer.isStarted())
							if ArkServer.isStarted():
								await ctx.send("ArkServer ist gestartet")
								return
							await asyncio.sleep(10)
						await ctx.send("Der ArkServer braucht unerwartet lange zum starten")

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
					try:
						await ctx.send("Der AvorionServer wird gestartet")
						AvorionServer.start()
					
					except Server_notStarting as e:
						await ctx.send("Der AvorionServer konnte nicht gestartet werden")
						await ctx.send("Der Fehler lautet:```"+str(e)+"```")
					except Server_isRunning as e:
						await ctx.send("Der AvorionServer läuft bereits")
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
					try:
						AvorionServer.stop()
					except Sever_notStopping as e:
						await ctx.send("Der AvorionServer konnte nicht gestoppt werden")
						await ctx.send("Der Fehler lautet:```"+str(e)+"```")
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
				try:
					AvorionServer.save()
				except RCON_error as e:
					await ctx.send("Es gab einen Fehler!")
					await ctx.send("Der Fehler lautet:```"+str(e)+"```")
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


@bot.command()
async def status(ctx, *args):
	if args:
		for arg in args:
			if arg.lower() in "ark":
				try:
					await ctx.send(ArkServer.status())
				except Server_notRunning as e:
					await ctx.send("ArkServer läuft nicht")
					await ctx.send("Der Fehler lautet:```"+str(e)+"```")
				return

			elif arg.lower() in "avorion":
				await ctx.send("Avorion hat diese Funktion noch nicht")
				return

			elif arg.lower() in "factorio":
				try:
					await ctx.send(FactorioServer.status())
				except Server_notRunning as e:
					await ctx.send("FactorioServer läuft nicht")
					await ctx.send("Der Fehler lautet:```"+str(e)+"```")
				return

	await ctx.send("Bitte gib einen Server zum Sichern an.")
	await ctx.send("```!status Ark|Avorion|Factorio```")


@is_admin()
@bot.command()
async def kill(ctx):
	await ctx.send("Yes Master.")
	await bot.close()

"""
**************************************************************************************
Python only Funktions
**************************************************************************************
"""


def exit_Kontroll():
	try:
		os.remove(settings.LockFile)
	except Exception as e:
		print("Lockfile konnte nicht entfernt werden" + str(e))


async def log(strLoggingText):
	if any(strElement in ("-l", "--logging") for strElement in sys.argv):
		strLoggingText = strftime("%Y.%m.%d %H:%M:%S", localtime()) +" - "+ strLoggingText
		print(strLoggingText)
		await settings.bot_debug.send(strLoggingText)


atexit.register(exit_Kontroll)
bot.run(settings.bot_id, loop="botloop")
