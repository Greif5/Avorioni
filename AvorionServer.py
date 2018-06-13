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
	"""
	
    strReturn = runRcon("/stop")

    return strReturn

def start():
    #do some starting stuff

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
