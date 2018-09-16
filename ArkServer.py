import	datetime
import	re
import	settings
import	subprocess
from	exceptionClasses import *


def backup(intParam=1):
	"""throws
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
		strBak = settings.Ark_BackupPath + settings.Ark_BackupName + "_" + strNow + ".tgz"

		# Run backup
		with tarfile.open(strBak, "w:gz") as tar:
			tar.add(settings.Ark_Path, arcname=os.path.basename(settings.Ark_Path))

		if intParam:
			try:
				start()
			except Server_isRunning:
				pass
			except Server_notStarting as e:
				raise Server_notStarting(e)

	except Server_notStopping as e:
		raise Server_notStopping(e)


def stop():
	"""throws
	Server_notStopping
	"""
	try:
		if "the server is already stopped" in str(subprocess.run(settings.Ark_Launcher+" stop", shell=True, check=True, stdout=subprocess.PIPE).stdout).lower():
			raise Server_notStopping("Kein Server gefunden")
	except Exception as e:
		raise Server_notStopping(e)


def start():
	"""throws
	Server_isRunning
	Server_notStarting
	"""
	try:
		if "start aborted due to server already running" in str(subprocess.run(settings.Ark_Launcher+" start", shell=True, check=True, stdout=subprocess.PIPE).stdout).lower():
			raise Server_isRunning("Server läuft schon")
	except Exception as e:
		raise Server_notStarting(e)


def isStarted():
	"""throws
	Server_notRunning
	"""
	try:
		strStatus = status()

		if re.match("Server online:( )*Yes", strStatus):
			return True
		else:
			return False
	except Exception as e:
		Server_notRunning(e)


def isUsed():
	"""throws
	Server_notRunning
	"""
	try:
		strStatus = status()

		if re.match("Server online:( )*Yes", strStatus):
			return True
		else:
			return False
	except Exception as e:
		Server_notRunning(e)


def save():
	"""throws
	Server_notRunning
	"""
	try:
		if "unable to send cmd to a stopped server!" in str(subprocess.run(settings.Ark_Launcher+" saveworld", shell=True, check=True, stdout=subprocess.PIPE).stdout).lower():
			raise Server_notRunning("Kein Server gefunden")
	except Exception as e:
		raise Server_notRunning(e)


def status():
	"""throws
	Server_notRunning
	"""
	try:
		strReturn = subprocess.run(settings.Ark_Launcher+" status", shell=True, check=True, stdout=subprocess.PIPE).stdout.decode("UTF-8")
		strReturn = strReturn.replace("[0;39m", "")
		strReturn = strReturn.replace("[1;31m", "")
		strReturn = strReturn.replace("[1;32m", "")
		strReturn = strReturn.replace(" Server",	"Server")
		strReturn = strReturn.replace(" ARKServers",	"ARKServers")
		strReturn = strReturn.replace(" Steam connect",	"Steam connect")
		return str("```"+ noEscape(strReturn) +"```")
	except Exception as e:
		raise Server_notRunning(e)


# IDK-Funktion to remove weird ASCII-Escape chars
noEscape = lambda s: "".join(i for i in s if not 27 == ord(i))
