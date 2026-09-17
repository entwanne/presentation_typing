from .base import TypeForm
from .type import Type

# Definition of `type` metaclass

base_type = Type(name='type')

# Set it as the type of types
TypeForm.type = base_type
