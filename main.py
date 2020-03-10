from time import localtime, strftime
from discord.ext import commands
from exceptionClasses import *
import asyncio
import atexit
import json
from ArkServer import ArkServer
from AvorionServer import AvorionServer
from FactorioServer import FactorioServer
import os
import sys


#  global Variables
listAdmins = []
botId = ""
jsonPath ="settings.json"
LockFile = "Avorioni.lock"


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
			if os.path.isfile(LockFile):
				os.remove(LockFile)
			print("Lockfile entfernt")
		except Exception as ex:
			print("Lockfile konnte nicht entfernt werden" + str(ex))
		sys.exit()

	if os.path.isfile(LockFile):
		if not any(strElement in ("-f", "--force") for strElement in sys.argv):
			print("Server läuft bereits.")
			sys.exit()
	else:
		f = open(LockFile, "w+")
		f.close()


# **************************************************************************************
# Python only Funktions
# **************************************************************************************
def exit_Kontroll():
	try:
		os.remove(LockFile)
	except Exception as e:
		print("Lockfile konnte nicht entfernt werden" + str(e))


async def log(strLoggingText):
	if any(strElement in ("-l", "--logging") for strElement in sys.argv):
		strLoggingText = strftime("%Y.%m.%d %H:%M:%S", localtime()) +" - "+ strLoggingText
		print(strLoggingText)
		# todo: what?
		# await settings.bot_debug.send(strLoggingText)


def jsonSave():
	saveDict = {
		"botId": botId,
		"admin": []
	}

	for admin in listAdmins:
		saveDict["admin"].append(admin)

	with open(f"{jsonPath}", "w") as f:
		json.dump(saveDict, f, indent=4)


# load json settings
def jsonLoad(path):
	loadDict = {
		"botId": "",
		"admin": []
	}

	if os.path.exists(path):
		with open(path, "r") as file:
			jsonHandle = json.load(file)

			for key in jsonHandle.keys():
				if key == "botId":
					loadDict["botId"] = jsonHandle[key]
				elif key == "admin":
					for admin in jsonHandle[key]:
						if admin not in loadDict["admin"]:
							loadDict["admin"].append(admin)
	else:
		print(f"Error: '{jsonPath}' does not exist")
		jsonSave()

	return loadDict["botId"], loadDict["admin"]


if __name__ == '__main__':
	parseCallArguments()
	botId, listAdmins = jsonLoad(jsonPath)

	bot = commands.Bot(command_prefix="!", description="Gameserver Bot")
	atexit.register(exit_Kontroll)


# **************************************************************************************
# Bot only Funktions
# **************************************************************************************
def is_admin():
	def invo(ctx):
		return ctx.author.id in listAdmins

	return commands.check(invo)


@bot.event
async def on_ready():
	await avorioniHandler.on_ready()


@bot.command()
async def backup(ctx, *args):
	await avorioniHandler.backup(ctx, *args)


@bot.command()
async def start(ctx, *args):
	await avorioniHandler.start(ctx, *args)


@bot.command()
async def stop(ctx, *args):
	await avorioniHandler.stop(ctx, *args)


@bot.command()
async def save(ctx, *args):
	await avorioniHandler.save(ctx, *args)


@bot.command()
async def status(ctx, *args):
	await avorioniHandler.status(ctx, *args)


@bot.command()
async def update(ctx, *args):
	await avorioniHandler.update(ctx, *args)


@is_admin()
@bot.command()
async def kill(ctx):
	await avorioniHandler.kill(ctx)


@is_admin()
@bot.command()
async def jsonSave(ctx):
	await jsonSave()


@is_admin()
@bot.command()
async def changename(ctx, *, name: str):
	await bot.user.edit(username=name)
	await ctx.send(ctx.author.mention + " - Changed name to: " + name)


class Avorioni:
	def __init__(self):
		self.serverMap = {
			# "Avorion": {"serverHandler": ArkServer(), "longName": "ArkServer"},
			"Ark": {"serverHandler": ArkServer(), "longName": "ArkServer"},
			"Factorio": {"serverHandler": FactorioServer(), "longName": "FactorioServer"}
		}

		# create a string of all allowed arguments
		allowedArguments = ""
		for allowedArg in self.serverMap.keys():
			allowedArguments += allowedArg + "|"

		# remove the last "|" for readability
		self.allowedArguments = allowedArguments[:-1]

	async def on_ready(self):
		print('Logged in as')
		print(bot.user.name)
		print(bot.user.id)
		print('------')
		print("loaded Server:")
		for serverHandle in self.serverMap.values():
			print(f"\t{serverHandle['longName']}")
		print(bot.guilds)

		# settings.bot_debug = bot.get_channel(settings.bot_debug_id)

	async def backup(self, ctx, *args):
		# set a default for the excepts
		serverLongName = "Server"
		try:
			if args:
				# use local variables to make the code more readable
				serverHandler = self.serverMap[args[0].lower()]["serverHandler"]
				serverLongName = self.serverMap[args[0].lower()]['longName']

				# send the backup command
				# todo: not implemented in avorion
				await ctx.send(f"{serverLongName} wird gesichert\nDies kann einige Sekunden dauern.")
				serverHandler.backup(userId=ctx.author.id, intParam=1)
				await ctx.send(f"{serverLongName} wurde gesichert")
			else:
				raise KeyError
		except NotImplemented:
			await ctx.send(f"{serverLongName} unterstützt diesen Befehl noch nicht!")
		except Server_notStopping as e:
			await ctx.send(f"{serverLongName} konnte nicht gestoppt werden")
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only
		except Server_BackupFailed as e:
			await ctx.send(f"{serverLongName} konnte nicht gesichert werden")
			await ctx.send("Bitte schau im Log nach dem Fehler.")
		except KeyError:
			await ctx.send("Bitte gib einen Server zum Sichern an.")
			await ctx.send(f"```!backup {self.allowedArguments}```")
		except Exception as e:
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only

	async def start(self, ctx, *args):
		# set a default for the excepts
		serverLongName = "Server"
		try:
			if args:
				# use local variables to make the code more readable
				serverHandler = self.serverMap[args[0].lower()]["serverHandler"]
				serverLongName = self.serverMap[args[0].lower()]['longName']

				# send the start command
				serverHandler.start(userId=ctx.author.id)
				await ctx.send(f"{serverLongName} wird gestartet")

				# wait 420 seconds for the server to be started
				for i in range(42):
					# print and return successfully
					if serverHandler.isStarted():
						await ctx.send(f"{serverLongName} ist gestartet")
						return
					await asyncio.sleep(10)
				# notify about the timeout
				await ctx.send(f"Der {serverLongName} braucht unerwartet lange zum starten")
			else:
				raise KeyError
		except NotImplemented:
			await ctx.send(f"{serverLongName} unterstützt diesen Befehl noch nicht!")
		except Server_notStarting as e:
			await ctx.send(f"{serverLongName} konnte nicht gestartet werden")
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only
		except Server_isRunning:
			await ctx.send(f"{serverLongName} läuft bereits")
		except NoRights:
			await ctx.send("DU darfst den Server nicht befehlen")
		except KeyError:
			await ctx.send("Bitte gib einen Server zum Starten an.")
			await ctx.send(f"```!start {self.allowedArguments}```")
		except Exception as e:
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only

	async def stop(self, ctx, *args):
		# set a default for the excepts
		serverLongName = "Server"
		try:
			if args:
				# use local variables to make the code more readable
				serverHandler = self.serverMap[args[0].lower()]["serverHandler"]
				serverLongName = self.serverMap[args[0].lower()]['longName']

				# send the stop command
				serverHandler.stop(userId=ctx.author.id)
				await ctx.send(f"{serverLongName} ist gestoppt")
			else:
				raise KeyError
		except NotImplemented:
			await ctx.send(f"{serverLongName} unterstützt diesen Befehl noch nicht!")
		except Server_notStopping as e:
			await ctx.send(f"{serverLongName} konnte nicht gestoppt werden")
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only
		except NoRights:
			await ctx.send("DU darfst den Server nicht befehlen")
		except KeyError:
			await ctx.send("Bitte gib einen Server zum Stoppen an.")
			await ctx.send(f"```!stop {self.allowedArguments}```")
		except Exception as e:
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only

	async def save(self, ctx, *args):
		# set a default for the excepts
		serverLongName = "Server"
		try:
			if args:
				# use local variables to make the code more readable
				serverHandler = self.serverMap[args[0].lower()]["serverHandler"]
				serverLongName = self.serverMap[args[0].lower()]['longName']

				# send the save command
				serverHandler.save(userId=ctx.author.id)
				await ctx.send(f"{serverLongName} wurde gesichert")
			else:
				raise KeyError
		except NotImplemented:
			await ctx.send(f"{serverLongName} unterstützt diesen Befehl noch nicht!")
		except Server_notRunning as e:
			await ctx.send(f"{serverLongName} nicht gesichert werden")
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only
		except RCON_error as e:
			await ctx.send("Es gab einen Fehler!")
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only
		except NoRights:
			await ctx.send("DU darfst den Server nicht befehlen")
		except KeyError:
			await ctx.send("Bitte gib einen Server zum Sichern an.")
			await ctx.send(f"```!save {self.allowedArguments}```")
		except Exception as e:
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only

	async def status(self, ctx, *args):
		# set a default for the excepts
		serverLongName = "Server"
		try:
			if args:
				# use local variables to make the code more readable
				serverHandler = self.serverMap[args[0].lower()]["serverHandler"]
				serverLongName = self.serverMap[args[0].lower()]['longName']

				# send the status command and print it's return
				await ctx.send(f"{serverHandler.status(userId=ctx.author.id)}")
				# todo Avorion hat diese Funktion noch nicht"
			else:
				raise KeyError
		except NotImplemented:
			await ctx.send(f"{serverLongName} unterstützt diesen Befehl noch nicht!")
		except Server_notRunning as e:
			await ctx.send(f"{serverLongName} läuft nicht")
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")
		except NoRights:
			await ctx.send("DU darfst den Server nicht befehlen")
		except KeyError:
			await ctx.send("Bitte gib einen Server zum Sichern an.")
			await ctx.send(f"```!status {self.allowedArguments}```")
		except Exception as e:
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only

	async def update(self, ctx, *args):
		# set a default for the excepts
		serverLongName = "Server"
		try:
			if args:
				# use local variables to make the code more readable
				serverHandler = self.serverMap[args[0].lower()]["serverHandler"]
				serverLongName = self.serverMap[args[0].lower()]['longName']

				# send the status command and print it's return
				await ctx.send(f"{serverHandler.update(userId=ctx.author.id)}")
			else:
				raise KeyError
		except NotImplemented:
			await ctx.send(f"{serverLongName} unterstützt diesen Befehl noch nicht!")
		except Server_notStopping as e:
			await ctx.send(f"{serverLongName} konnte nicht gestoppt werden")
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")
		except NoRights:
			await ctx.send("DU darfst den Server nicht befehlen")
		except KeyError:
			await ctx.send("Bitte gib einen Server zum Sichern an.")
			await ctx.send(f"```!status {self.allowedArguments}```")
		except Exception as e:
			await ctx.send("Der Fehler lautet:```" + str(e) + "```")  # todo put in logs only

	async def kill(self, ctx):
		await ctx.send("Yes Master.")
		await bot.close()


if __name__ == '__main__':
	avorioniHandler = Avorioni()
	bot.run(botId)
