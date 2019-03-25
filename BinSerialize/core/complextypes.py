import struct

from .dtype import dtype
from .stdtypes import _uint32
from .Pointer import Pointer
from .utils import instance_dtype


class _filesize(dtype):
    def __init__(self, value_dtype=_uint32):
        dtype.__init__(self)
        self.value_dtype = instance_dtype(value_dtype)

    def _deserialize(self, fobj):
        self.value = self.value_dtype.deserialize(fobj)

    def _serialize(self, fobj, pointer_data):
        pointer_data.append((fobj.tell(), self))
        # write an empty header for now
        fobj.write(struct.pack(self.offset_dtype.fmt, 0))


class _array(dtype):
    def __init__(self, array_dtype, length):
        dtype.__init__(self)
        self.array_dtype = instance_dtype(array_dtype)
        self.length = length

    def _deserialize(self, fobj):
        self.value = []
        for _ in range(self.length):
            self.array_dtype.deserialize(fobj)
            self.value.append(self.array_dtype.value)

    def _serialize(self, fobj, pointer_data):
        for val in self.value:
            fobj.write(struct.pack(self.array_dtype.fmt, val))


class _array_2d(dtype):
    def __init__(self, array_dtype, rows, columns):
        dtype.__init__(self)
        self.array_dtype = instance_dtype(array_dtype)
        self.rows = rows
        self.columns = columns

    def _deserialize(self, fobj):
        self.value = []
        for i in range(self.rows):
            self.value.append(list())
            for _ in range(self.columns):
                self.array_dtype.deserialize(fobj)
                self.value[i].append(self.array_dtype.value)

    def _serialize(self, fobj, pointer_data):
        for val in self.value:
            fobj.write(struct.pack(self.array_dtype.fmt, val))


class _list(dtype):
    def __init__(self, list_dtype, list_count_dtype=_uint32):
        dtype.__init__(self)
        self.list_dtype = instance_dtype(list_dtype)
        self.list_count_dtype = instance_dtype(list_count_dtype)

    def _deserialize(self, fobj):
        count = struct.unpack(self.endianess + 'I', fobj.read(0x4))[0]
        self.value = []
        for _ in range(count):
            self.list_dtype.deserialize(fobj)
            self.value.append(self.list_dtype.value)

    def _serialize(self, fobj, pointer_data):
        fobj.write(struct.pack(self.endianess + 'I', len(self.value)))
        for val in self.value:
            fobj.write(struct.pack(self.list_dtype.fmt, val))


class _pointer(dtype):
    pointer_positions = dict()

    def __init__(self, data_dtype, offset_dtype=_uint32, offset_mode='abs'):
        dtype.__init__(self)
        self.offset_dtype = instance_dtype(offset_dtype)
        self.data_dtype = instance_dtype(data_dtype)
        self.offset_mode = offset_mode

    def _deserialize(self, fobj):
        with Pointer(fobj, self.offset_dtype, self.offset_mode):
            self.data_dtype.deserialize(fobj)
            if hasattr(self.data_dtype, 'value'):
                self.value = self.data_dtype.value
            else:
                self.value = self.data_dtype

    def _serialize(self, fobj, pointer_data):
        pointer_data.append((fobj.tell(), self))
        # write an empty header for now
        fobj.write(struct.pack(self.offset_dtype.fmt, 0))


dtype.registered_funcs.update({'filesize': _filesize,
                               'array': _array,
                               'list': _list,
                               'pointer': _pointer})
