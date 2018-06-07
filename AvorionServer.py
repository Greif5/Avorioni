import settings
import valve.rcon

def runRcon(strCommand):
    """throws
    UnicodeDecodeError
    RCONAuthenticationError
    RCONCommunicationError
    RCONMessageError
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
    strReturn = runRcon("/save")

    return strReturn