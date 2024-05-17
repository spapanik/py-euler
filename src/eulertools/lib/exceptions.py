class MissingProjectRootError(FileNotFoundError):
    pass


class FailedRunError(RuntimeError):
    pass


class InvalidLanguageError(ValueError):
    pass


class InvalidProblemError(ValueError):
    pass
