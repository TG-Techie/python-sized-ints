from sized_ints import *

start = overflow.ison()
with overflow(False):
    assert overflow.isoff() # fisrt inside

    with overflow(True): # a
        assert overflow.ison() # a inside
    assert overflow.isoff() # a after (match fisrt inside, ie False)


    with overflow(True): # b
        assert overflow.ison()

        with overflow(False): # c
            assert overflow.isoff() # c inside

            with overflow(True): # d
                assert overflow.ison() # d inside

            assert overflow.isoff() # d after (match c)

        assert overflow.ison() # c after (match b)

    assert overflow.isoff() # b after (match after a)

end = overflow.ison()
assert start == end, f"{start} == {end}"
