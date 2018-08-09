import	datetime
import	settings
import	subprocess
import	tarfile
import	time
import	valve.rcon
import	os.path
import	psutil
from exceptionClasses import *


def backup(intParam = 1):
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
		strBak = settings.BackupPath + settings.BackupName + "_" + strNow + ".tgz"

		# Run backup
		with tarfile.open(strBak, "w:gz") as tar:
			tar.add(settings.ServerPath, arcname=os.path.basename(settings.ServerPath))

		if intParam:
			try:
				start()
			except Server_isRunning:
				pass
			except Server_notStarting as e:
				raise Server_notStarting(e)

	except Server_notStopping as e:
		raise Server_notStopping(e)


def runRcon(strCommand):
	"""throws
	RCON_error
	"""

	"""returns
	string
	"""
	try:
		strReturn = valve.rcon.execute(settings.address+":"+settings.port, settings.pw, strCommand)
	except Exception as e:
		raise RCON_error(e)

	return strReturn


def stop():
	"""throws
	Sever_notStopping
	"""

	proc = getServer()
	if proc:
		try:
			save()
		except Server_notRunning():
			return
		try:
			strReturn = runRcon("/stop")
		except RCON_error:
			strReturn = "SOME ERROR"

		if not strReturn:
			try:
				proc.kill()
			except Exception as e:
				raise Server_notStopping(e)

		time.sleep(1)
		if psutil.pid_exists(proc.pid):
			if psutil.Process(pid=proc.pid).name == proc.name():
				raise Server_notStopping()


def start():
	"""throws
	Server_isRunning
	Server_notStarting
	"""
	proc = getServer()
	if not proc:
		try:
			"""start server"""
		except Exception as e:
			raise Server_notStarting(e)
	else:
		raise Server_isRunning()


def save():
	"""throws
	RCON_error

	Sever_notRunning
	"""
	
	proc = getServer()
	if proc:
		try:
			strReturn = runRcon("/save")
		except Exception as e:
			raise RCON_error(e)

		return

	raise Server_notRunning()


def update():
	"""throws
	Server_notStarting
	Server_notStopping
	Server_UpdateFailed
	"""

	try:
		backup(0)
	except Server_notStopping as e:
		raise Server_notStopping(e)
	except Server_notStarting as e:
		raise Server_notStarting(e)

	try:
		# Run Steam CMD with Params
		subprocess.run(settings.steamCMD+" +login anonymous +force_install_dir "+settings.ServerPath+" +app_update 565060 validate")
	except Exception as e:
		raise Server_UpdateFailed(e)


def getServer():
	for proc in psutil.process_iter():
		if proc.name() == "AvorionServer":
			return proc
