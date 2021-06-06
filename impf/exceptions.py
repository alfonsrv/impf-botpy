class AdvancedSessionError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message

    def __repr__(self):
        return f'AdvancedSessionError({self.code!r}, {self.message!r})'

    def __str__(self):
        return f'[{self.code}] {self.message}'


class AdvancedSessionCache(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message

    def __repr__(self):
        return f'AdvancedSessionCache({self.code!r}, {self.message!r})'

    def __str__(self):
        return f'Cookies likely expired – [{self.code}] {self.message}'


class AlertError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message

    def __repr__(self):
        return f'AlertError({self.code!r}, {self.message!r})'

    def __str__(self):
        return f'[{self.code}] {self.message}'


class WorkflowException(Exception):
    pass
