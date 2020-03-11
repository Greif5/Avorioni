import datetime
import json
import os
import subprocess
import tarfile
import valve
from exceptionClasses import *


class AvorionServer:
	def __init__(self, jsonPath="settings.json"):
		self.path = "/path/to/AvorionServer"
		self.pathBackup = "/path/to/AvorionBackup"
		self.backupName = "Avorion"
		self.launcherName = ""
		self.cmdHandle = None
		self.steamCMD = "/path/to/steamCMD"

		self.priviligedUser = []
		self.adminList = []
		self.rconSettings = {
			"address": "127.0.0.1",
			"port": "PORT",
			"pw": "PASSOWRD"
		}

		self.jsonPath = jsonPath
		self.jsonKey = "Avorion"

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
							elif subKey == "steamCMD":
								self.steamCMD = subHandle[subKey]
							elif subKey == "user":
								for user in subHandle[subKey]:
									if user not in self.priviligedUser:
										self.priviligedUser.append(user)
							elif subKey == "admin":
								for admin in subHandle[subKey]:
									if admin not in self.adminList:
										self.adminList.append(admin)
							elif subKey == "rconSettings":
								try:
									for rconKey in subHandle[subKey]:
										self.rconSettings[rconKey] = subHandle[subKey][rconKey]
								except KeyError:
									print(f"Error: key '{rconKey}' not found")  # todo: put in logs only

	def saveJson(self):
		saveDict = {
			"path": self.path,
			"pathBackup": self.pathBackup,
			"backupName": self.backupName,
			"launcherName": self.launcherName,
			"steamCMD": self.steamCMD,
			"user": [],
			"admin": [],
			"rconSettings": self.rconSettings
		}

		for user in self.priviligedUser:
			saveDict["user"].append(user)

		with open(f"{self.jsonPath}", "w") as f:
			json.dump({self.jsonKey: saveDict}, f, indent=4)

	# todo Implement
	def backup(self, userId, intParam=1):
		"""throws
		Server_notStarting
		Server_notStopping
		NoRights
		NotImplemented
		"""

		"""Params
		Restart Server Y/n
		"""
		if userId not in self.adminList:
			raise NoRights
		raise NotImplemented
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
				tar.add(self.pathBackup, arcname=os.path.basename(self.pathBackup))

			if intParam:
				try:
					self.start(userId=userId)
				except Server_isRunning:
					pass
				except Server_notStarting as e:
					raise Server_notStarting(e)

		except Server_notStopping as e:
			raise Server_notStopping(e)

	# todo Implement
	def runRcon(self, userId, strCommand):
		"""throws
		RCON_error
		NoRights
		NotImplemented
		"""

		"""returns
		string
		"""
		if userId not in self.adminList:
			raise NoRights
		raise NotImplemented

		try:
			strReturn = valve.rcon.execute(
				f"{self.rconSettings['address']}:{self.rconSettings['port']}",
				self.rconSettings["pw"],
				strCommand)
		except Exception as e:
			raise RCON_error(e)

		return strReturn

	# todo Implement
	def stop(self, userId):
		"""throws
		Sever_notStopping
		NoRights
		NotImplemented
		"""
		if userId not in self.adminList:
			raise NoRights
		raise NotImplemented

		if self.cmdHandle:
			try:
				self.save(userId=userId)
			except Server_notRunning():
				return

			try:
				strReturn = self.cmdHandle.communicate("/stop")[0]
				print(strReturn)

				if not strReturn:
					self.cmdHandle.kill()

			except Exception as e:
				raise Server_notStopping(e)

	# todo Implement
	def start(self, userId):
		"""throws
		Server_isRunning
		Server_notStarting
		NoRights
		NotImplemented
		"""
		if userId not in self.adminList:
			raise NoRights
		raise NotImplemented

		if not self.cmdHandle:
			try:
				print("Starting Avorion")
				self.cmdHandle = subprocess.Popen(
					self.launcherName,
					stdin=subprocess.PIPE,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					shell=True)
				print("Done")
			except Exception as e:
				raise Server_notStarting(e)
		else:
			raise Server_isRunning()

	# todo Implement
	def save(self, userId):
		"""throws
		RCON_error
		Sever_notRunning
		NoRights
		NotImplemented
		"""
		if userId not in self.adminList:
			raise NoRights
		raise NotImplemented

		if self.cmdHandle:
			try:
				# strReturn = runRcon("/save")
				print("Sending")
				byteReturn = self.cmdHandle.communicate("/save".encode(), 20)[0]
				strReturn = byteReturn.decode('utf-8')
				print(strReturn)
				print("Done")
			except Exception as e:
				raise RCON_error(e)
		else:
			raise Server_notRunning()

	# todo Implement
	def status(self, userId):
		"""throws
		NoRights
		NotImplemented
		"""
		if userId not in self.adminList:
			raise NoRights
		raise NotImplemented

	# todo Implement
	def update(self, userId):
		"""throws
		Server_notStarting
		Server_notStopping
		Server_UpdateFailed
		NoRights
		NotImplemented
		"""
		if userId not in self.adminList:
			raise NoRights
		raise NotImplemented

		try:
			self.backup(0)
		except Server_notStopping as e:
			raise Server_notStopping(e)
		except Server_notStarting as e:
			raise Server_notStarting(e)

		try:
			# Run Steam CMD with Params
			subprocess.run(
				f"{self.steamCMD} +login anonymous +force_install_dir {self.path} +app_update 565060 validate")
		except Exception as e:
			raise Server_UpdateFailed(e)

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
