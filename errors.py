class OutputFileError(Exception):
    def __init__(self, message="OutputFileError"):
        msg = message
        if message == "OutputFileError":
            msg = f"OutputFileError: {message}"
        super().__init__(msg)