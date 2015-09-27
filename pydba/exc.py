class PyDBAError(Exception):
    """Base exception for this project."""


class DatabaseError(PyDBAError):
    """Indicates an error occurred with database."""


class CommandNotFoundError(PyDBAError):
    """Indicates a command was not found."""
