class OstfException(Exception):

    code = 400

    def __init__(self, message='', argv=()):
        self.message = message
        self.argv = argv


class OstfDBException(OstfException):
    pass

class OstfCommandsException(OstfException):
    pass

class OstfNoseException(OstfException):
    pass
