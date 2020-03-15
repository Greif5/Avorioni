class Server_BackupFailed(Exception):
	pass


class Server_notStopping(Exception):
	pass


class Server_notStarting(Exception):
	pass


class Server_notRunning(Exception):
	pass


class Server_isRunning(Exception):
	pass


class Server_UpdateFailed(Exception):
	pass


class RCON_error(Exception):
	pass


class NoRights(Exception):
	pass


class UserNotAllowed(Exception):
	pass


class UserAlreadyAllowed(Exception):
	pass
