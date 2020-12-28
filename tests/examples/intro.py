# ```python
from sized_ints import *

# you can make sized number that have limited values ranges
a = u8(127)

# they can be used as normal with plain ints or other ints of the same size
b = a + u8(5)
b -= 5

try: # Sized Ints ensures that you manually
    c = b + u16(2) # raises TypeError (b's width < u16)
except:
    c = u16(b) + u16(2)

# but you can always cast back to plain ints
plain = int(b)
# ```
