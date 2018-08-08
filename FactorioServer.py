import datetime
import settings
import subprocess
from exceptionClasses import *


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
        strBak = settings.Factorio_BackupPath + settings.Factorio_BackupName + "_" + strNow + ".tgz"

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


def stop():
    """throws
    Sever_notStopping
    """
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
    """
    try:
        subprocess.run(settings.Factorio_Launcher+" stop",shell=True, check=True)
    except Exception as e:
        raise Sever_notStopping(e)


def start():
    """throws
    Server_isRunning
    Server_notStarting
    """
    try:
        subprocess.run(settings.Factorio_Launcher+" start",shell=True, check=True)
    except Exception as e:
        raise Server_notStarting(e)


def save():
    """throws
    RCON_error

    Sever_notRunning
    """
    """
    proc = getServer()
    if proc:
        try:
            strReturn = runRcon("/save")
        except Exception e:
            raise RCON_error(e)

        return

    raise Server_notRunning()
    """
    try:
        subprocess.run(settings.Factorio_Launcher+" save",shell=True, check=True)
    except Exception as e:
        raise Sever_notRunning(e)


def getServer():
    for proc in psutil.process_iter():
        if proc.name() == "factorio":
            return proc
