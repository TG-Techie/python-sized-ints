from sized_ints import *

width_4_tests = (
    (0b0000, 0),
    (0b0001, 1),
    (0b0010, 2),
    (0b0011, 3),
    (0b0100, 4),
    (0b0101, 5),
    (0b0110, 6),
    (0b0111, 7),
    (0b1000, -8),
    (0b1001, -7),
    (0b1010, -6),
    (0b1011, -5),
    (0b1100, -4),
    (0b1101, -3),
    (0b1110, -2),
    (0b1111, -1),
)

for unsigned, signed in width_4_tests:
    assert (
        u4(unsigned).twos() == signed
    ), f"{unsigned=}, {signed=}, {u4(unsigned).twos()=}"

for unsigned, signed in width_4_tests:
    assert (
        unsigned == i4(signed).twos()
    ), f"{unsigned=}, {signed=}, {i4(signed).twos()=}"
