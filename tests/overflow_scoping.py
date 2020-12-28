from sized_ints import *

def func():
    assert overflow.isoff()

with overflow(True):
    assert overflow.ison()
    func()
    assert overflow.ison()
