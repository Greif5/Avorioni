import datetime
import os
import json
import subprocess
import tarfile
import time
from exceptionClasses import *


class FactorioServer:
	def __init__(self, jsonPath="settings.json"):
		self.path = "/path/to/FactorioServer"
		self.pathBackup = "/path/to/FactorioBackup"
		self.backupName = "Factorio"
		self.launcherName = "/path/to/Factorio-init-script"

		self.priviligedUser = []
		self.adminList = []

		self.jsonPath = jsonPath
		self.jsonKey = "Factorio"

		self.readJson()

	def readJson(self):
		if os.path.exists(self.jsonPath):
			with open(self.jsonPath, "r") as file:
				jsonHandle = json.load(file)

				for key in jsonHandle.keys():
					if key == self.jsonKey:
						subHandle = jsonHandle[key]
						for subKey in subHandle:
							if subKey == "path":
								self.path = subHandle[subKey]
							elif subKey == "pathBackup":
								self.pathBackup = subHandle[subKey]
							elif subKey == "backupName":
								self.backupName = subHandle[subKey]
							elif subKey == "launcherName":
								self.launcherName = subHandle[subKey]
							elif subKey == "user":
								for user in subHandle[subKey]:
									if user not in self.priviligedUser:
										self.priviligedUser.append(user)
							elif subKey == "admin":
								for admin in subHandle[subKey]:
									if admin not in self.adminList:
										self.adminList.append(admin)

	def saveJson(self):
		saveDict = {
			"path": self.path,
			"pathBackup": self.pathBackup,
			"backupName": self.backupName,
			"launcherName": self.launcherName,
			"user": [],
			"admin": []
		}

		for user in self.priviligedUser:
			saveDict["user"].append(user)

		with open(f"{self.jsonPath}", "w") as f:
			json.dump({self.jsonKey: saveDict}, f, indent=4)

	def backup(self, userId, intParam=1):
		"""throws
		Server_BackupFailed
		Server_notStarting
		Server_notStopping
		"""

		"""Params
		Restart Server Y/n
		"""

		try:
			# Stop the Server
			self.stop(userId=userId)
			# Create time and backupname
			# Time cheatsheet: http://strftime.org/
			dtNow = datetime.datetime.now()
			strNow = dtNow.strftime('%Y-%m-%d_%H-%M-%S')
			strBak = self.pathBackup + "/" + self.backupName + "_" + strNow + ".tgz"

			# Create backupfolder
			os.makedirs(self.pathBackup, exist_ok=True)

			# Short waiting periode for the Server to fully stop
			# The timeout of 20*5s = 100s should give it enough time to fully stop
			iTimeOut = 0
			while "Factorio is running." in self.status(userId=userId):
				if iTimeOut > 20:
					raise Server_BackupFailed("Serverstopp Timeout")
				time.sleep(5)
				iTimeOut += 1

			# Run backup
			with tarfile.open(strBak, "w:gz") as tar:
				tar.add(self.path, arcname=os.path.basename(self.path))

			if intParam:
				try:
					self.start(userId=userId)
				except Server_isRunning:
					pass
				except Server_notStarting as e:
					raise Server_notStarting(e)

		except Server_notStopping as e:
			raise Server_notStopping(e)
		except Exception as e:
			print(e)
			raise Server_BackupFailed(e)

	def stop(self, userId):
		"""throws
		Server_notStopping
		NoRights
		"""
		if userId not in self.priviligedUser:
			raise NoRights
		try:
			if "Factorio is not running." in str(
					subprocess.Popen(
						self.launcherName + " stop",
						shell=True,
						stdout=subprocess.PIPE).stdout).lower():
				raise Server_notStopping("Kein Server gefunden")
		except Exception as e:
			raise Server_notStopping(e)

	def start(self, userId):
		"""throws
		Server_isRunning
		Server_notStarting
		NoRights
		"""
		if userId not in self.priviligedUser:
			raise NoRights
		try:
			if "server already running." in str(
					subprocess.run(
						self.launcherName + " start",
						shell=True,
						check=True,
						stdout=subprocess.PIPE).stdout).lower():
				raise Server_isRunning("Server läuft schon")
		except Exception as e:
			raise Server_notStarting(e)

	def save(self, userId):
		"""throws
		Server_notRunning
		NoRights
		"""
		if userId not in self.priviligedUser:
			raise NoRights
		try:
			if "unable to send cmd to a stopped server!" in str(
					subprocess.run(
						self.launcherName + " cmd /server-save",
						shell=True,
						check=True,
						stdout=subprocess.PIPE).stdout).lower():
				raise Server_notRunning("Kein Server gefunden")
		except Exception as e:
			raise Server_notRunning(e)

	def status(self, userId):
		"""throws
		Server_notRunning
		NoRights
		"""
		if userId not in self.priviligedUser:
			raise NoRights
		try:
			strReturn_Status = subprocess.run(
				self.launcherName + " status",
				shell=True,
				stdout=subprocess.PIPE).stdout.decode("UTF-8")
			if "Factorio is not running." in str(strReturn_Status):
				return str("```" + strReturn_Status + "```")

			strReturn_Players = subprocess.run(
				self.launcherName + " players",
				shell=True,
				stdout=subprocess.PIPE).stdout.decode("UTF-8")
			strReturn_PlayersOn = subprocess.run(
				self.launcherName + " players-online",
				shell=True,
				stdout=subprocess.PIPE).stdout.decode("UTF-8")

			if strReturn_PlayersOn == "":
				strReturn_PlayersOn = "0"
			return str(
				"```" + strReturn_Status.rstrip() +
				"\nPlayers online: " + strReturn_PlayersOn.rstrip() +
				"\n" + strReturn_Players.rstrip() + "```")
		except Exception as e:
			raise Server_notRunning(e)
