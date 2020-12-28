# Sized Ints

Sized Ints brings fixed width integers to python! Whether bit packing, bit manipulating, or preparing code to interface with mmio, Sized Ints makes swizzling and unswizzling bits a breeze.

> __Note:__ This project is under development, there may be:
> - **minor** api changes, while this is not expected it is possible
> - changes in the under lying implementation

## Example
```python
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
```

### What sizes are there?
Any sizes cpython can represent.
```python
# for convenience you can import all the baked in ints with the sized_ints module
from sized_ints import *
print(dir())
# if you need additional, specific sizes you can import them from `sized`
from sized import u20, u1132, i27

# however if you do not know what sizes you'll need ahead of time, that's fine.
#   you can choose int sizes at 'runtime' using the `Signed` and `Unsigned` types
from sized_ints import *
from typing import *

def new_user_sized_int() -> Type[Unsigned]:
    width = int(input('width of new sized int: ')) # for some reason?
    ux = Unsigned[width] # get the  new Unsigned size type
    return ux
```
##### Baked in sizes:
- u0, u1, u4, u8, u16, u32, u64, u128, u256, u512, u1024
- i1, i4, i8, u16, i128, i256, i512, i1024

## Overflow
By default overflow errors are off for all Sized Ints

```python
# by default overflow is silent and numbers will rollover
d = sized.u8(232) + sized.u8(127) # u8(103), no error
```

However, you can manually enable or disable overflow on a scope by scope basis.
```python
with overflow(True):
    try:
        d = sized.u8(232) + sized.u8(127) # will raise
    except OverflowError:
        print("error raised, yay?")
```
These contexts will only affect your current scope so functions you call aren't affected.
```python

def some_func():
    # needs no overflow errors (we can rely on the default)
    assert overflow.ison() is False
    assert u8(232) + u8(127) == u8(103)

with overflow(True):
    try: u8(255) + 1
    except: print('overflow caught')

    print(f"some_func before, {overflow.ison()=}")
    some_func()
    print(f"some_func after, {overflow.ison()=}")
```

### Tips and Tricks:
```python
# unsigned ints can be packed and unpacked by widths
... # documentation needed
```
```python
# overflow contexts can also be used inline for single statements
with overflow(True):
    x = u3(1)
    with overflow(False): x += 200
```

### Issues and Features:
- __Bugs__: If you find a bug/issue, please file an issue on Github with an example and explanation.
- __Features__: If you have a proposed feature please either fork the [python-sized-ints repo](https://github.com/TG-Techie/python-sized-ints) and make a pull request with the code or without code make an issue to discuss the possible feature.

#### __Todos:__ help welcome
- extend the documentation to cover `.twos()`, `.as_signed/as_unsigned()`, `Unsigned.pack()`, `Unsigned.unpack()`, `tri`, `utri`, etc
- write more tests (:sweat_smile:)
- switch from auto generated dunder/magic methods to hand rolled methods in `_SizedInt`
- write a `hex()` function to express the size of the int (like `bin()`)
- and a non sized `uint` type that is always >= 0
