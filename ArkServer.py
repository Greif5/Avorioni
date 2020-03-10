import datetime
import re
import tarfile
import os
import json
import subprocess
from exceptionClasses import *


class ArkServer:
	def __init__(self, jsonPath="settings.json"):
		self.path = "/path/to/ArkServer"
		self.pathBackup = "/path/to/ArkBackup"
		self.backupName = "Ark"
		self.launcherName = "arkmanager"

		self.priviligedUser = []
		self.adminList = []

		self.jsonPath = jsonPath
		self.jsonKey = "Ark"

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
		Server_notStarting
		Server_notStopping
		NoRights
		"""

		"""Params
		Restart Server Y/n
		
		"""
		if userId not in self.adminList:
			raise NoRights

		try:
			# Stop the Server
			self.stop(userId=userId)
			# Create time and backupname
			# Time cheatsheet: http://strftime.org/
			dtNow = datetime.datetime.now()
			strNow = dtNow.strftime('%Y-%m-%d_%H-%M-%S')
			strBak = self.pathBackup + self.backupName + "_" + strNow + ".tgz"

			# Run backup
			with tarfile.open(strBak, "w:gz") as tar:
				tar.add(self.pathArk, arcname=os.path.basename(self.pathArk))

			if intParam:
				try:
					self.start(userId=userId)
				except Server_isRunning:
					pass
				except Server_notStarting as e:
					raise Server_notStarting(e)

		except Server_notStopping as e:
			raise Server_notStopping(e)

	def stop(self, userId):
		"""throws
		Server_notStopping
		NoRights
		"""
		if userId not in self.priviligedUser:
			raise NoRights
		try:
			if "the server is already stopped" in str(subprocess.run(self.launcherName + " stop", shell=True, check=True, stdout=subprocess.PIPE).stdout).lower():
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
			if "start aborted due to server already running" in str(
					subprocess.run(self.launcherName + " start", shell=True, check=True, stdout=subprocess.PIPE).stdout).lower():
				raise Server_isRunning("Server läuft schon")
		except Exception as e:
			raise Server_notStarting(e)

	def isStarted(self, userId):
		"""throws
		Server_notRunning
		"""
		try:
			strStatus = self.status(userId=userId)

			if re.match("Server online:( )*Yes", strStatus):
				return True
			else:
				return False
		except Exception as e:
			Server_notRunning(e)

	def isUsed(self, userId):
		"""throws
		Server_notRunning
		"""
		try:
			strStatus = self.status(userId=userId)

			if re.match("Server online:( )*Yes", strStatus):
				return True
			else:
				return False
		except Exception as e:
			Server_notRunning(e)

	def save(self, userId):
		"""throws
		Server_notRunning
		NoRights
		"""
		if userId not in self.priviligedUser:
			raise NoRights
		try:
			if "unable to send cmd to a stopped server!" in str(
					subprocess.run(self.launcherName + " saveworld", shell=True, check=True, stdout=subprocess.PIPE).stdout).lower():
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
			strReturn = subprocess.run(self.launcherName + " status", shell=True, check=True, stdout=subprocess.PIPE).stdout.decode("UTF-8")
			strReturn = strReturn.replace("[0;39m", "")
			strReturn = strReturn.replace("[1;31m", "")
			strReturn = strReturn.replace("[1;32m", "")
			strReturn = strReturn.replace(" Server", "Server")
			strReturn = strReturn.replace(" ARKServers", "ARKServers")
			strReturn = strReturn.replace(" Steam connect", "Steam connect")
			return str("```" + noEscape(strReturn) + "```")
		except Exception as e:
			raise Server_notRunning(e)

	def update(self, userId):
		"""throws
		Server_notStopping
		NoRights
		"""
		if userId not in self.adminList:
			raise NoRights
		raise NotImplemented

	def userAdd(self, userId, newUser):
		if userId in self.adminList:
			self.priviligedUser.append(newUser)
			self.saveJson()
		else:
			raise NoRights

	def userRemove(self, userId, newUser):
		if userId in self.adminList:
			self.priviligedUser.remove(newUser)
			self.saveJson()
		else:
			raise NoRights


# IDK-Funktion to remove weird ASCII-Escape chars
noEscape = lambda s: "".join(i for i in s if not 27 == ord(i))

if __name__ == '__main__':
	foo = ArkServer()
	foo.saveJson()
