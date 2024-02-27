class InternalServerException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.status_code = 500

    def __str__(self):
        return self.message


class ServiceUnavailableException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.status_code = 503

    def __str__(self):
        return self.message
