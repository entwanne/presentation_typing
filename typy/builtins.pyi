# we should have a first pass on the file to reference existing classes
# or have a dependency graph to evaluate a statement only when all needed annotations are loaded
# (and raise an error if dependencies are never resolved)
class int:
    pass

class float:
    pass

class str:
    pass

class int:
    def __init__(self, value: int | str):
        ...
    def __add__(self, rhs: int) -> int:
        ...

class float:
    def __init__(self, value: float | int | str):
        ...
    def __add__(self, rhs: float) -> float:
        ...

class str:
    def __init__(self, value: str | int):
        ...
    def __add__(self, rhs: str) -> str:
        ...
