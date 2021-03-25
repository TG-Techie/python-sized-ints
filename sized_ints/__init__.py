from typing import *
import typing
import sys
import builtins
import functools

# TODO: write value tests!
# TODO: call normal int 'InfinInt'?
# TODO: hand rool ^ and ~ for proper bit manipulation
# TODO: hand roll all of the operations
# TODO: consider memoizing seach uXX type based on the value for single existence numbers
# TODO: add check to make sure a _bit_width_ can de represented by the system, ie log2(sys.maxsize) = max _bit_width_
# TODO: add uint for whole numbers

__version__ = "0.1.5"

__all__ = [  # uses a list so the auto genreated uX can be exported
    "Unsigned",
    "Signed",
    "sized",
    "overflow",
    "OverflowError",
    "tri",
    "utri",
    "bin",
    "bitwidth",
]


class OverflowError(Exception):
    pass


singleton = lambda cls: cls()

T = TypeVar("T", bound="Base")


def bin(num: object) -> str:
    """
    A zero padding aware verison of the builin bin function that converts ints
    to string representations of binary numbers.
    """
    global builtins, _SignedInt, _UnsignedInt
    if isinstance(num, _UnsignedInt):
        cls = type(num)
        body = builtins.bin(num).lstrip("0b")
        width = cls._bit_width_
        # u0 returns only '0b'm this is for consistency's sake, no outlier cases
        return f"{cls.__name__}(0b{'0'*(width - len(body)) + body})"
    elif isinstance(num, _SignedInt):
        cls = type(num)
        body = builtins.bin(num).lstrip("-0b")
        width = cls._bit_width_ - 1
        return f"{cls.__name__}({'-0b' if num < 0 else '0b'}{'0'*(width - len(body)) + body})"
    else:
        return builtins.bin(num)


def bitwidth(val: object) -> int:
    assert isinstance(val, (_SizedInt, Signed, Unsigned))
    return val._bit_width_


_binops = {
    # arith ops
    "__add__",
    "__and__",
    "__divmod__",
    "__floor__",
    "__floordiv__",
    "__lshift__",
    "__mod__",
    "__mul__",
    "__or__",
    "__pow__",
    "__radd__",
    "__rand__",
    "__rdivmod__",
    "__rfloordiv__",
    "__rlshift__",
    "__rmod__",
    "__rmul__",
    "__ror__",
    "__rpow__",
    "__rrshift__",
    "__rshift__",
    "__rsub__",
    "__rtruediv__",
    "__rxor__",
    "__sub__",
    "__truediv__",
    "__xor__",
    # logical ops:
    "__lt__",
    "__ne__",
    "__ge__",
    "__gt__",
    "__le__",
    "__eq__",
}

_binop_symbol = {
    # arith ops
    "__add__": "+",
    "__and__": "&",
    "__floordiv__": "//",
    "__lshift__": "<<",
    "__mod__": "%",
    "__mul__": "*",
    "__or__": "|",
    "__pow__": "**",
    "__radd__": "+",
    "__rand__": "&",
    "__rfloordiv__": "//",
    "__rlshift__": "<<",
    "__rmod__": "%",
    "__rmul__": "*",
    "__ror__": "|",
    "__rpow__": "**",
    "__rrshift__": ">>",
    "__rshift__": ">>",
    "__rsub__": "-",
    "__rtruediv__": "/",
    "__rxor__": "^",
    "__sub__": "-",
    "__truediv__": "/",
    "__xor__": "^",
    # logical ops:
    "__lt__": "<",
    "__ne__": "!=",
    "__ge__": ">=",
    "__gt__": ">",
    "__le__": "<=",
    "__eq__": "==",
}

# need to do: __reduce_ex__, __reduce__, __round__,

_uniops = {
    "__abs__",
    "__ceil__",
    "__invert__",
    "__index__",
    "__neg__",
    "__pos__",
    "__trunc__",
}


class _SizedInt(int):

    _sized_int_types_ = {}

    _bit_width_ = None

    _max_value_ = None
    _min_value_ = None

    _clip_mod_ = None
    _clip_offset_ = None

    def __new__(cls: Type[T], value=0, _check_overflow=False) -> T:
        global int, overflow

        if __debug__:  # make sure that _nest_level of ison is correct
            locals()[overflow._local_flag_name] = None
            # setting this to none means that there be an error if
            # .ison() reaches out too few levels
        # perform normal casts from str, float etc

        check_overflow = overflow.ison(_nest_level=1) or _check_overflow
        # print(f"{value=}, {cls=}, {check_overflow=}")
        if check_overflow and _check_overflow:
            cls._raise_on_overflow(value)
        else:
            value = cls._clip_overflow(value)
        return super().__new__(cls, value)

    def __repr__(self):
        cls = type(self)
        return f"{cls.__name__}({int(self)})"
        # return f"{'sized.'*cls._sized_auto_gened_}{cls.__name__}({int(self)})"

    def __init__(self, *_, **__):
        super().__init__()

    @classmethod
    def _raise_on_overflow(cls: Type[T], src: object) -> T:  # may raise
        global _SizedInt
        if cls is _SizedInt:
            raise NotImplementedError("do not use a raw _SizedInt")
        # print(f"{src=}, {src < cls._min_value_ or src > cls._max_value_=}, {src < cls._min_value_=}, {src > cls._max_value_=}")
        if src < cls._min_value_ or src > cls._max_value_:
            raise OverflowError(
                f"{cls} ints can only represent values >= "
                + f"{cls._min_value_} and <= {cls._max_value_}, got {src}"
            )

    @classmethod
    def _clip_overflow(cls: Type[T], src: int) -> int:
        return (src + cls._clip_offset_) % cls._clip_mod_ - cls._clip_offset_

    @classmethod
    def _determine_type_with(cls, other):
        othercls = type(other)
        if othercls is int:
            return cls
        elif cls._is_signed_ != othercls._is_signed_:
            raise TypeError(
                f"cannot perform calculations wtih a '{cls.__name__}' and "
                f"a '{othercls.__name__}',  cast to '{cls.__name__}' "
                f"by `{cls.__name__}({other})`"
            )
        return cls if cls._bit_width_ > othercls._bit_width_ else othercls

    # uni ops:
    __abs__ = __pos__ = lambda self: type(self)(
        int(self).__abs__(),
        _check_overflow=overflow.ison(_nest_level=1),
    )

    __ceil__ = lambda self: type(self)(
        int(self).__ceil__(),
        _check_overflow=overflow.ison(_nest_level=1),
    )

    __floor__ = lambda self: type(self)(
        int(self).__floor__(),
        _check_overflow=overflow.ison(_nest_level=1),
    )

    __invert__ = lambda self: type(self)(
        int(self) ^ (2 ** self._bit_width_ - 1),
        _check_overflow=overflow.ison(_nest_level=1),
    )

    __index__ = lambda self: int(self)

    __neg__ = lambda self: type(self)(
        -int(self),
        _check_overflow=overflow.ison(_nest_level=1),
    )

    __trunc__ = lambda self: type(self)(
        int(self).__trunc__(),
        _check_overflow=overflow.ison(_nest_level=1),
    )

    # logical ops:
    __eq__ = lambda self, other: int(self) == int(other)
    __ne__ = lambda self, other: int(self) != int(other)
    __ge__ = lambda self, other: int(self) >= int(other)
    __le__ = lambda self, other: int(self) <= int(other)
    __gt__ = lambda self, other: int(self) > int(other)
    __lt__ = lambda self, other: int(self) < int(other)

    # binary ops:
    def __add__(self, other):
        return self._determine_type_with(other)(
            int(self) + int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __radd__(self, other):
        return self._determine_type_with(other)(
            int(other) + int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __sub__(self, other):
        return self._determine_type_with(other)(
            int(self) - int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __rsub__(self, other):
        return self._determine_type_with(other)(
            int(other) - int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __mul__(self, other):
        return self._determine_type_with(other)(
            int(self) * int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __rmul__(self, other):
        return self._determine_type_with(other)(
            int(other) * int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __pow__(self, other):
        return self._determine_type_with(other)(
            int(self) ** int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __rpow__(self, other):
        return self._determine_type_with(other)(
            int(other) ** int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __mod__(self, other):
        return self._determine_type_with(other)(
            int(self) % int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __mod__(self, other):
        return self._determine_type_with(other)(
            int(other) % int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __floordiv__(self, other):
        return self._determine_type_with(other)(
            int(self) // int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __rfloordiv__(self, other):
        return self._determine_type_with(other)(
            int(other) // int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __lshift__(self, other):
        return self._determine_type_with(other)(
            int(self) << int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __rlshift__(self, other):
        return self._determine_type_with(other)(
            int(other) << int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __rshift__(self, other):
        return self._determine_type_with(other)(
            int(self) >> int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __rrshift__(self, other):
        return self._determine_type_with(other)(
            int(other) >> int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __and__(self, other):
        return self._determine_type_with(other)(
            int(self) & int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __rand__(self, other):
        return self._determine_type_with(other)(
            int(other) & int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __or__(self, other):
        return self._determine_type_with(other)(
            int(self) | int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __ror__(self, other):
        return self._determine_type_with(other)(
            int(other) | int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __xor__(self, other):
        return self._determine_type_with(other)(
            int(self) ^ int(other),
            _check_overflow=overflow.ison(_nest_level=1),
        )

    def __rxor__(self, other):
        return self._determine_type_with(other)(
            int(other) ^ int(self),
            _check_overflow=overflow.ison(_nest_level=1),
        )


class _SignedInt(_SizedInt):
    def as_signed(self):
        return self

    def as_unsigned(self):
        return self.twos()

    def twos(self):
        cls = type(self)
        ival = int(self)

        sign_bit = 1 if ival < 0 else 0

        body_mask = 2 ** cls._bit_width_ - 1

        return Unsigned[cls._bit_width_](
            ival if ival >= 0 else (abs(ival) ^ body_mask) + 1
        )


class _UnsignedInt(_SizedInt):
    def as_signed(self):
        return self.twos()

    def as_unsigned(self):
        return self

    def twos(self):
        """
        calculate the two's complement of the given value
        """
        cls = type(self)
        uval = int(self)

        lower_bits_mask = (2 ** cls._bit_width_ - 1) >> 1
        sign_bit_mask = 1 << (cls._bit_width_ - 1)

        sign_bit = uval & sign_bit_mask

        sign = -1 if sign_bit > 0 else 1

        body = uval & lower_bits_mask
        body_value = ((body ^ lower_bits_mask) + 1) if sign < 0 else body

        return Signed[cls._bit_width_](sign * body_value)


# metaclasses to genrate any width int at runtime
class Signed(type):

    # __slots__ = (
    #     "_bit_width_",
    #     "_max_value_",
    #     "_min_value_",
    #     "_clip_mod_",
    #     "_clip_offset_",
    #     "_is_signed_",
    # )

    _signed_int_types_ = {}

    def __new__(cls, width: int) -> type:
        global Signed

        if width < 1:
            raise TypeError(f"uints cannot have negative width")

        name = f"i{width}"
        if name in Signed._signed_int_types_:
            raise TypeError(
                f"{name} already exists and cannot be created twice, use Signed[{width}]"
            )
        else:
            self = super().__new__(
                cls,
                name,
                (_SignedInt,),
                {
                    "_bit_width_": width,
                    "_max_value_": int(2 ** (width - 1) - 1),
                    "_min_value_": -int(2 ** (width - 1)),
                    "_clip_mod_": int(2 ** (width)),
                    "_clip_offset_": int(2 ** (width - 1)),
                    "_is_signed_": True,
                },
            )
            Signed._signed_int_types_[name] = self
            return self

    def __class_getitem__(cls, width: int) -> type:
        name = f"i{width}"
        existing = cls._signed_int_types_
        if name not in existing:
            existing[name] = cls(width)
        return existing[name]

    def __repr__(self: type) -> str:
        return f"<class '{self.__name__}'>"
        # return f"<class '{'sized.'*self._sized_auto_gened_}{self.__name__}'>"


class Unsigned(type):

    # __slots__ = (
    #     "_bit_width_",
    #     "_max_value_",
    #     "_min_value_",
    #     "_clip_mod_",
    #     "_clip_offset_",
    #     "_is_signed_",
    # )

    _unsigned_int_types_ = {}

    def __new__(cls, width: int) -> type:
        global Unsigned

        if width < 0:
            raise TypeError(f"uints cannot have negative width")

        name = f"u{width}"
        # check that this is the first time this width is being made
        if name in Unsigned._unsigned_int_types_:
            raise TypeError(
                f"{name} already exists and cannot be created twice, use Unsigned[{width}]"
            )

        self = super().__new__(
            cls,
            name,
            (_UnsignedInt,),
            {
                "_bit_width_": width,
                "_max_value_": int(2 ** width - 1),
                "_min_value_": int(0),
                "_clip_mod_": int(2 ** (width)),
                "_clip_offset_": int(0),
                "_is_signed_": False,
            },
        )
        Unsigned._unsigned_int_types_[name] = self
        return self

    def __class_getitem__(cls, width: int) -> type:
        name = f"u{width}"
        existing = cls._unsigned_int_types_
        if name not in existing:
            existing[name] = cls(width)
        return existing[name]

    def __repr__(self: type) -> str:
        return f"<class '{self.__name__}'>"

    @staticmethod
    def pack(*nums) -> "Unsigned":
        """
        A function to take several unsigned integes and combine them into
        one larger number. For example Unsigned.pack(u3(0b101), u4(0011)) returns
        u7(0b1010011).
        """
        global Unsigned

        # format input
        # if the only input was a single iterable use that
        if len(nums) == 1 and hasattr(nums[0], "__iter__"):
            nums = iter(nums[0])

        val = 0
        width = 0
        for index, num in enumerate(nums):
            assert isinstance(num, _UnsignedInt), f"found {type(num)}"
            numcls = type(num)
            assert isinstance(numcls, Unsigned), (
                "all inputs must be unsigned integers, "
                + f"found item at index {index} was a {numcls}"
            )
            val = (val << numcls._bit_width_) + int(num)
            width += numcls._bit_width_
            # print(width, bin(Unsigned(width)(val)))
        return Unsigned[width](val)

    @staticmethod
    def unpack(source: Union[int, "Unsigned"], into: tuple) -> Tuple["Unsigned", ...]:
        """
        Takes an integer (int or Unsigned) and breaks it into smaller uints.
        For example Unsigned.unpack(u7(0b1010011), (u3, u2, u2)) would return
        (u3(0b101), u2(0b00), u2(0b11)). Both 'normal' and unsigned ints can
        be unpacked, normal ints are assumed to be infinitely 0 padded on the left.
        Additionally adding a ... to the begining of an unpack template (the
        tuple of types) will "absorb" any extra zeros to the left.
        """

        # todo: allow the ... anywhere in the unpack sequence
        #   so (u2, ..., u5) is allowed and any size

        global Unsigned
        assert len(into) != 0

        intcls = type(source)

        if isinstance(source, _UnsignedInt):
            src_width = intcls._bit_width_
            sum_width = sum(cls._bit_width_ for cls in into if cls is not ...)
            if src_width == sum_width:
                pass
            elif src_width < sum_width:
                unpack_target = tuple(cls.__name__ for cls in into)
                raise TypeError(
                    "cannot unpack mis-mathched unsigned integer widths, "
                    + f"u{src_width} -> {unpack_target} (ie {src_width} -> {sum_width}).\n"
                    + f"either balance the widths or cast the source number to a "
                    + f"plain int: `Unsigned.unpack(<{intcls.__name__}>, {unpack_target})`"
                )
            elif src_width > sum_width and ... not in into:
                unpack_target = tuple(cls.__name__ for cls in into)
                raise TypeError(
                    "cannot unpack mis-mathched unsigned integer widths, "
                    + f"u{src_width} -> {unpack_target} (ie {src_width} -> {sum_width}).\n"
                    + f"either balance the widths or add a `...` to the unpack template: "
                    + f"`Unsigned.unpack(<{intcls.__name__}>, {('...',)+unpack_target})`"
                )

        if into[0] is not ... and ... in into:
            raise NotImplementedError(
                f"`...` not yet supported at index {into.index(...)} (only 0)"
            )

        if not isinstance(source, _UnsignedInt) and ... in into:
            raise ValueError(f"... can only be used with unsigned ints, got {intcls}")

        chunks = []
        val = int(source)
        for cls in reversed(into):
            if cls is ...:
                break
            width = cls._bit_width_
            chunks.insert(0, cls(val & (2 ** width - 1)))
            val = val >> width

        return tuple(chunks)


class overflow:

    _local_flag_name = "..sized int overflow flags.."
    # this is the key used for
    # it is invisible in locals() call.

    def __init__(self, flag):
        self.flag = flag

    def _get_locals(*, nest_level: int):
        """
        nest_level is the next level fo the call site,
        0 is the scope of the call site, 1 would be one scope outside of that
        """
        frame = sys._getframe(1 + nest_level)
        return frame.f_locals

    def __enter__(self, *args, **kwargs):
        global sys, overflow
        lcls = overflow._get_locals(nest_level=1)
        if overflow._local_flag_name not in lcls:
            lcls[overflow._local_flag_name] = []
        lcls[overflow._local_flag_name].append(self.flag)

    def __exit__(self, *args, **kwargs) -> None:
        global sys, overflow
        lcls = overflow._get_locals(nest_level=1)
        lcls[overflow._local_flag_name].pop(-1)

    def ison(*_, _nest_level: int = 0) -> bool:
        global overflow
        lcls = overflow._get_locals(nest_level=1 + _nest_level)
        if overflow._local_flag_name in lcls:
            flags = lcls[overflow._local_flag_name]
            return flags[-1] if len(flags) else False
        else:
            return False

    def isoff(*_, _nest_level: int = 0) -> bool:
        # uses *_ so there isn't any extra call nesting from static/classmethod
        global overflow
        return not overflow.ison(_nest_level=1 + _nest_level)


@singleton
class sized:
    # used an an autop generator for int types on import
    # (is added to sys.modules below)

    __path__ = None

    @property
    def __all__(self):
        global Signed, Unsigned
        return [*Signed._signed_int_types_, *Unsigned._unsigned_int_types_]

    def __getattr__(self, name):
        global Signed, Unsigned

        if name in Signed._signed_int_types_:
            return Signed._signed_int_types_[name]
        elif name in Unsigned._unsigned_int_types_:
            return Unsigned._unsigned_int_types_[name]
        else:
            prefix, body = name[0], name[1:]
            # find singedness
            if prefix == "i":
                kind = Signed
            elif prefix == "u":
                kind = Unsigned
            else:
                raise NameError(
                    f"sized ints' names must start with 'i' or 'u', found '{prefix}' in '{name}'"
                )

            # find width
            if body.isnumeric() and "." not in body:
                width = int(body)
            else:
                raise NameError(
                    f"sized ints must have whole number widths, found '{body}'  in '{name}'"
                )

            cls = kind(width)
            return cls


class tri(_SizedInt):
    _bit_width_ = None
    _max_value_ = 1
    _min_value_ = -1

    _clip_mod_ = 3
    _clip_offset_ = 1


class utri(_SizedInt):
    _bit_width_ = None
    _max_value_ = 2
    _min_value_ = 0

    _clip_mod_ = 3
    _clip_offset_ = 0


# setup the eviroment and baked in types for importing

for width in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
    ucls = Unsigned(width)
    __all__.append(ucls.__name__)
    locals()[ucls.__name__] = ucls

    icls = Signed(width)
    __all__.append(icls.__name__)
    locals()[icls.__name__] = icls

u0 = Unsigned[0]
__all__.append("u0")

sys.modules["sized"] = sized
