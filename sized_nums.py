from typing import *
import builtins

# TODO: call normal int 'InfinInt'?
# TODO: add two runmodes, one with overflow excetions and one with mod clipping
# TODO: reduce redundant _binops and _binops_symbol dics? (however they are not 1 to 1)
# TODO: consider genreating fewer auto created int widths? 

# this uses a list b/c env auto gen appends classes to export (below)
__all__ = ['Unsigned', 'Signed', 'tri', 'bin', 'OverflowError']

class OverflowError(Exception):
    pass


T = TypeVar('T', bound='Base')

def bin(num:object) -> str:
    """
    A zero padding aware verison of the builin bin function that converts ints
    to string representations of binary numbers.
    """
    global builtins, _SignedInt, _UnsignedInt
    if isinstance(num, _UnsignedInt):
        cls = type(num)
        body = builtins.bin(num).lstrip('0b')
        width = cls._bit_width_
        # u0 returns only '0b'm this is for consistency's sake, no outlier cases
        return '0b' + '0'*(width - len(body)) + body
    elif isinstance(num, _SignedInt):
        cls = type(num)
        body = builtins.bin(num).lstrip('-0b')
        width = cls._bit_width_ - 1
        return ('-0b' if num < 0 else '+0b') + '0'*(width - len(body)) + body
    else:
        return builtins.bin(num)

_binops = {'__add__', '__and__', '__divmod__', '__floor__',
    '__floordiv__', '__lshift__','__mod__', '__mul__', '__or__', '__pow__',
    '__radd__', '__rand__', '__rdivmod__', '__rfloordiv__', '__rlshift__',
    '__rmod__', '__rmul__', '__ror__', '__rpow__', '__rrshift__',
    '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', '__sub__',
    '__truediv__', '__xor__',
        # logical ops:
        '__lt__', '__ne__', '__ge__', '__gt__', '__le__', '__eq__'
}

_binop_symbol = {
    '__add__' : '+', '__and__' : '&', '__floordiv__' : '//', '__lshift__' : '<<',
    '__mod__' : '%', '__mul__' : '*', '__or__' : '|', '__pow__' : '**',
    '__radd__' : '+', '__rand__' : '&', '__rfloordiv__' : '//', '__rlshift__' : '<<',
    '__rmod__' : '%', '__rmul__' : '*', '__ror__' : '|',
    '__rpow__' : '**', '__rrshift__' : '>>', '__rshift__' : '>>', '__rsub__' : '-',
    '__rtruediv__' : '/', '__rxor__' : '^', '__sub__' : '-', '__truediv__' : '/',
    '__xor__' : '^',
        # logical ops:
    '__lt__' : '<', '__ne__' : '!=', '__ge__' : '>=',
    '__gt__' : '>', '__le__' : '<=', '__eq__' : '=='
}

# need to do: __reduce_ex__, __reduce__, __round__,

_uniops = {'__abs__', '__ceil__', '__invert__', '__index__',
    '__neg__',  '__pos__', '__trunc__',
}

class _CheckedInt(int):

    _sized_int_types_ = {}

    _bit_width_ = None
    _max_value_ = None
    _min_value_ = None

    def __new__(cls: Type[T], src=0) -> T:
        global int
        # perform normal casts from str, float etc
        value = int(src)
        cls._err_check(value) # may raise
        return super().__new__(cls, src)

    def __repr__(self):
        return f"{type(self).__name__}({int(self)})"

    @classmethod
    def _err_check(cls: Type[T], src: object) -> T: # may raise
        global _CheckedInt
        if cls is _CheckedInt:
            raise NotImplementedError("do not use a raw _CheckedInt")
        if src < cls._min_value_ or src > cls._max_value_:
            raise OverflowError(
                 f"{cls} ints can only represent values >= "
                +f"{cls._min_value_} and <= {cls._max_value_}, got {src}"
            )


    @classmethod
    def tryfrom(cls: Type[T], src: object): # Result[T, str]
        raise NotImplementedError(
            ".tryfrom(...) not implemented, will return an `envly.Result[...]`"
        )

    # generate operand methods
    for op in _uniops:
        exec(f"""def {op}(self):
                    return type(self)(int(self).{op}())
                    #cls = type(self)
                    #return cls(int(self).{op}())
             """)
    else:
        del op

    for op in _binops:
        exec(f"""def {op}(self, other):
                    cls = type(self)
                    if not isinstance(other, (cls, int)):
                        raise  TypeError(f"cannot {_binop_symbol.get(op, op.strip('_'))} a '{{type(other).__name__}}' to '{{cls.__name__}}', "\
                            f"be sure to cast using `{{cls.__name__}}.tryfrom({{other}})`"
                        )
                    return cls(int(self).{op}(int(other)))
             """)
    else:
        del op

class _SignedInt(_CheckedInt):

    def as_unsinged(src):
        global abs
        cls = type(src)
        src = int(src)
        assert isinstance(cls, Signed)
        signbit = u1(1 if src < 0 else 0)
        body = abs(src)
        if signbit == 1:
            val = body - 1 # -1 -> 0 b/c abs(-1) -1 convs back to
        else:
            val = body
        return Unsigned(cls._bit_width_)(signbit<<(cls._bit_width_-1) + val)

class _UnsignedInt(_CheckedInt):
    def as_signed(src):
        cls = type(src)
        src = int(src)
        assert isinstance(cls, Unsigned)
        signbit = u1(src >> (cls._bit_width_ -1))
        body = src & ~(1<<(cls._bit_width_ -1))

        if signbit == 1: # convert from two's
            val = body + 1 # 0 - > 1 -> 2, 2 -> 3 etc
        else:
            val = body

        return Signed(cls._bit_width_)((0, -1)[signbit] * val)

# metaclasses to genrate any width int widths ate runtime
class Signed(type):

    _signed_int_types_ = {}

    def __new__(cls, width: int) -> type:
        global Signed

        if width < 1:
            raise TypeError(f"uints cannot have negative width")

        tag = (cls, width)
        if tag in Signed._signed_int_types_:
            return Signed._signed_int_types_[tag]
        else:
            self = super().__new__(cls,
                f'i{width}',
                (_SignedInt,),
                {
                    '_bit_width_' : width,
                    '_max_value_' :  int( 2**(width-1) -1),
                    '_min_value_' : -int( 2**(width-1)   ),
                }
            )
            Signed._signed_int_types_[tag] = self
            return self

    def __repr__(self:type) -> str:
        return f"<class '{self.__name__}'>"

class Unsigned(type):

    _unsigned_int_types_ = {}

    def __new__(cls, width: int) -> type:
        global Unsigned

        if width < 0:
            raise TypeError(f"uints cannot have negative width")

        tag = (cls, width)
        if tag in Unsigned._unsigned_int_types_:
            return Unsigned._unsigned_int_types_[tag]
        else:
            self = super().__new__(cls,
                f'u{width}',
                (_UnsignedInt,),
                {
                    '_bit_width_' : width,
                    '_max_value_' : int(2**width - 1),
                    '_min_value_' : int(0),
                }
            )
            Unsigned._unsigned_int_types_[tag] = self
            return self

    def __repr__(self:type) -> str:
        return f"<class '{self.__name__}'>"

    @staticmethod
    def pack(*nums:'Unsigned') -> 'Unsigned':
        """
        A function to take several unsinged integes and combine them into
        one larger number. For example Unsinged.pack(u3(0b101), u4(0011)) returns
        u7(0b1010011).
        """
        global Unsigned
        val = 0
        width = 0
        for index, num in enumerate(nums):
            numcls = type(num)
            assert isinstance(numcls, Unsigned), (
                  "all inputs must be unsinged integers, "
                +f"found item at index {index} was a {numcls}"
            )
            val = (val << numcls._bit_width_) + int(num)
            width += numcls._bit_width_
        return Unsigned(width)(val)

    @staticmethod
    def unpack(source: Union[int, 'Unsigned'], into: tuple) -> Tuple['Unsigned', ...]:
        """
        Takes an integer (int or Unsinged) and breaks it into smaller uints.
        For example Unsinged.unpack(u7(0b1010011), (u3, u2, u2)) would return
        (u3(0b101), u2(0b00), u2(0b11)). Both 'normal' and unsinged ints can
        be unpacked, normal ints are assumed to be infinitely 0 padded on the left.
        Additionally adding a ... to the begining of an unpack template (the
        tuple of types) will "absorb" any extra zeros to the left.
         # (... has additional future functionality planned)
        """

        # todo: allow the ... anywhere in the unpack sequence
        #   so (u2, ..., u5) is allowed and any size

        global Unsigned
        assert len(into) != 0

        intcls = type(source)

        if isinstance(source, _UnsignedInt):
            src_width = intcls._bit_width_
            sum_width = sum(cls._bit_width_ for cls in into if cls is not ...)
            print(f"{src_width == sum_width=}, {src_width=} == {sum_width=}")
            if src_width == sum_width:
                pass
            elif src_width < sum_width:
                unpack_target = tuple(cls.__name__ for cls in into)
                raise TypeError(
                      "cannot unpack mis-mathched unsinged integer widths, "
                    +f"u{src_width} -> {unpack_target} (ie {src_width} -> {sum_width}).\n"
                    +f"either balance the widths or cast the source number to a "
                    +f"plain int: `Unsigned.unpack(<{intcls.__name__}>, {unpack_target})`"
                )
            elif src_width > sum_width and ... not in into:
                unpack_target = tuple(cls.__name__ for cls in into)
                raise TypeError(
                      "cannot unpack mis-mathched unsinged integer widths, "
                    +f"u{src_width} -> {unpack_target} (ie {src_width} -> {sum_width}).\n"
                    +f"either balance the widths or add a `...` to the unpack template: "
                    +f"`Unsigned.unpack(<{intcls.__name__}>, {('...',)+unpack_target})`"
                )

        if into[0] is not ... and ... in into:
            raise NotImplementedError(
                f"`...` not yet supported at index {into.index(...)} (only 0)"
            )

        if not isinstance(source, _UnsignedInt) and ... in into:
            raise ValueError(
                f"... can only be used with unsinged inst, found {intcls}"
            )

        chunks = []
        val = int(source)
        for cls in reversed(into):
            if cls is ...:
                break
            width = cls._bit_width_
            chunks.insert(0, cls(val & (2**width -1)))
            val = val >> width

        return tuple(chunks)

class tri(_CheckedInt):
    _bit_width_ = None
    _max_value_ = 1
    _min_value_ = -1

# make env by auto generating classes and string into the local scope
for width in [*range(1, 128), 128, 256, 512, 1024]:
    ucls = Unsigned(width)
    __all__.append(ucls.__name__)
    locals()[ucls.__name__] = ucls

    icls = Signed(width)
    __all__.append(icls.__name__)
    locals()[icls.__name__] = icls

u0 = Unsigned(0)
__all__.append('u0')
