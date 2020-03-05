import datetime
import re
import tarfile
import os
import json
import subprocess
from exceptionClasses import *


class ArkServer:
	def __init__(self, jsonPath="settings.json"):
		self.pathArk = "/path/to/ArkServer"
		self.pathBackup = "/path/to/ArkBackup"
		self.backupName = "Ark"
		self.launcherName = "arkmanager"

		self.readJson(filePath=jsonPath)

	def readJson(self, filePath):
		with open(filePath, "r") as file:
			jsonHandle = json.load(file)

			for key in jsonHandle.keys():
				if key == "pathArk":
					self.pathArk = jsonHandle[key]
				elif key == "pathBackup":
					self.pathBackup = jsonHandle[key]
				elif key == "backupName":
					self.backupName = jsonHandle[key]
				elif key == "launcherName":
					self.launcherName = jsonHandle[key]

	def backup(self, intParam=1):
		"""throws
		Server_notStarting
		Server_notStopping
		"""

		"""Params
		Restart Server Y/n
		"""

		try:
			# Stop the Server
			self.stop()
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
					self.start()
				except Server_isRunning:
					pass
				except Server_notStarting as e:
					raise Server_notStarting(e)

		except Server_notStopping as e:
			raise Server_notStopping(e)

	def stop(self):
		"""throws
		Server_notStopping
		"""
		try:
			if "the server is already stopped" in str(subprocess.run(self.launcherName + " stop", shell=True, check=True, stdout=subprocess.PIPE).stdout).lower():
				raise Server_notStopping("Kein Server gefunden")
		except Exception as e:
			raise Server_notStopping(e)

	def start(self):
		"""throws
		Server_isRunning
		Server_notStarting
		"""
		try:
			if "start aborted due to server already running" in str(
					subprocess.run(self.launcherName + " start", shell=True, check=True, stdout=subprocess.PIPE).stdout).lower():
				raise Server_isRunning("Server läuft schon")
		except Exception as e:
			raise Server_notStarting(e)

	def isStarted(self):
		"""throws
		Server_notRunning
		"""
		try:
			strStatus = self.status()

			if re.match("Server online:( )*Yes", strStatus):
				return True
			else:
				return False
		except Exception as e:
			Server_notRunning(e)

	def isUsed(self):
		"""throws
		Server_notRunning
		"""
		try:
			strStatus = self.status()

			if re.match("Server online:( )*Yes", strStatus):
				return True
			else:
				return False
		except Exception as e:
			Server_notRunning(e)

	def save(self):
		"""throws
		Server_notRunning
		"""
		try:
			if "unable to send cmd to a stopped server!" in str(
					subprocess.run(self.launcherName + " saveworld", shell=True, check=True, stdout=subprocess.PIPE).stdout).lower():
				raise Server_notRunning("Kein Server gefunden")
		except Exception as e:
			raise Server_notRunning(e)

	def status(self):
		"""throws
		Server_notRunning
		"""
		try:
			strReturn = ""
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


# IDK-Funktion to remove weird ASCII-Escape chars
noEscape = lambda s: "".join(i for i in s if not 27 == ord(i))
