from sized_ints import *

# ```python
def some_func():
    # needs no overflow errors (we can rely on the default)
    assert overflow.ison() is False
    assert u8(232) + u8(127) == u8(103)

with overflow(True):
    try:
        x = u8(255) + 3
    except:
        print('\toverflow caught')

    assert overflow.ison() is True
    some_func()
    assert overflow.ison() is True
# ```
