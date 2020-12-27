# Sized Ints
----

sized ints brings fixed width integers to python! Whether bit packing, bit manipulating, or prepareing code to interface with mmio, sized ints makes swizzling and unswizzling bits a breeze.

> __Note:__ This project is under development, there may be:
- minor api changes, while this is not expected it is possible
- changes in the under lying implementation


## Example
```python
from sized_ints import *

# you can make sized number that have limited values ranges
a = u8(127)
# they can be used as normal with plain ints or other ints of the same size
b = a + u8(5)
b -= 5 # plain ints are best used with +=, *=, etc

# but you cannot add ints of different signs and widths
c = b + u16(2) # raises TypeError (b's width < u16)
c = u16(b) + u16(2)

# but you can always cast back to plain ints ('InfinInts')
plain = int(b)

# TODO: add more examples, etc
```

### What sizes are there?
Any sizes cpython can represent.
```python
# for convenience you can import all the baked ints along with all of its helper
from sized_ints import *
print(dir())

# if you need specific other sixes you can import from `sized`
from sized_ints import *
from sized import u20, u1132, i27
```
```python
# however if you do not know what sizes you'll need ahead of time that's fine,
#   you can choose ints' sizes at 'runtime' using `Signed` and `Unsigned`
from sized_ints import Unsigned, SomeWidth

def new_user_sized_int() -> Unsigned[SomeWidth]:
    width = int(input('width of new sized int: ')) # for some reason?
    ux = Unsigned[width] # get the  new Unsigned size type
    return ux
```
##### Baked in sizes:
- u0-u16, u32, u32, u64, u128, u256, u512, u1024
- i1-i16, i32, i32, i64, i128, i256, i512, i1024

## Overflow
By default overflow is off for all sized ints

```python
# by default overflow is silent
d = sized.u8(232) + sized.u8(127) # u8(103), no error
```

However, you can manually enable or disable overflow on a scope by scope basis.
```python
with overflow(True):
    try:
        d = sized.u8(232) + sized.u8(127)
    except OverflowError:
        print("error raised, yay?")
```
These contexts will only affect your current scope (so functions you call aren't affected) and they can be nested.
```python

def somefunc():
    # needs no overflow errors (we can rely on the default)
    print(f"in somefunc, {overflow.ison()=}")
    assert u8(103) == u8(232) + u8(127)

with overflow(True):
    try: u8(255) + 1
    except: print('overflow caught')

    print(f"outside of somefunc, {overflow.ison()=}")
    somefunc()
    print(f"outside of somefunc, {overflow.ison()=}")
```

### Tips and Tricks:
```python
# unsigned ints can be packed and unpacked by widths
```
```python
# overflow contexts can also be used inline for single statements
with overflow(True):
    x = u3(1)
    with overflow(False): x += 200
```
