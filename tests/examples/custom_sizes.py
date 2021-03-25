# ```python
# for convenience you can import all the baked in ints with the sized_ints module
from sized_ints import *

# print(dir())

# if you need additional, specific sizes you can import them from `sized`
from sized import u20, u1132, i27

# however if you do not know what sizes you'll need ahead of time, that's fine.
#   you can choose int sizes at 'runtime' using the `Signed` and `Unsigned` types
from sized_ints import *
from typing import *


def new_user_sized_int() -> Type[Unsigned]:
    width = int(input("width of new sized int: "))  # for some reason?
    ux = Unsigned[width]  # get the  new Unsigned size type
    return ux


# ```
