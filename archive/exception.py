"""Exception handling.
"""

class _BaseException(Exception):
    """An exception that tries to suppress misleading context.

    `Exception Chaining and Embedded Tracebacks`_ has been introduced
    with Python 3.  Unfortunately the result is completely misleading
    most of the times.  This class supresses the context in
    :meth:`__init__`.

    .. _Exception Chaining and Embedded Tracebacks: https://www.python.org/dev/peps/pep-3134/

    """
    def __init__(self, *args):
        super().__init__(*args)
        if hasattr(self, '__cause__'):
            self.__cause__ = None

class ArchiveError(_BaseException):
    pass

class ArchiveCreateError(ArchiveError):
    pass

class ArchiveReadError(ArchiveError):
    pass

class ArchiveIntegrityError(ArchiveError):
    pass

