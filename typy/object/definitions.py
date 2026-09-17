from .base import TypeForm, Value
from .dynamic import DynamicFunction, ApplicationFunction
from .function import Callable
from .type import Type, UnionType

# Definition of `type` metaclass

base_type = Type(
    name='type',
    bases=(),
    methods={},
)
base_type.methods['__or__'] = DynamicFunction(
    lambda cls: ApplicationFunction(
        name='__or__',
        args=(base_type, base_type) if cls is None else (base_type,),
        returns=base_type,
        apply=lambda cls, rhs: UnionType(types=(cls, rhs)),
    ),
)
base_type.methods['__call__'] = DynamicFunction(
    lambda cls: ApplicationFunction(
        name='__call__',
        args=() if cls is None else cls.methods['__init__'].args[1:] if '__init__' in cls.methods else (),
        returns=cls,
        apply=lambda cls, *args: Value(type=cls),
    ),
)

# Set it as the type of types
TypeForm.type = base_type


# The type of functions, aka types.FunctionType

function_type = Type(
    name='function',
    bases=(),
    methods={
        '__call__': DynamicFunction(
            lambda func: ApplicationFunction(
                name='__call__',
                args=() if func is None else func.args,
                returns=None if func is None else func.returns,
            ),
        ),
    },
)

Callable.type = function_type
