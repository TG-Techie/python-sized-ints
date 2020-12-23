# Sized Ints
----

sized ints brings fixed width integers to python! Whether bit packing, bit manipulating, or prepareing code to interface with mmio, sized ints makes swizzling and unswizzling bits a breeze.

## Example
```python
from sized_ints import *

# you can make sized number that have limited values ranges
a = u8(127)
# they can be added to plain ints or other ints of the same size
b = a + u8(5)
b -= 5 # plain ints are best used with +=, *=, etc (see note 1)

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
# for connivence you can import all the baked ints along with all of its helper
from sized_ints import *
print(dir())

# if you need specific other sixes you can import from `sized`
from sized_ints import *
from sized import u20, u1132, i27

# however if you do not know what sizes you'll need ahead of time that's fine,
#   you can choose ints' sizes at 'runtime' using `Signed` and `Unsigned`

width = int(input('width: ')) # for some reason?
ux = Unsigned(width)
number = ux(0)
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
# overflow contexts can also be used inline for single statements
with overflow(True):
    x = u3(1)
    with overflow(False): x += 200
```

#### Notes:
1. functionality detail: size-ed-ness is only preserved when the 'magic' or 'dunder' method is called on a previously sized number
