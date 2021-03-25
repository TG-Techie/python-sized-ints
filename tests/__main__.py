from sized_ints import *

from . import overflow_nesting

print("overflow_nesting passed")

from . import overflow_scoping

print("overflow_scoping passed")

from . import twos_complement

print("twos_complement passed")

print("testing examples")
from .examples import overflow_nesting
from .examples import intro
from .examples import custom_sizes

print("examples passed")
