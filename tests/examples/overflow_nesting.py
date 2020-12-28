from sized_ints import *

# ```python
def some_func():
    # needs no overflow errors (we can rely on the default)
    assert overflow.ison() is False
    assert u8(232) + u8(127) == u8(103)


with overflow(True):
    try: u8(255) + 1
    except: print('overflow caught')

    assert overflow.ison() is True
    some_func()
    assert overflow.ison() is True
# ```
