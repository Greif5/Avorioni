import datetime
import settings
import valve.rcon
import os.path

def backup(intParam = 1):
	"""throws
	"""
	
	"""Params
	Restart Server Y/n
	"""
		
	"""returns
	0	-	All ok
	1	-	Backupcreated and Server stoped
	-2	-	Server could not be stopped
	-3	-	Server could not be started
	"""
	
	#Stop the Server
	if !stop():
		#Create time and backupname
		#Time cheatsheet: http://strftime.org/
		dtNow	= datetime.datetime.now()
		strNow	= dtNow.strftime('%Y-%m-%d_%H-%M-%S')
		strBak	= settings.BackupPath + settings.BackupName +"_"+ strNow +".tgz"
		
		#Run backup
		with tarfile.open(strBak, "w:gz") as tar:
			tar.add(settings.ServerPath, arcname=os.path.basename(settings.ServerPath))
		
		if intParam:
			if start():
				return 0
			else
				return -3
		else
			return 1
	else
		return -2

def runRcon(strCommand):
    """throws
    UnicodeDecodeError
    RCONAuthenticationError
    RCONCommunicationError
    RCONMessageError
    """
    
    """returns
	string
	"""
    strReturn = valve.rcon.execute(settings.address+":"+settings.port, settings.pw, strCommand)

    return strReturn

def stop():
    """throws
    UnicodeDecodeError
    RCONAuthenticationError
    RCONCommunicationError
    RCONMessageError
    """
    
    """returns
	0	-	all OK
	-1	-	Lockfile could not be removed
	"""
	
	if os.path.isfile(settings.LockFile):
		strReturn = runRcon("/stop")
    
		#Delete the Lockfile
		try:
			os.remove(settings.LockFile)
		catch OSError:
			return -1
		return 0
	else
		return 0

def start():
	"""returns
	0	-	All OK
	-1	-	Server already running / Lockfile exists
	-2	-	Lockfile could not be created
	"""
    #do some starting stuff
    
    if os.path.isfile(settings.LockFile):
		return -1
	
    #Create a Lockfile
    try:
		os.open(settings.LockFile,'w')
	catch OSError:
		return -2 
		
    return 0

def save():
    """throws
	UnicodeDecodeError
	RCONAuthenticationError
	RCONCommunicationError
	RCONMessageError
	"""
	
	"""returns
	0	-	All Ok
	-1	-	Server not running
	"""
	
	if !os.path.isfile(settings.LockFile):
		return -1
    
    strReturn = runRcon("/save")

    return 0

def update():
	"""returns
	0	-	All Ok
	-1	-	Lockfile could not be removed / Server could not be stopped
	"""
	
	intErrorCode = backup(0)
	if intErrorCode == -1:
		return -1
		
	#Run Steam CMD with Params
	
	return 0:
