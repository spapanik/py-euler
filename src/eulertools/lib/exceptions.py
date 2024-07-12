from itertools import chain
from pathlib import Path


class DuplicateProblemError(RuntimeError):
    __slots__ = ()

    def __init__(self, problem_id: str) -> None:
        super().__init__(f"Duplicate problem id: {problem_id}")


class InternalError(RuntimeError):
    __slots__ = ()

    def __init__(self, debug_info: list[str]) -> None:
        super().__init__("eulertools reached an inconsistent state. Reasons:")
        self.__notes__ = [f"    * {info}" for info in debug_info]


class InvalidLanguageError(ValueError):
    __slots__ = ()

    def __init__(self, language: str) -> None:
        super().__init__(f"{language} is not a valid language")


class InvalidProblemError(ValueError):
    __slots__ = ("parsed_languages",)

    def __init__(self, problem: str, parsed_languages: set[str]) -> None:
        self.parsed_languages = sorted(parsed_languages)
        super().__init__(f"{problem} is not a valid problem for {self.language_names}")

    @property
    def language_names(self) -> str:
        if not self.parsed_languages:
            return "any language"
        return ", ".join(self.parsed_languages)


class InvalidVersionError(ValueError):
    __slots__ = ()

    def __init__(self, min_version: str) -> None:
        super().__init__(f"The project requires a eulertools >= v{min_version}")


class MissingProjectRootError(FileNotFoundError):
    __slots__ = ()

    def __init__(self, cwd: Path) -> None:
        super().__init__("Couldn't find a project root directory")
        self.__notes__ = list(
            chain(
                ["Locations searched:"],
                (f"    * {path.joinpath('.euler')}" for path in cwd.parents),
            )
        )


class MissingVersionError(ValueError):
    __slots__ = ()

    def __init__(self, settings: Path) -> None:
        super().__init__(f"Config in `{settings}` has no version info")


class ProblemNotFoundError(ValueError):
    __slots__ = ()

    def __init__(self, name: str) -> None:
        super().__init__(f"Couldn't locate problem named `{name}`")
