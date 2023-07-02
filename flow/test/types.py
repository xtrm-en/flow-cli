import enum
from dataclasses import dataclass


@dataclass
class TestTarget:
    decl: str
    name: str


@dataclass
class TestMetadata:
    type: str
    target: TestTarget
    source: str


class ResultType(enum.Enum):
    SUCCESS = enum.auto()
    FAILURE = enum.auto()
    ERROR = enum.auto()


@dataclass
class TestResult:
    success: bool
    results: list[ResultType]
