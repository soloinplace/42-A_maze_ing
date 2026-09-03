"""Application-specific exceptions with user-facing messages."""


class AMazeIngError(Exception):
    """Base class for expected application errors."""


class ConfigurationError(AMazeIngError):
    """Raised when the configuration file cannot be parsed."""


class OutputFileError(AMazeIngError):
    """Raised when a maze output file is invalid or cannot be written."""
