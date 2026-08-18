# ./app/exceptions/system.py


class SystemOperationError(Exception):
    """ Raised for errors related to system operations. """
    pass


class ProcessError(Exception):
    """ Raised for errors related to system processes and subprocesses. """
    pass


class ExecutableNotFoundError(ProcessError):
    """ Raised when the executable not found. """
    pass


class ProcessStartupError(ProcessError):
    """ Raised when the process has failed to start. """
    pass


class ProcessNotFoundError(ProcessError):
    """ Raised when the process is not found. """
    pass


class ProcessTerminationError(ProcessError):
    """ Raised when the process has failed to terminate. """
    pass
