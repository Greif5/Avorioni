import	datetime
import	settings
import	subprocess
import	tarfile
import	time
import valve
import	os.path
import	psutil
from exceptionClasses import *


class Avorion:
	def __init__(self):
		self.cmdHandle = None

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
			strBak = settings.Avorion_BackupPath + settings.Avorion_BackupName + "_" + strNow + ".tgz"

			# Run backup
			with tarfile.open(strBak, "w:gz") as tar:
				tar.add(settings.Avorion_BackupPath, arcname=os.path.basename(settings.Avorion_BackupPath))

			if intParam:
				try:
					self.start()
				except Server_isRunning:
					pass
				except Server_notStarting as e:
					raise Server_notStarting(e)

		except Server_notStopping as e:
			raise Server_notStopping(e)

	def runRcon(self, strCommand):
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

	def stop(self):
		"""throws
		Sever_notStopping
		"""

		if self.cmdHandle:
			try:
				self.save()
			except Server_notRunning():
				return

			try:
				strReturn = settings.Avorion_Handler.communicate("/stop")[0]
				print(strReturn)

				if not strReturn:
					self.cmdHandle.kill()

			except Exception as e:
					raise Server_notStopping(e)

			time.sleep(1)
			if self.getServer():
				raise Server_notStopping()

	def start(self):
		"""throws
		Server_isRunning
		Server_notStarting
		"""
		if not self.cmdHandle:
			try:
				print("Starting Avorion")
				self.cmdHandle = subprocess.Popen(
					settings.Avorion_Launcher,
					stdin=subprocess.PIPE,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					shell=True)
				print("Done")
			except Exception as e:
				raise Server_notStarting(e)
		else:
			raise Server_isRunning()

	def save(self):
		"""throws
		RCON_error
		Sever_notRunning
		"""
		if self.cmdHandle:
			try:
				# strReturn = runRcon("/save")
				print("Sending")
				byteReturn = self.cmdHandle.communicate("/save".encode(),20)[0]
				strReturn = byteReturn.decode('utf-8')
				print(strReturn)
				print("Done")
			except Exception as e:
				raise RCON_error(e)
		else:
			raise Server_notRunning()

	def update(self):
		"""throws
		Server_notStarting
		Server_notStopping
		Server_UpdateFailed
		"""

		try:
			self.backup(0)
		except Server_notStopping as e:
			raise Server_notStopping(e)
		except Server_notStarting as e:
			raise Server_notStarting(e)

		try:
			# Run Steam CMD with Params
			subprocess.run(settings.steamCMD+" +login anonymous +force_install_dir "+settings.Avorion_Path+" +app_update 565060 validate")
		except Exception as e:
			raise Server_UpdateFailed(e)
