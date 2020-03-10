from time import localtime, strftime
from discord.ext import commands
from exceptionClasses import *
import asyncio
import atexit
import discord
from ArkServer import ArkServer
import AvorionServer
import FactorioServer
import os
import sys
import settings


# Parameter:
# -c	--clear
# deletes Lockfile, if it exits.
#
# -f	--force
# forces start even with existing lockfile
#
# -l	--logging
# 		logs stuff
def parseCallArguments():
	if any(strElement in ("-c", "--clear") for strElement in sys.argv):
		try:
			if os.path.isfile(settings.LockFile):
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


# **************************************************************************************
# Python only Funktions
# **************************************************************************************
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


if __name__ == '__main__':
	parseCallArguments()
	bot = commands.Bot(command_prefix="!", description="Gameserver Bot")
	atexit.register(exit_Kontroll)


# **************************************************************************************
# Bot only Funktions
# **************************************************************************************
def is_admin():
	def invo(ctx):
		return ctx.author.id in settings.list_Admins

	return commands.check(invo)


@bot.event
async def on_ready():
	await avorioniHandler.on_ready()


@bot.command()
async def backup(ctx, *args):
	await avorioniHandler.backup(ctx=ctx, *args)


@bot.command()
async def start(ctx, *args):
	await avorioniHandler.start(ctx=ctx, *args)


@bot.command()
async def test(ctx, arg):
	await ctx.send(arg)
	await avorioniHandler.status(ctx, arg)


@bot.command()
async def stop(ctx, *args):
	await avorioniHandler.stop(ctx=ctx, *args)


@bot.command()
async def save(ctx, *args):
	await avorioniHandler.save(ctx=ctx, *args)


@bot.command()
async def status(ctx, args):
	print(ctx)
	print(args)
	await avorioniHandler.status(ctx=ctx, *args)


@is_admin()
@bot.command()
async def kill(ctx):
	await avorioniHandler.kill(ctx=ctx)


@is_admin()
@bot.command()
async def changename(self, ctx, *, name: str):
	await bot.user.edit(username=name)
	await ctx.send(ctx.author.mention + " - Changed name to: " + name)


class Avorioni:
	def __init__(self):
		self.handleArk = ArkServer()

	async def on_ready(self):
		print('Logged in as')
		print(bot.user.name)
		print(bot.user.id)
		print('------')
		print("loaded Server:")
		print(self.handleArk)
		print(bot.guilds)

		settings.bot_debug = bot.get_channel(settings.bot_debug_id)

	async def backup(self, ctx, *args):
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

	async def start(self, ctx, *args):
		try:
			if args:
				for arg in args:
					if arg.lower() in "ark":
						self.handleArk.start(userId=ctx.author.id)
						await ctx.send("ArkServer wird gestartet")

						for i in range(42):
							print(self.handleArk.isStarted())
							if self.handleArk.isStarted():
								await ctx.send("ArkServer ist gestartet")
								return
							await asyncio.sleep(10)
						await ctx.send("Der ArkServer braucht unerwartet lange zum starten")
					elif arg.lower() in "avorion":
						if ctx.author.id in settings.list_Avorion:
							try:
								await ctx.send("Der AvorionServer wird gestartet")
								AvorionServer.start()

							except Server_notStarting as e:
								await ctx.send("Der AvorionServer konnte nicht gestartet werden")
								await ctx.send("Der Fehler lautet:```"+str(e)+"```")
							except Server_isRunning:
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
			else:
				await ctx.send("Bitte gib einen Server zum Starten an.")
				await ctx.send("```!start Ark|Avorion|Factorio```")
		except Server_notStarting as e:
			await ctx.send("Server konnte nicht gestartet werden")
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")
		except Server_isRunning:
			await ctx.send("Server läuft bereits")
		except NoRights:
			await ctx.send("DU darfst den Server nicht befehlen")

	async def stop(self, ctx, args):
		try:
			if args:
				for arg in args:
					if arg.lower() in "ark":
						self.handleArk.stop(userId=ctx.author.id)
						await ctx.send("ArkServer ist gestoppt")
						return

					elif arg.lower() in "avorion":
						if ctx.author.id in settings.list_Avorion:
							try:
								AvorionServer.stop()
							except Server_notStopping as e:
								await ctx.send("Der AvorionServer konnte nicht gestoppt werden")
								await ctx.send("Der Fehler lautet:```"+str(e)+"```")
						else:
							await ctx.send("DU darfst den Server nicht befehlen")

						return

					elif arg.lower() in "factorio":
						if ctx.author.id in settings.list_Factorio:
							FactorioServer.stop()
							await ctx.send("FactorioServer ist gestoppt")
						else:
							await ctx.send("DU darfst den Server nicht befehlen")
						return
			else:
				await ctx.send("Bitte gib einen Server zum Stoppen an.")
				await ctx.send("```!stop Ark|Avorion|Factorio```")
		except Server_notStopping as e:
			await ctx.send("Server konnte nicht gestoppt werden")
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")
		except NoRights:
			await ctx.send("DU darfst den Server nicht befehlen")

	async def save(self, ctx, args):
		if args:
			for arg in args:
				if arg.lower() in "ark":
					try:
						self.handleArk.save(userId=ctx.author.id)
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

	async def status(self, ctx, args):
		try:
			if args:
				for arg in args:
					if arg.lower() in "ark":
						try:
							await ctx.send(self.handleArk.status(userId=ctx.author.id))
						except Server_notRunning as e:
							await ctx.send("ArkServer läuft nicht")
							await ctx.send("Der Fehler lautet:```" + str(e) + "```")

					elif arg.lower() in "avorion":
						await ctx.send("Avorion hat diese Funktion noch nicht")

					elif arg.lower() in "factorio":
						try:
							await ctx.send(FactorioServer.status())
						except Server_notRunning as e:
							await ctx.send("FactorioServer läuft nicht")
							await ctx.send("Der Fehler lautet:```" + str(e) + "```")
			else:
				await ctx.send("Bitte gib einen Server zum Sichern an.")
				await ctx.send("```!status Ark|Avorion|Factorio```")
		except NoRights:
			await ctx.send("DU darfst den Server nicht befehlen")

	async def kill(self, ctx):
		await ctx.send("Yes Master.")
		await bot.close()


if __name__ == '__main__':
	avorioniHandler = Avorioni()
	bot.run(settings.bot_id)
