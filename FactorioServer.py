import datetime
import os
import settings
import subprocess
import tarfile
from exceptionClasses import *


def backup(intParam=1):
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
		stop()
		# Create time and backupname
		# Time cheatsheet: http://strftime.org/
		dtNow = datetime.datetime.now()
		strNow = dtNow.strftime('%Y-%m-%d_%H-%M-%S')
		strBak = settings.Factorio_BackupPath + settings.Factorio_BackupName + "_" + strNow + ".tgz"

		# Create backupfolder
		if not os.path.isdir(settings.Factorio_BackupPath):
			os.makedirs(settings.Factorio_BackupPath)

		# Run backup
		with tarfile.open(strBak, "w:gz") as tar:
			tar.add(settings.Factorio_Path, arcname=os.path.basename(settings.Factorio_Path))

		if intParam:
			try:
				start()
			except Server_isRunning:
				pass
			except Server_notStarting as e:
				raise Server_notStarting(e)

	except Server_notStopping as e:
		raise Server_notStopping(e)
	except Exception as e:
		print(e)
		raise Server_BackupFailed(e)


def stop():
	"""throws
	Server_notStopping
	"""
	try:
		if "Factorio is not running." in str(subprocess.Popen(settings.Factorio_Launcher+" stop", shell=True, stdout=subprocess.PIPE).stdout).lower():
			raise Server_notStopping("Kein Server gefunden")
	except Exception as e:
		raise Server_notStopping(e)


def start():
	"""throws
	Server_isRunning
	Server_notStarting
	"""
	try:
		if "server already running." in str(subprocess.run(settings.Factorio_Launcher+" start",shell=True, check=True,stdout=subprocess.PIPE).stdout).lower():
			raise Server_isRunning("Server läuft schon")
	except Exception as e:
		raise Server_notStarting(e)


def save():
	"""throws
	Server_notRunning
	"""
	try:
		if "unable to send cmd to a stopped server!" in str(subprocess.run(settings.Factorio_Launcher+" cmd /server-save",shell=True, check=True,stdout=subprocess.PIPE).stdout).lower():
			raise Server_notRunning("Kein Server gefunden")
	except Exception as e:
		raise Server_notRunning(e)

def status():
		"""throws
		Server_notRunning
		"""
		try:
			strReturn = subprocess.run(settings.Factorio_Launcher + " status", shell=True, stdout=subprocess.PIPE).stdout.decode("UTF-8")
			return str("```" + strReturn + "```")
		except Exception as e:
			raise Server_notRunning(e)

def getServer():
	for proc in psutil.process_iter():
		if proc.name() == "factorio":
			return proc
