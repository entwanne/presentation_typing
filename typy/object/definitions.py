from .base import TypeForm
from .function import Callable
from .type import Type

# Definition of `type` metaclass

base_type = Type(name='type')

# Set it as the type of types
TypeForm.type = base_type


# The type of functions, aka types.FunctionType

function_type = Type(name='function')

Callable.type = function_type
