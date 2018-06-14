import datetime
import settings
import valve.rcon

def backup():
	"""throws
	"""
		
	"""returns
	true/false
	"""
	
	#Stop the Server
	stop()
	
	#Create time and backupname
	#Time cheatsheet: http://strftime.org/
	dtNow	= datetime.datetime.now()
	strNow	= dtNow.strftime('%Y-%m-%d_%H-%M-%S')
	strBak	= settings.BackupPath + settings.BackupName +"_"+ strNow +".tgz"
	
	#Run backup
	with tarfile.open(strBak, "w:gz") as tar:
		tar.add(settings.ServerPath, arcname=os.path.basename(settings.ServerPath))
	
	
	start()
	return true

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
	string
	false
	"""
	
    strReturn = runRcon("/stop")
    
    #Delete the Lockfile
    try:
		os.remove(settings.LockFile)
	catch OSError:
		return False

    return strReturn

def start():
    #do some starting stuff
    
    #Create a Lockfile
    try:
		os.open(settings.LockFile,'w')
	catch OSError:
		return False 
		
    return False

def save():
    """throws
	UnicodeDecodeError
	RCONAuthenticationError
	RCONCommunicationError
	RCONMessageError
	"""
	
	"""returns
	string
	"""
	
    strReturn = runRcon("/save")

    return strReturn
