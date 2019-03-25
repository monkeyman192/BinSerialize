from BinSerialize import BinSerialize, dtype
import struct

d = dtype(endianess='<')


# define a cutom variable type
class half_tuple(dtype):
    def __init__(self):
        dtype.__init__(self)

    def _deserialize(self, fobj):
        self.value = struct.unpack('<hh', fobj.read(0x4))[::-1]

    def _serialize(self, fobj, pointer_data):
        fobj.write(struct.pack('<hh', *self.value[::-1]))


d.register('half_tuple', half_tuple)


# create some classes with the required structure


class test(BinSerialize):
    def __init__(self):
        BinSerialize.__init__(self)

        self._m = d.array(d.int32, 2)


class test2(BinSerialize):
    def __init__(self):
        BinSerialize.__init__(self)

        self._x = d.half_tuple
        self._y = d.pointer(test, d.int32)
        self._a = d.list(d.float32)


class test3(BinSerialize):
    def __init__(self):
        BinSerialize.__init__(self)

        self._x = d.int32
        self._y = d.uint32
        self._z = d.int32


def test_io():
    m = test()
    m.deserialize('file.bin')
    assert m.x == (2, 1)
    # change the value
    m.x = (3, 4)
    assert len(m.a) == 2
    # add another value
    m.a.append(0.25)

    m.serialize('file2.bin')
    # check the new values are serialized correctly
    with open('file2.bin', 'rb') as f:
        assert f.read(4) == b'\x04\x00\x03\x00'
        assert f.read(4) == b'\x18\x00\x00\x00'
        assert f.read(4) == b'\x03\x00\x00\x00'
