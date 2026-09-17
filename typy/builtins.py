from .object import Type, Function

int = Type(
    name='int',
    bases=(),
    methods={},
)
float = Type(
    name='float',
    bases=(),
    methods={},
)
str = Type(
    name='str',
    bases=(),
    methods={},
)

int.methods['__init__'] = Function(
    name='__init__',
    args=(int, int | float | str),
    returns=int,
)
int.methods['__add__'] = Function(
    name='__add__',
    args=(int, int),
    returns=int,
)

float.methods['__init__'] = Function(
    name='__init__',
    args=(float, int | float | str),
    returns=float,
)
float.methods['__add__'] = Function(
    name='__add__',
    args=(float, float | int),
    returns=float,
)

str.methods['__init__'] = Function(
    name='__init__',
    args=(str, str | int | float),
    returns=str,
)
str.methods['__add__'] = Function(
    name='__add__',
    args=(str, str),
    returns=str,
)
